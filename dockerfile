# STAGE 1: construcción
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# STAGE 2: imagen final
FROM python:3.12-slim

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY src/ ./src/

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

ENV DATABASE_URL="postgresql://user:password@db:5432/tiendauv_db"

CMD ["uvicorn", "src.carrito.api:app", "--host", "0.0.0.0", "--port", "8000"]