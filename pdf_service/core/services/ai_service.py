from datetime import datetime
from typing import Dict, List, Any

import aiohttp
from fastapi import HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

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
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.0-flash"

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
                        error_text = await response.text()
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error from Gemini API: {error_text}",
                        )

                    response_data = await response.json()
                    ai_response = (
                        response_data.get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "")
                    )

                    if not ai_response:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to get a valid response from Gemini API",
                        )

            # Save user message to database
            user_chat_message = ChatMessage(user_id=user_id, message=message, is_user=True, timestamp=datetime.now())
            self.db.add(user_chat_message)

            # Save AI response to database
            ai_chat_message = ChatMessage(user_id=user_id, message=ai_response, is_user=False, timestamp=datetime.now())
            self.db.add(ai_chat_message)

            await self.db.commit()

            return {"message": message, "response": ai_response, "pdf_title": pdf_title}

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing chat request: {str(e)}"
            )

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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving chat history: {str(e)}"
            )
