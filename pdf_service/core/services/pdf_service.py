import io
from datetime import datetime
from typing import List, Dict, Any

from bson import ObjectId
import PyPDF2
from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from sqlalchemy.ext.asyncio import AsyncSession

from libs.db.mongodb import get_async_mongodb
from libs.logger import get_logger
from pdf_service.api.v1.pdf.pdf_schemas import PDFUploadMetadata, PDFMetadataResponse
from libs.exceptions.schemas import ExceptionBase
from libs.exceptions.errors import ErrorCode


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
        self.logger = get_logger("pdf_service.service")

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
        self.logger.info(
            "Uploading PDF to GridFS",
            filename=metadata.filename,
            user_id=user_id,
            file_size=file.size if hasattr(file, "size") else "unknown",
        )

        # Use MongoDB database connection from constructor or get a new one if not provided
        # Get MongoDB connection (can't use 'or' operator with MongoDB objects)
        mongodb = self.mongodb if self.mongodb is not None else await get_async_mongodb()

        # Create GridFS bucket
        fs = AsyncIOMotorGridFSBucket(mongodb)

        # Read file content
        content = await file.read()
        file_size = len(content)
        self.logger.debug("Read file content", actual_file_size=file_size)

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

        try:
            # Upload file to GridFS
            grid_id = await fs.upload_from_stream(
                filename=metadata.filename,
                source=io.BytesIO(content),
                metadata=file_metadata,
            )
            self.logger.debug("File uploaded to GridFS", grid_id=str(grid_id))

            # Create metadata document in the PDF metadata collection
            pdf_metadata = {
                "grid_fs_id": grid_id,
                "filename": metadata.filename,
                "title": metadata.title,
                "description": metadata.description,
                "user_id": user_id,
                "file_size": file_size,
                "upload_date": datetime.utcnow(),
                "parsed": False,
                "text_content": None,
                "content_type": metadata.content_type,
            }
        except Exception as e:
            self.logger.error("Failed to upload file to GridFS", error=str(e))
            raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR)

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
        Get PDF metadata by document ID

        Args:
            document_id: ID of the PDF document
            user_id: ID of the user requesting the metadata

        Returns:
            Metadata of the PDF document

        Raises:
            ExceptionBase: If the document is not found or doesn't belong to the user
        """
        self.logger.info("Getting PDF metadata", document_id=document_id, user_id=user_id)

        # Get MongoDB connection
        mongodb = self.mongodb if self.mongodb is not None else await get_async_mongodb()

        try:
            # Convert string ID to ObjectId
            obj_id = ObjectId(document_id)
        except Exception:
            raise ExceptionBase(ErrorCode.BAD_REQUEST)

        # Find document with matching ID and user_id
        metadata_collection = mongodb["pdf_metadata"]
        document = await metadata_collection.find_one({"_id": obj_id, "user_id": user_id})

        # Check if document exists
        if not document:
            self.logger.warning("PDF document not found", document_id=document_id)
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Check if document belongs to the user
        if document["user_id"] != user_id:
            self.logger.warning(
                "Unauthorized access attempt to PDF document",
                document_id=document_id,
                requested_by_user_id=user_id,
                owner_user_id=document["user_id"],
            )
            raise ExceptionBase(ErrorCode.FORBIDDEN)

        # Convert ObjectId to string for response
        document["id"] = str(document.pop("_id"))

        # Ensure required fields exist
        if "content_type" not in document:
            document["content_type"] = "application/pdf"
        if "filename" not in document:
            document["filename"] = f"{document['title']}.pdf"

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
        self.logger.info("Listing user PDFs", user_id=user_id, skip=skip, limit=limit)

        # Get MongoDB connection
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

            # Ensure required fields exist
            if "content_type" not in doc:
                doc["content_type"] = "application/pdf"
            if "filename" not in doc:
                doc["filename"] = f"{doc['title']}.pdf"

            documents.append(PDFMetadataResponse(**doc))

        return documents

    async def delete_pdf(self, document_id: str, user_id: int) -> bool:
        """
        Delete a PDF document and its metadata

        Args:
            document_id: ID of the PDF document to delete
            user_id: ID of the user requesting the deletion

        Returns:
            True if the document was deleted successfully

        Raises:
            ExceptionBase: If the document is not found or doesn't belong to the user
        """
        self.logger.info("Deleting PDF document", document_id=document_id, user_id=user_id)

        # Get MongoDB connection
        mongodb = self.mongodb if self.mongodb is not None else await get_async_mongodb()

        try:
            # Convert string ID to ObjectId
            obj_id = ObjectId(document_id)
        except Exception:
            raise ExceptionBase(ErrorCode.BAD_REQUEST)

        # Find document with matching ID and user_id
        metadata_collection = mongodb["pdf_metadata"]
        document = await metadata_collection.find_one({"_id": obj_id, "user_id": user_id})

        if not document:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Create GridFS bucket
        fs = AsyncIOMotorGridFSBucket(mongodb)

        try:
            # Delete file from GridFS
            await fs.delete(document["grid_fs_id"])
            self.logger.debug("File deleted from GridFS", grid_id=str(document["grid_fs_id"]))

            # Delete metadata from MongoDB collection
            result = await metadata_collection.delete_one({"_id": ObjectId(document_id)})

            if result.deleted_count > 0:
                self.logger.info("PDF document deleted successfully", document_id=document_id)
                return True
            else:
                self.logger.warning("Failed to delete PDF metadata", document_id=document_id)
                return False

        except Exception as e:
            self.logger.error("Error deleting PDF document", document_id=document_id, error=str(e))
            raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR)

    async def parse_pdf_text(self, document_id: str, user_id: int) -> bool:
        """
        Parse text content from a PDF document and store it in the metadata

        Args:
            document_id: ID of the PDF document to parse
            user_id: ID of the user requesting the parsing

        Returns:
            True if the document was parsed successfully

        Raises:
            ExceptionBase: If the document is not found or doesn't belong to the user
        """
        self.logger.info("Parsing PDF text", document_id=document_id, user_id=user_id)

        # Get MongoDB connection
        mongodb = self.mongodb if self.mongodb is not None else await get_async_mongodb()
        metadata_collection = mongodb["pdf_metadata"]

        try:
            # Convert string ID to ObjectId
            obj_id = ObjectId(document_id)
        except Exception:
            raise ExceptionBase(ErrorCode.BAD_REQUEST)

        # Find document with matching ID and user_id
        document = await metadata_collection.find_one({"_id": obj_id, "user_id": user_id})

        if not document:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

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
                try:
                    page_text = page.extract_text()
                    if page_text:
                        pdf_content += page_text + "\n"
                    else:
                        self.logger.warning(f"Empty text extracted from page {page_num + 1}")
                except Exception as e:
                    self.logger.error(f"Error extracting text from page {page_num + 1}: {str(e)}")
                    # Continue with next page instead of failing completely

            # Update metadata with page count if not already set
            if "page_count" not in document or not document["page_count"]:
                await metadata_collection.update_one({"_id": obj_id}, {"$set": {"page_count": num_pages}})

            # Save the extracted text to the pdf_texts collection
            pdf_texts = mongodb["pdf_texts"]
            await pdf_texts.update_one(
                {"document_id": document_id, "user_id": user_id},
                {"$set": {"content": pdf_content, "parsed_date": datetime.utcnow()}},
                upsert=True,
            )

        except Exception as e:
            self.logger.error(f"Error parsing PDF: {str(e)}")
            raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR)

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
        except ExceptionBase:
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
            except Exception:
                return ""

        return text_doc["content"]
