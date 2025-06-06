from libs.db.db import ASYNC_DATABASE_URL as SQLALCHEMY_DATABASE_URL  # Backward compatibility
from libs.db.db import (
    SYNC_DATABASE_URL,
    Base,
    get_async_db,
    get_async_db_context,
    get_db,
    get_db_context,
    get_sync_db,
    get_db_session_sync,
    get_sync_db_context,
)

from libs.db.mongodb import (
    get_async_mongodb,
    get_async_mongodb_context,
    get_sync_mongodb,
    get_sync_mongodb_context,
    get_mongodb,
    get_mongodb_context,
    get_collection,
)

__all__ = [
    # Primary new interface - SQL
    "get_db",
    "get_db_context",
    "get_async_db",
    "get_async_db_context",
    "get_sync_db",
    "get_sync_db_context",
    # MongoDB interface
    "get_mongodb",
    "get_mongodb_context",
    "get_async_mongodb",
    "get_async_mongodb_context",
    "get_sync_mongodb",
    "get_sync_mongodb_context",
    "get_collection",
    # Backward compatibility
    "get_db_session",
    "get_db_sync",
    "get_db_session_sync",
    # Other exports
    "Base",
    "SQLALCHEMY_DATABASE_URL",
    "SYNC_DATABASE_URL",
]
