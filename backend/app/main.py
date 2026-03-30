from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api import api_router
from app.core.config import APP_NAME, APP_VERSION, ensure_runtime_dirs, get_cors_origins, get_logs_dir
from app.db.database import init_database
from app.models.schemas import ApiStatusResponse, HealthResponse


def configure_logging() -> logging.Logger:
    ensure_runtime_dirs()
    logger = logging.getLogger("cartopharma")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.handlers.clear()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = get_logs_dir() / f"backend_{timestamp}.log"
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] [request_id=%(request_id)s] %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    stream_handler = logging.StreamHandler()

    class DefaultRequestIdFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if not hasattr(record, "request_id"):
                record.request_id = "-"
            return True

    default_filter = DefaultRequestIdFilter()
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    file_handler.addFilter(default_filter)
    stream_handler.addFilter(default_filter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.info("backend_start", extra={"request_id": "-"})
    return logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.logger = configure_logging()
    init_database()
    yield


app = FastAPI(
    title=APP_NAME,
    description="Base technique CartoPharma (France uniquement)",
    version=APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    logger: logging.Logger = request.app.state.logger
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "request_failed",
            extra={"request_id": request_id, "method": request.method, "path": request.url.path, "duration_ms": round(duration_ms, 2)},
        )
        response = JSONResponse(status_code=500, content={"detail": "Internal Server Error", "request_id": request_id})

    duration_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": getattr(response, "status_code", None),
            "duration_ms": round(duration_ms, 2),
        },
    )
    return response


app.include_router(api_router)


@app.get("/", response_model=ApiStatusResponse)
async def root() -> ApiStatusResponse:
    return ApiStatusResponse(
        message=APP_NAME,
        version=APP_VERSION,
        status="operational",
    )


@app.get("/health", response_model=HealthResponse, include_in_schema=False)
async def root_health() -> HealthResponse:
    from app.core.config import get_database_path

    return HealthResponse(status="healthy", scope="foundation", database=str(get_database_path()))
