"""
MongoDB connection module for document-chat-assistant.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.database import Database
from motor.motor_asyncio import AsyncIOMotorDatabase
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator, Any

from libs import settings


# MongoDB connection clients
async_client = AsyncIOMotorClient(settings.MONGO_URI)
sync_client = MongoClient(settings.MONGO_URI)


# Async MongoDB functions
async def get_async_mongodb() -> AsyncIOMotorDatabase:
    """
    Asynchronous dependency for FastAPI to get a MongoDB database.

    Returns:
        AsyncIOMotorDatabase: An asynchronous MongoDB database
    """
    return async_client[settings.MONGO_DB]


@asynccontextmanager
async def get_async_mongodb_context() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    Asynchronous context manager for MongoDB database.

    Yields:
        AsyncIOMotorDatabase: An asynchronous MongoDB database
    """
    db = async_client[settings.MONGO_DB]
    try:
        yield db
    finally:
        # No explicit close needed for Motor client
        pass


# Sync MongoDB functions
def get_sync_mongodb() -> Database:
    """
    Synchronous dependency for FastAPI to get a MongoDB database.
    Used primarily in Celery tasks.

    Returns:
        Database: A synchronous MongoDB database
    """
    return sync_client[settings.MONGO_DB]


@contextmanager
def get_sync_mongodb_context() -> Generator[Database, Any, None]:
    """
    Synchronous context manager for MongoDB database.
    Used primarily in Celery tasks.

    Yields:
        Database: A synchronous MongoDB database
    """
    db = sync_client[settings.MONGO_DB]
    try:
        yield db
    finally:
        # No explicit close needed for PyMongo client
        pass


# Unified interface
def get_mongodb(async_mode: bool = True):
    """
    Unified function to get a MongoDB database based on the mode.

    Args:
        async_mode: Whether to use async or sync mode

    Returns:
        Either an async or sync MongoDB database
    """
    if async_mode:
        return get_async_mongodb()
    return get_sync_mongodb()


def get_mongodb_context(async_mode: bool = True):
    """
    Unified context manager for MongoDB database based on the mode.

    Args:
        async_mode: Whether to use async or sync mode

    Returns:
        Either an async or sync context manager
    """
    if async_mode:
        return get_async_mongodb_context()
    return get_sync_mongodb_context()


# Helper function to get a specific collection
def get_collection(collection_name: str, async_mode: bool = True):
    """
    Get a specific MongoDB collection.

    Args:
        collection_name: Name of the collection
        async_mode: Whether to use async or sync mode

    Returns:
        Either an async or sync MongoDB collection
    """
    if async_mode:
        return get_async_mongodb()[collection_name]
    return get_sync_mongodb()[collection_name]
