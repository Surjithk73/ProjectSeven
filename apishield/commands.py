"""Bounded argv execution with process-tree ownership and capped logs."""
import ctypes
import os
import re
import signal
import subprocess
import threading
import time

from .configuration import SECRET_NAME


def sanitized_environment(config) -> dict[str, str]:
    allowed = {"PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP", "LANG", "LC_ALL"}
    environment = {name: value for name, value in os.environ.items() if name.upper() in allowed}
    environment.update(config.environment)
    # Neither Python search paths nor controller credentials are inherited.
    environment["PYTHONUNBUFFERED"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def redact(text: str) -> str:
    for name, value in os.environ.items():
        if SECRET_NAME.search(name) and value and len(value) >= 4:
            text = text.replace(value, "[REDACTED]")
    text = re.sub(r"(?i)(\b(?:api[_-]?key|access[_-]?key|private[_-]?key|secret|token|password|passwd|credential|authorization)\b[\"']?\s*[:=]\s*[\"']?)([^\s,\"'{}]+)", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)\bBearer\s+[^\s,\"'{}]+", "Bearer [REDACTED]", text)
    text = re.sub(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", "[REDACTED PRIVATE KEY]", text, flags=re.S)
    return text


def redact_data(value):
    """Redact string leaves without damaging JSON escaping or numeric evidence."""
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, dict):
        return {key: "[REDACTED]" if SECRET_NAME.search(str(key)) else redact_data(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact_data(item) for item in value]
    return value


class _WindowsTree:
    """A Windows Job Object owns descendants, including after the parent exits."""
    def __init__(self):
        from ctypes import wintypes
        class BasicLimits(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong),
                ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]
        class Counters(ctypes.Structure):
            _fields_ = [(name, ctypes.c_ulonglong) for name in ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount", "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]
        class ExtendedLimits(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", BasicLimits), ("IoInfo", Counters),
                ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]
        class Accounting(ctypes.Structure):
            _fields_ = [(name, ctypes.c_longlong) for name in ("TotalUserTime", "TotalKernelTime", "ThisPeriodTotalUserTime", "ThisPeriodTotalKernelTime")] + [(name, wintypes.DWORD) for name in ("TotalPageFaultCount", "TotalProcesses", "ActiveProcesses", "TotalTerminatedProcesses")]
        self.accounting_type = Accounting
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.kernel.CreateJobObjectW.restype = wintypes.HANDLE
        self.kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        self.kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self.kernel.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p]
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.handle = self.kernel.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = ExtendedLimits()
        limits.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            self.kernel.CloseHandle(self.handle)
            raise ctypes.WinError(ctypes.get_last_error())

    def attach_and_resume(self, process):
        if not self.kernel.AssignProcessToJobObject(self.handle, int(process._handle)):
            raise ctypes.WinError(ctypes.get_last_error())
        ntdll = ctypes.WinDLL("ntdll")
        ntdll.NtResumeProcess.argtypes = [ctypes.c_void_p]
        ntdll.NtResumeProcess.restype = ctypes.c_long
        if ntdll.NtResumeProcess(int(process._handle)) != 0:
            raise OSError("could not resume owned repository process")

    def stop(self):
        if self.handle:
            if not self.kernel.TerminateJobObject(self.handle, 1):
                raise ctypes.WinError(ctypes.get_last_error())
            deadline = time.monotonic() + 5
            while True:
                accounting = self.accounting_type()
                if not self.kernel.QueryInformationJobObject(self.handle, 1, ctypes.byref(accounting), ctypes.sizeof(accounting), None):
                    raise ctypes.WinError(ctypes.get_last_error())
                if accounting.ActiveProcesses == 0:
                    break
                if time.monotonic() >= deadline:
                    raise RuntimeError("repository descendants did not terminate")
                time.sleep(0.01)
            self.kernel.CloseHandle(self.handle)
            self.handle = None


def _stop(process, tree):
    if tree is not None:
        tree.stop()
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if process.poll() is None:
        process.kill()
    process.wait(timeout=5)


def run_command(argv: list[str], job, label: str) -> dict:
    if not isinstance(argv, list) or not argv or any(not isinstance(value, str) or "\x00" in value for value in argv) or not argv[0].strip():
        raise ValueError("command must be a nonempty argv array")
    job.check()
    start = time.monotonic()
    deadline = start + min(job.config.budgets.command_timeout_seconds, job.remaining())
    limit = job.config.budgets.output_limit_bytes
    chunks = {"stdout": bytearray(), "stderr": bytearray()}
    capture_lock = threading.Lock()
    captured = 0
    output_limited = False
    timed_out = cancelled = False
    process = None
    tree = None
    readers = []

    def consume(stream, name):
        nonlocal captured, output_limited
        try:
            while True:
                data = stream.read(4096)
                if not data:
                    break
                with capture_lock:
                    available = max(0, limit - captured)
                    chunks[name].extend(data[:available])
                    captured += min(available, len(data))
                    output_limited |= len(data) > available
        finally:
            stream.close()

    job.event("command_started", label=label, argv=argv)
    try:
        if os.name == "nt":
            tree = _WindowsTree()
        process = subprocess.Popen(argv, cwd=job.workspace, env=sanitized_environment(job.config),
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=False, start_new_session=os.name != "nt",
            creationflags=(0x4 | subprocess.CREATE_NEW_PROCESS_GROUP) if os.name == "nt" else 0)
        if tree is not None:
            tree.attach_and_resume(process)
        for name, stream in (("stdout", process.stdout), ("stderr", process.stderr)):
            thread = threading.Thread(target=consume, args=(stream, name), daemon=True)
            thread.start()
            readers.append(thread)
        while process.poll() is None:
            if job.cancelled():
                cancelled = True
                break
            if time.monotonic() >= deadline:
                timed_out = True
                break
            time.sleep(0.02)
        cancelled |= job.cancelled()
        exit_code = process.poll()
        # Stop owned descendants even when the parent exited successfully.
        _stop(process, tree)
        if exit_code is None:
            exit_code = process.returncode
        for reader in readers:
            reader.join(timeout=5)
        if any(reader.is_alive() for reader in readers):
            raise RuntimeError("repository output readers did not terminate")
    except OSError as exc:
        exit_code = None
        chunks["stderr"] = bytearray(str(exc).encode()[:limit])
    finally:
        if process is not None and (process.poll() is None or (tree is not None and tree.handle)):
            _stop(process, tree)
        elif tree is not None and tree.handle:
            tree.stop()
    stdout = redact(chunks["stdout"].decode("utf-8", errors="replace")).replace("\r\n", "\n")
    stderr = redact(chunks["stderr"].decode("utf-8", errors="replace")).replace("\r\n", "\n")
    # Redaction and UTF-8 replacement can expand data; cap the persisted form as well.
    output_limited |= len((stdout + stderr).encode("utf-8")) > limit
    stdout_bytes = stdout.encode("utf-8")[:limit]
    stdout = stdout_bytes.decode("utf-8", errors="ignore")
    stderr = stderr.encode("utf-8")[:max(0, limit - len(stdout.encode("utf-8")))].decode("utf-8", errors="ignore")
    result = {"exit_code": exit_code, "stdout": stdout, "stderr": stderr,
        "duration_seconds": time.monotonic() - start, "timed_out": timed_out,
        "cancelled": cancelled, "output_limited": output_limited}
    job.event("command_finished", label=label, **result)
    return result
