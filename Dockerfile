FROM node:22-alpine AS web-assets
WORKDIR /assets
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts --no-audit --no-fund

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /service
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY web ./web
COPY --from=web-assets /assets/node_modules/ag-grid-community/dist/ag-grid-community.min.js ./node_modules/ag-grid-community/dist/
COPY --from=web-assets /assets/node_modules/ag-grid-community/LICENSE.txt ./node_modules/ag-grid-community/
RUN useradd --create-home assembly && chown -R assembly:assembly /service
USER assembly
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
