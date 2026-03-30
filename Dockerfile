# syntax=docker/dockerfile:1

FROM node:20-bookworm-slim AS web-build
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend ./
RUN npm run build


FROM node:20-bookworm-slim

WORKDIR /app

ENV NODE_ENV=production \
    CARTOPHARMA_DATA_DIR=/data \
    CARTOPHARMA_MODE=docker \
    INTERNAL_API_URL=http://127.0.0.1:8000

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    tini \
  && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY backend/requirements.txt ./backend-requirements.txt
RUN pip install --no-cache-dir -r ./backend-requirements.txt

COPY backend ./backend
COPY --from=web-build /app/frontend /app/frontend
COPY run_linux.sh /app/run_linux.sh

RUN sed -i 's/\r$//' /app/run_linux.sh \
  && chmod +x /app/run_linux.sh \
  && mkdir -p /data

EXPOSE 3000

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/run_linux.sh", "--docker"]
