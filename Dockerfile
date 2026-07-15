# Alma Mater financial portal — Cloud Run image.
# Self-contained live app (its own auth + Shopify/QBO); no vendored kit yet.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Non-root; owns /app because the app writes custom_*.json to ./data at runtime.
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080
CMD ["sh", "-c", "exec streamlit run app_client.py --server.port=${PORT:-8080} --server.address=0.0.0.0"]
