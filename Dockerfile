# Official oasdiff v1.11.7, pinned to its verified registry digest.
# Upstream installs the static Linux executable in /usr/bin/oasdiff.
FROM tufin/oasdiff:v1.11.7@sha256:d6f1e645251cc1da527311955347d8ce8bd2b7ed09bcce07176b2577b8daf19c AS oasdiff
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app OASDIFF_BIN=/usr/local/bin/oasdiff
WORKDIR /app
COPY --from=oasdiff /usr/bin/oasdiff /usr/local/bin/oasdiff
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "dashboard_api:app", "--host", "0.0.0.0", "--port", "8002"]
