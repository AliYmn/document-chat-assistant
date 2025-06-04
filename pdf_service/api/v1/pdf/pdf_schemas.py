from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PDFUploadMetadata(BaseModel):
    """Metadata for uploaded PDF files"""

    title: str = Field(..., description="Title of the PDF document")
    description: Optional[str] = Field(None, description="Description of the PDF document")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags associated with the document")
    filename: str = Field(..., description="Original filename of the PDF")
    content_type: str = Field("application/pdf", description="Content type of the file")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sample Document",
                "description": "A sample PDF document",
                "tags": ["sample", "document", "pdf"],
                "filename": "sample.pdf",
                "content_type": "application/pdf",
            }
        }


class PDFMetadataResponse(BaseModel):
    """Response model for PDF metadata"""

    id: str = Field(..., description="MongoDB document ID")
    title: str = Field(..., description="Title of the PDF document")
    description: Optional[str] = Field(None, description="Description of the PDF document")
    tags: List[str] = Field(default_factory=list, description="Tags associated with the document")
    filename: str = Field(..., description="Original filename of the PDF")
    user_id: int = Field(..., description="ID of the user who uploaded the document")
    file_size: int = Field(..., description="Size of the file in bytes")
    upload_date: datetime = Field(..., description="Upload timestamp")
    content_type: str = Field(..., description="Content type of the file")


class ChatRequest(BaseModel):
    """Request model for chat with PDF"""

    message: str = Field(..., description="User message to send to the AI")

    class Config:
        json_schema_extra = {"example": {"message": "What is this document about?"}}


class ChatResponse(BaseModel):
    """Response model for chat with PDF"""

    message: str = Field(..., description="User's original message")
    response: str = Field(..., description="AI response to the user's message")
    pdf_title: str = Field(..., description="Title of the PDF document being discussed")


class ChatMessageResponse(BaseModel):
    """Model for a single chat message in history"""

    id: str = Field(..., description="Message ID")
    message: str = Field(..., description="Message content")
    is_user: bool = Field(..., description="Whether the message is from the user (True) or AI (False)")
    timestamp: str = Field(..., description="Message timestamp in ISO format")


class ChatHistoryResponse(BaseModel):
    """Response model for chat history"""

    history: List[Dict[str, Any]] = Field(..., description="List of chat messages")
