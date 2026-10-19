ARG PYTHON_BASE
FROM ${PYTHON_BASE}
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /work
COPY benchmarks/runners/candidate_worker.py /opt/apishield/candidate_worker.py
COPY benchmarks/runners/oracle_worker.py /opt/apishield/oracle_worker.py
USER 65534:65534
CMD ["python", "-I", "-B", "/opt/apishield/candidate_worker.py"]
