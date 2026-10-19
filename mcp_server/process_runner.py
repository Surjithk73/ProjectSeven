"""Run a bounded repair process and terminate its descendants before recovery."""
import os
import signal
import subprocess


class ProcessCleanupError(RuntimeError):
    """The repair process may still own files; do not restore or start another job."""


def run_agent_process(command, *, env, cwd, timeout=300):
    options = {'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE, 'env': env, 'cwd': cwd}
    if os.name != 'nt':
        options['start_new_session'] = True
    process = subprocess.Popen(command, **options)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            if os.name == 'nt':
                killed = subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                                        capture_output=True, timeout=15)
                if killed.returncode != 0 and process.poll() is None:
                    raise ProcessCleanupError('Could not terminate repair process tree; recovery requires attention')
            else:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            process.communicate(timeout=15)
        except Exception as error:
            raise ProcessCleanupError('Repair process cleanup failed; stop its processes before restarting the dashboard') from error
        raise
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
