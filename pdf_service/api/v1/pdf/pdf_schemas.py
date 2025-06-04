from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class PDFUploadMetadata(BaseModel):
    """Metadata for uploaded PDF files"""

    title: str = Field(..., description="Title of the PDF document")
    description: Optional[str] = Field(None, description="Description of the PDF document")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags associated with the document")
    filename: str = Field(..., description="Original filename of the PDF")
    content_type: str = Field("application/pdf", description="Content type of the file")

    class Config:
        schema_extra = {
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
