from contextlib import asynccontextmanager
from typing import AsyncGenerator

import anyio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from libs import ExceptionBase, settings
from libs.logger import configure_logging, get_logger, LoggingMiddleware
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from auth_service.api.v1.auth.auth_router import auth_router
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
import time


# Configure structured logging
configure_logging("auth_service", log_level="INFO")
logger = get_logger("auth_service.main")

# Initialize Sentry if enabled and in production environment
if settings.SENTRY_ENABLED and settings.ENV_NAME == "PRODUCTION":
    logger.info("Initializing Sentry integration")
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
    )


# App Lifespan
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting auth service")

    # Thread limiter setting
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 100
    logger.debug("Thread limiter configured", total_tokens=limiter.total_tokens)

    # Initialize rate limiter with Redis connection
    redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
    logger.info("Connecting to Redis", host=settings.REDIS_HOST, port=settings.REDIS_PORT)

    try:
        redis_instance = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_instance)
        logger.info("Rate limiter initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize rate limiter", error=str(e))
        raise

    logger.info("Auth service started successfully")
    yield

    # Close Redis connection on shutdown
    logger.info("Shutting down auth service")
    await redis_instance.close()
    logger.info("Redis connection closed")


# APP Configuration
app = FastAPI(
    title=settings.PROJECT_NAME.format(project_name="Auth"),
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_STR}/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    lifespan=lifespan,
)

# Middleware settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["GET", "POST", "PATCH"],
    allow_credentials=False,
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)


# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(ExceptionBase)
async def http_exception_handler(_request, exc: ExceptionBase) -> ORJSONResponse:
    logger.error(
        "Exception occurred",
        status_code=exc.status_code,
        error_code=exc.code,
        message=exc.message,
    )
    return ORJSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    logger.exception("Unhandled exception", path=request.url.path, method=request.method, error=str(exc))
    return ORJSONResponse(status_code=500, content={"detail": "Internal server error", "error_code": "internal_error"})


app.include_router(auth_router, prefix=settings.API_STR)
