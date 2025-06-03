from sqlalchemy.ext.asyncio import AsyncSession
from pdf_service.api.v1.pdf.pdf_schemas import PDFDocumentBase


class PDFService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_or_update_pdf_document(self, user_id: int, pdf_document: PDFDocumentBase):
        pass
