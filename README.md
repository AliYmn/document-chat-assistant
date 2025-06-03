# 📄 Document Chat Assistant

A secure and modular FastAPI backend application that allows authenticated users to upload PDF documents, extract their content, and chat with the contents using a Gemini-based LLM integration.

## 🚀 Features

- 🔐 JWT-based authentication
- 📄 PDF upload, parsing, and selection
- 🤖 Gemini LLM integration for chat
- 🗃️ PostgreSQL for structured data (users, chat history)
- 📦 MongoDB + GridFS for storing PDF files and metadata
- 📈 Structured logging and error handling
- 🐳 Fully Dockerized

## 🛠 Tech Stack

- **Backend Framework:** FastAPI
- **Authentication:** JWT
- **Database:** PostgreSQL + MongoDB (GridFS)
- **LLM:** Gemini Pro via Google AI Studio (OpenAI SDK-compatible)
- **Containerization:** Docker
- **PDF Parsing:** PyPDF2
