from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # API Settings
    DEBUG: bool
    API_STR: str = "/api/v1"
    PROJECT_NAME: str = "{project_name} Service API"
    PROJECT_VERSION: str = "v1"

    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int

    # POSTGRES
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PORT: int

    # MONGODB
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_DB: str
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_URI: str

    # RabbitMQ
    RABBITMQ_PASS: str
    RABBITMQ_USER: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int

    # Gemini AI API
    GEMINI_API_KEY: str
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # REDIS
    REDIS_PORT: int
    REDIS_HOST: str
    REDIS_PASSWORD: str
    REDIS_TTL: int
    REDIS_PREFIX: str
    FERNET_KEY: str

    # Celery Worker
    AUTH_QUEUE_NAME: str
    AUTH_WORKER_NAME: str
    PDF_QUEUE_NAME: str
    PDF_WORKER_NAME: str

    # Email Settings
    MAIL_HOST: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str

    # Gemini
    GEMINI_API_KEY: str
    GEMINI_BASE_URL: str

    # Sentry
    SENTRY_DSN: str
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_ENABLED: bool = False
    ENV_NAME: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Config()
