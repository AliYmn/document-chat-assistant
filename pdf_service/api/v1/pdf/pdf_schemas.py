from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# PDF Document schemas
class PDFDocumentBase(BaseModel):
    """Base model for PDF Document data"""

    title: str = Field(..., description="Title of the PDF document")
    description: Optional[str] = Field(None, description="Description of the PDF document")
    tags: Optional[List[str]] = Field(None, description="Tags associated with the document")
    language: Optional[str] = Field("en", description="Language of the document")
    page_count: Optional[int] = Field(None, description="Number of pages in the document")
    file_size: Optional[int] = Field(None, description="Size of the file in bytes")


class PDFDocumentResponse(PDFDocumentBase):
    """Response model for PDF Document data"""

    id: int
    user_id: int
    file_path: str
    created_date: datetime
    updated_date: Optional[datetime] = None

    class Config:
        from_attributes = True
