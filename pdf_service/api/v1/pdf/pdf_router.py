from fastapi import APIRouter, Depends, status, Header
from typing import Annotated
from fastapi_limiter.depends import RateLimiter

from pdf_service.api.v1.pdf.pdf_schemas import (
    PDFDocumentBase,
)
from pdf_service.core.services.pdf_service import PDFService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db
from libs.service.auth import AuthService

router = APIRouter(tags=["Fasting"], prefix="/fasting")


def get_pdf_service(db: AsyncSession = Depends(get_async_db)) -> PDFService:
    return PDFService(db)


def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


# FastingPlan endpoints
@router.post(
    "/plan",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=15, seconds=60))],
)
async def create_or_update_fasting_plan(
    plan_data: PDFDocumentBase,
    authorization: Annotated[str | None, Header()] = None,
    pdf_service: PDFService = Depends(get_pdf_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await pdf_service.create_or_update_pdf_document(user.id, plan_data)
