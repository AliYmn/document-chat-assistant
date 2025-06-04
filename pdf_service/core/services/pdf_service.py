import io
from datetime import datetime
from typing import List, Dict, Any

from bson import ObjectId
import PyPDF2
from fastapi import UploadFile, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from sqlalchemy.ext.asyncio import AsyncSession

from libs.db.mongodb import get_async_mongodb
from pdf_service.api.v1.pdf.pdf_schemas import PDFUploadMetadata, PDFMetadataResponse


class PDFService:
    """Service for managing PDF documents with MongoDB GridFS"""

    def __init__(self, db: AsyncSession, mongodb=None):
        """Initialize the PDF service

        Args:
            db: SQL database session
            mongodb: MongoDB database connection
        """
        self.db = db
        self.mongodb = mongodb

    async def upload_pdf_to_gridfs(
        self, file: UploadFile, metadata: PDFUploadMetadata, user_id: int
    ) -> PDFMetadataResponse:
        """
        Upload a PDF file to MongoDB using GridFS with metadata stored in a separate collection.

        Args:
            file: The uploaded PDF file
            metadata: Metadata for the PDF file
            user_id: ID of the user uploading the file

        Returns:
            Metadata of the uploaded PDF file
        """
        # Use MongoDB database connection from constructor or get a new one if not provided
        # Get MongoDB connection (can't use 'or' operator with MongoDB objects)
        mongodb = self.mongodb if self.mongodb is not None else await get_async_mongodb()

        # Create GridFS bucket
        fs = AsyncIOMotorGridFSBucket(mongodb)

        # Read file content
        content = await file.read()
        file_size = len(content)

        # Prepare file metadata
        file_metadata = {
            "filename": metadata.filename,
            "contentType": metadata.content_type,
            "metadata": {
                "title": metadata.title,
                "description": metadata.description,
                "tags": metadata.tags or [],
                "user_id": user_id,
                "upload_date": datetime.now(),
            },
        }

        # Upload file to GridFS
        file_id = await fs.upload_from_stream(metadata.filename, io.BytesIO(content), metadata=file_metadata)

        # Store metadata in a separate collection for efficient querying
        pdf_metadata = {
            "grid_fs_id": file_id,
            "title": metadata.title,
            "description": metadata.description,
            "tags": metadata.tags or [],
            "filename": metadata.filename,
            "user_id": user_id,
            "file_size": file_size,
            "upload_date": datetime.now(),
            "content_type": metadata.content_type,
        }

        # Insert metadata into the pdf_metadata collection
        metadata_collection = mongodb["pdf_metadata"]
        result = await metadata_collection.insert_one(pdf_metadata)

        # Get the inserted metadata document
        inserted_metadata = await metadata_collection.find_one({"_id": result.inserted_id})

        # Convert ObjectId to string for response
        inserted_metadata["id"] = str(inserted_metadata.pop("_id"))

        return PDFMetadataResponse(**inserted_metadata)

    async def get_pdf_metadata(self, document_id: str, user_id: int) -> PDFMetadataResponse:
        """
        Get metadata for a specific PDF document

        Args:
            document_id: ID of the PDF document
            user_id: ID of the user requesting the document

        Returns:
            Metadata of the PDF document
        """
        # Get MongoDB connection (can't use 'or' operator with MongoDB objects)
        mongodb = self.mongodb if self.mongodb is not None else await get_async_mongodb()
        metadata_collection = mongodb["pdf_metadata"]

        try:
            # Convert string ID to ObjectId
            obj_id = ObjectId(document_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format")

        # Find document with matching ID and user_id
        document = await metadata_collection.find_one({"_id": obj_id, "user_id": user_id})

        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        # Convert ObjectId to string for response
        document["id"] = str(document.pop("_id"))

        return PDFMetadataResponse(**document)

    async def list_user_pdfs(self, user_id: int, skip: int = 0, limit: int = 10) -> List[PDFMetadataResponse]:
        """
        List all PDF documents for a specific user with pagination

        Args:
            user_id: ID of the user
            skip: Number of documents to skip
            limit: Maximum number of documents to return

        Returns:
            List of PDF document metadata
        """
        # Get MongoDB connection (can't use 'or' operator with MongoDB objects)
        mongodb = self.mongodb if self.mongodb is not None else await get_async_mongodb()
        metadata_collection = mongodb["pdf_metadata"]

        # Find all documents for the user with pagination
        cursor = metadata_collection.find({"user_id": user_id})
        cursor.sort("upload_date", -1)  # Sort by upload date, newest first
        cursor.skip(skip).limit(limit)

        documents = []
        async for doc in cursor:
            # Convert ObjectId to string for response
            doc["id"] = str(doc.pop("_id"))
            documents.append(PDFMetadataResponse(**doc))

        return documents

    async def delete_pdf(self, document_id: str, user_id: int) -> Dict[str, Any]:
        """
        Delete a PDF document and its metadata

        Args:
            document_id: ID of the PDF document to delete
            user_id: ID of the user requesting deletion

        Returns:
            Dictionary with deletion status
        """
        # Get MongoDB connection (can't use 'or' operator with MongoDB objects)
        mongodb = self.mongodb if self.mongodb is not None else await get_async_mongodb()
        metadata_collection = mongodb["pdf_metadata"]

        try:
            # Convert string ID to ObjectId
            obj_id = ObjectId(document_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format")

        # Find document with matching ID and user_id
        document = await metadata_collection.find_one({"_id": obj_id, "user_id": user_id})

        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        # Get GridFS bucket
        fs = AsyncIOMotorGridFSBucket(mongodb)

        # Delete file from GridFS
        await fs.delete(document["grid_fs_id"])

        # Delete metadata
        await metadata_collection.delete_one({"_id": obj_id})

        return {"status": "success", "message": "Document deleted successfully"}

    async def parse_pdf_text(self, document_id: str, user_id: int) -> Dict[str, Any]:
        """
        Extract text content from a PDF document

        Args:
            document_id: ID of the PDF document
            user_id: ID of the user requesting parsing

        Returns:
            Dictionary with text content and metadata
        """
        # Get MongoDB connection (can't use 'or' operator with MongoDB objects)
        mongodb = self.mongodb if self.mongodb is not None else await get_async_mongodb()
        metadata_collection = mongodb["pdf_metadata"]

        try:
            # Convert string ID to ObjectId
            obj_id = ObjectId(document_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format")

        # Find document with matching ID and user_id
        document = await metadata_collection.find_one({"_id": obj_id, "user_id": user_id})

        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        # Get GridFS bucket
        fs = AsyncIOMotorGridFSBucket(mongodb)

        # Download file from GridFS
        grid_out = await fs.open_download_stream(document["grid_fs_id"])
        content = await grid_out.read()

        # Parse PDF content using PyPDF2
        pdf_content = ""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            num_pages = len(pdf_reader.pages)

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                pdf_content += page.extract_text() + "\n"

            # Update metadata with page count if not already set
            if "page_count" not in document or not document["page_count"]:
                await metadata_collection.update_one({"_id": obj_id}, {"$set": {"page_count": num_pages}})

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error parsing PDF: {str(e)}"
            )

        return {"document_id": document_id, "title": document["title"], "page_count": num_pages, "content": pdf_content}

    async def select_pdf_for_chat(self, document_id: str, user_id: int) -> Dict[str, Any]:
        """
        Select a PDF for chat by setting it as the active document

        Args:
            document_id: ID of the PDF document
            user_id: ID of the user

        Returns:
            Dictionary with selection status
        """
        # First verify the document exists and belongs to the user
        document = await self.get_pdf_metadata(document_id, user_id)

        # Store the selection in a user preferences collection
        # Get MongoDB connection (can't use 'or' operator with MongoDB objects)
        mongodb = self.mongodb if self.mongodb is not None else await get_async_mongodb()
        user_prefs = mongodb["user_preferences"]

        # Update or insert user preference for active PDF
        await user_prefs.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "active_pdf_id": document_id,
                    "active_pdf_title": document.title,
                    "last_updated": datetime.now(),
                }
            },
            upsert=True,
        )

        return {"status": "success", "message": f"PDF '{document.title}' selected for chat", "document_id": document_id}

    async def get_selected_pdf(self, user_id: int) -> Dict[str, Any]:
        """
        Get the currently selected PDF for a user

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with selected PDF details or None if no PDF is selected
        """
        # Get MongoDB connection (can't use 'or' operator with MongoDB objects)
        mongodb = self.mongodb if self.mongodb is not None else await get_async_mongodb()
        user_prefs = mongodb["user_preferences"]

        # Get user preference for active PDF
        user_pref = await user_prefs.find_one({"user_id": user_id})
        if not user_pref or "active_pdf_id" not in user_pref:
            return None

        # Get PDF metadata
        try:
            document = await self.get_pdf_metadata(user_pref["active_pdf_id"], user_id)
            return {"document_id": user_pref["active_pdf_id"], "title": document.title}
        except HTTPException:
            # If the PDF no longer exists, clear the selection
            await user_prefs.update_one({"user_id": user_id}, {"$unset": {"active_pdf_id": "", "active_pdf_title": ""}})
            return None

    async def get_pdf_text(self, document_id: str, user_id: int) -> str:
        """
        Get the text content of a PDF document

        Args:
            document_id: ID of the PDF document
            user_id: ID of the user

        Returns:
            Text content of the PDF or empty string if not parsed
        """
        # Get MongoDB connection (can't use 'or' operator with MongoDB objects)
        mongodb = self.mongodb if self.mongodb is not None else await get_async_mongodb()
        pdf_texts = mongodb["pdf_texts"]

        # Check if the PDF has been parsed
        text_doc = await pdf_texts.find_one({"document_id": document_id, "user_id": user_id})
        if not text_doc or "content" not in text_doc:
            # If not parsed, try to parse it now
            try:
                parse_result = await self.parse_pdf_text(document_id, user_id)
                return parse_result.get("content", "")
            except HTTPException:
                return ""

        return text_doc["content"]
