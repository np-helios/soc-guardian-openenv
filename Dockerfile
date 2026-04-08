FROM node:20-bullseye-slim AS frontend-builder

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
      "fastapi>=0.115.0,<1.0.0" \
      "httpx>=0.27.0,<1.0.0" \
      "openai>=2.7.2,<3.0.0" \
      "pydantic>=2.8.0,<3.0.0" \
      "pyyaml>=6.0.0,<7.0.0" \
      "uvicorn>=0.30.0,<1.0.0"

EXPOSE 7860

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
