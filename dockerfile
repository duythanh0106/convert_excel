FROM python:3.11-slim as builder
WORKDIR /app

COPY requirements.txt .
RUN pip install \
 --no-cache-dir \
 --user \
 --default-timeout=100 \
 --retries 10 \
 -r requirements.txt


FROM python:3.11-slim
WORKDIR /app

RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/uploads /app/outputs /app/templates && \
    chown -R appuser:appuser /app

COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser main.py excel_processor.py auth_oidc.py ./
COPY --chown=appuser:appuser templates/ ./templates/

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
