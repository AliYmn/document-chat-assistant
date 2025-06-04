from fastapi import APIRouter, Depends, status, File, UploadFile, Form, HTTPException, Header
from typing import List
from fastapi_limiter.depends import RateLimiter
from typing import Annotated

from pdf_service.api.v1.pdf.pdf_schemas import PDFUploadMetadata, PDFMetadataResponse
from pdf_service.core.services.pdf_service import PDFService
from libs.service.auth import AuthService
from libs.db import get_async_db
from libs.db.mongodb import get_async_mongodb
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    tags=["pdf"],
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)


async def get_pdf_service(db: AsyncSession = Depends(get_async_db)) -> PDFService:
    mongodb = await get_async_mongodb()
    return PDFService(db=db, mongodb=mongodb)


def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


@router.post("/pdf-upload", response_model=PDFMetadataResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(None),
    tags: str = Form(None),
    authorization: Annotated[str | None, Header()] = None,
    pdf_service: PDFService = Depends(get_pdf_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Upload a PDF file to MongoDB using GridFS
    """
    # Extract user_id from auth_service
    user = await auth_service.get_user_from_token(authorization)

    # Validate file content type
    if not file.content_type or "pdf" not in file.content_type.lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed")

    # Parse tags if provided
    tag_list = tags.split(",") if tags else []

    # Create metadata object
    metadata = PDFUploadMetadata(
        filename=file.filename, title=title, description=description, tags=tag_list, content_type=file.content_type
    )

    # Upload PDF to GridFS
    return await pdf_service.upload_pdf_to_gridfs(file, metadata, user.id)


@router.get("/pdf-list", response_model=List[PDFMetadataResponse])
async def list_pdfs(
    skip: int = 0,
    limit: int = 10,
    authorization: Annotated[str | None, Header()] = None,
    pdf_service: PDFService = Depends(get_pdf_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    List all PDF files for the current user with pagination
    """
    user = await auth_service.get_user_from_token(authorization)
    return await pdf_service.list_user_pdfs(user.id, skip, limit)


@router.get("/pdf/{document_id}", response_model=PDFMetadataResponse)
async def get_pdf_metadata(
    document_id: str,
    pdf_service: PDFService = Depends(get_pdf_service),
    authorization: Annotated[str | None, Header()] = None,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get metadata for a specific PDF document
    """
    user = await auth_service.get_user_from_token(authorization)
    return await pdf_service.get_pdf_metadata(document_id, user.id)


@router.delete("/pdf/{document_id}", status_code=status.HTTP_200_OK)
async def delete_pdf(
    document_id: str,
    authorization: Annotated[str | None, Header()] = None,
    pdf_service: PDFService = Depends(get_pdf_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Delete a PDF document and its metadata
    """
    user = await auth_service.get_user_from_token(authorization)
    return await pdf_service.delete_pdf(document_id, user.id)


@router.post("/pdf-parse", status_code=status.HTTP_200_OK)
async def parse_pdf(
    document_id: str,
    authorization: Annotated[str | None, Header()] = None,
    pdf_service: PDFService = Depends(get_pdf_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Extract text content from a PDF document
    """
    user = await auth_service.get_user_from_token(authorization)
    return await pdf_service.parse_pdf_text(document_id, user.id)


@router.post("/pdf-select", status_code=status.HTTP_200_OK)
async def select_pdf(
    document_id: str,
    authorization: Annotated[str | None, Header()] = None,
    pdf_service: PDFService = Depends(get_pdf_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Select a PDF for chat by setting it as the active document
    """
    user = await auth_service.get_user_from_token(authorization)
    return await pdf_service.select_pdf_for_chat(document_id, user.id)
