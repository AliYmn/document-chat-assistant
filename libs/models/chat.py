from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from libs.models.base import Base


class ChatMessage(Base):
    """Chat message model for storing user and AI messages"""

    __tablename__ = "chat_messages"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_user = Column(Boolean, default=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, user_id={self.user_id}, is_user={self.is_user})>"
