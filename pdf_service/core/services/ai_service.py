from datetime import datetime
from typing import Dict, Any, List

import aiohttp
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from libs.exceptions.schemas import ExceptionBase
from libs.exceptions.errors import ErrorCode
from libs.logger import get_logger
from libs.settings import settings
from libs.models.chat import ChatMessage


class AIService:
    """Service for interacting with Gemini API and managing chat history"""

    def __init__(self, db: AsyncSession):
        """Initialize the AI service

        Args:
            db: SQL database session
        """
        self.db = db
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = settings.GEMINI_API_URL
        self.model = settings.GEMINI_MODEL
        self.logger = get_logger("ai_service")

    async def chat_with_pdf(self, user_id: int, message: str, pdf_content: str, pdf_title: str) -> Dict[str, Any]:
        """Send a message to Gemini API with PDF context and get a response

        Args:
            user_id: ID of the user sending the message
            message: User's message
            pdf_content: Content of the PDF document
            pdf_title: Title of the PDF document

        Returns:
            Dictionary with AI response and message details
        """
        try:
            # Create system prompt with PDF context
            system_prompt = f"""You are an AI assistant helping with questions about a PDF document titled '{pdf_title}'.
            Use the following PDF content to answer the user's questions accurately.
            If the answer cannot be found in the PDF content, politely say so and suggest what might help.

            PDF CONTENT:
            {pdf_content}
            """

            # Prepare request payload for Gemini API
            payload = {
                "contents": [
                    {"parts": [{"text": system_prompt}], "role": "model"},
                    {"parts": [{"text": message}], "role": "user"},
                ]
            }

            # Make API request to Gemini
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers={"Content-Type": "application/json"}) as response:
                    if response.status != 200:
                        self.logger.error("Error from Gemini API", status=response.status)
                        await response.text()  # Consume response body
                        raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR)

                    response_data = await response.json()
                    ai_response = (
                        response_data.get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "")
                    )

                    if not ai_response:
                        raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR)

            # Save user message to database
            user_chat_message = ChatMessage(user_id=user_id, message=message, is_user=True, timestamp=datetime.now())
            self.db.add(user_chat_message)

            # Save AI response to database
            ai_chat_message = ChatMessage(user_id=user_id, message=ai_response, is_user=False, timestamp=datetime.now())
            self.db.add(ai_chat_message)

            await self.db.commit()

            return {"message": message, "response": ai_response, "pdf_title": pdf_title}

        except aiohttp.ClientError as e:
            self.logger.error(f"Gemini API connection error: {str(e)}")
            raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR, message="Failed to connect to AI service")
        except ExceptionBase:
            # Re-raise existing ExceptionBase exceptions
            raise
        except Exception as e:
            self.logger.error(f"Error in chat_with_pdf: {str(e)}")
            raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR)

    async def get_chat_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for a user

        Args:
            user_id: ID of the user
            limit: Maximum number of messages to return

        Returns:
            List of chat messages
        """
        try:
            # Query chat messages for the user, ordered by timestamp
            result = await self.db.execute(
                select(ChatMessage)
                .where(ChatMessage.user_id == user_id)
                .order_by(desc(ChatMessage.timestamp))
                .limit(limit)
            )

            messages = result.scalars().all()

            # Convert to list of dictionaries
            history = [
                {
                    "id": str(msg.id),
                    "message": msg.message,
                    "is_user": msg.is_user,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in messages
            ]

            return history

        except Exception as e:
            self.logger.error(f"Error retrieving chat history: {str(e)}")
            raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR, message="Failed to retrieve chat history")
