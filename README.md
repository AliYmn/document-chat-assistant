# 📄 Document Chat Assistant

A secure and modular FastAPI backend application that allows authenticated users to upload PDF documents, extract their content, and chat with the contents using a Gemini-based LLM integration.

## 🚀 Features

- 🔐 JWT-based authentication with token refresh and password reset
- 📄 PDF upload, parsing, selection, and management
- 🤖 Gemini LLM integration for intelligent document chat
- 🗃️ PostgreSQL for structured data (users, chat history)
- 📦 MongoDB + GridFS for efficient PDF file storage and metadata
- 📈 Structured logging and comprehensive error handling
- 🔒 Rate limiting for enhanced security
- 🐳 Fully Dockerized microservices architecture

## 🛠 Tech Stack

- **Backend Framework:** FastAPI
- **Authentication:** JWT
- **Databases:**
  - PostgreSQL (users, chat history)
  - MongoDB with GridFS (PDF storage)
  - Redis (rate limiting, caching)
- **Message Queue:** RabbitMQ
- **LLM:** Gemini Pro via Google AI Studio (OpenAI SDK-compatible)
- **Containerization:** Docker & Docker Compose
- **PDF Parsing:** PyPDF2
- **Monitoring:** Sentry integration

## 📋 System Architecture

The application follows a microservices architecture with two main services:

1. **Auth Service**: Handles user registration, authentication, and token management
2. **PDF Service**: Manages PDF uploads, storage, parsing, and chat functionality

Both services share common libraries for database access, authentication, and error handling.

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/document-chat-assistant.git
   cd document-chat-assistant
   ```

2. Create an environment file:
   ```bash
   cp .env.example .env
   ```

3. Update the `.env` file with your configuration values, especially:
   - Database credentials
   - JWT secret keys
   - Gemini API key

### Running with Docker

Start all services using Docker Compose:

```bash
docker-compose up -d
```

This will start the following services:
- Auth Service (API)
- PDF Service (API)
- PostgreSQL database
- MongoDB database
- Redis cache
- RabbitMQ message broker
- PGAdmin (PostgreSQL management)
- Mongo Express (MongoDB management)

## 🔌 API Usage

### Authentication

#### Register a new user

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword"}'
```

#### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### PDF Management

#### Upload a PDF

```bash
curl -X POST http://localhost:8001/api/v1/pdf-upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "title=My Document" \
  -F "description=Document description" \
  -F "tags=important,work"
```

#### List PDFs

```bash
curl -X GET http://localhost:8001/api/v1/pdf-list?skip=0&limit=10 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Parse PDF

```bash
curl -X POST http://localhost:8001/api/v1/pdf-parse/DOCUMENT_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Select PDF for Chat

```bash
curl -X POST http://localhost:8001/api/v1/pdf-select/DOCUMENT_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Chat with PDF

```bash
curl -X POST http://localhost:8001/api/v1/pdf-chat \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the main topic of this document?"}'
```

#### Get Chat History

```bash
curl -X GET http://localhost:8001/api/v1/chat-history?limit=50 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## ⚙️ Environment Variables

The application uses the following environment variables:

### General Settings
```
ENV_NAME=development
PROJECT_NAME="{project_name} Service"
API_STR=/api/v1
LOG_LEVEL=INFO
```

### Security Settings
```
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Database Settings
```
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=document_chat

# MongoDB
MONGO_USER=mongo
MONGO_PASSWORD=mongo
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_DB=document_chat
MONGO_URL=mongodb://${MONGO_USER}:${MONGO_PASSWORD}@${MONGO_HOST}:${MONGO_PORT}
```

### Service Settings
```
# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis

# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672

# Gemini API
GEMINI_API_KEY=your-gemini-api-key
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models
GEMINI_MODEL=gemini-pro
```

## 🧪 Testing

Run tests using the Makefile command:

```bash
make test
```

For specific test files:

```bash
make test-file FILE=tests/unit/pdf_service/core/services/test_ai_service.py
```

## 🔍 Postman Collection

A comprehensive Postman collection is included in the repository to help you test and interact with the API endpoints.

### How to Use the Postman Collection

1. Import the `postman_collection.json` file into Postman
2. Create an environment with the following variables:
   - `auth_url`: URL for the Auth Service (e.g., `http://localhost:8000`)
   - `pdf_url`: URL for the PDF Service (e.g., `http://localhost:8001`)
   - `user_email`: Your test user email
   - `user_password`: Your test user password

### Available Requests

#### Auth Service
- Register User
- Login (automatically sets access_token and refresh_token in your environment)
- Get Current User
- Refresh Token
- Request Password Reset
- Reset Password

#### PDF Service
- Upload PDF
- List PDFs
- Get PDF Metadata
- Parse PDF
- Select PDF for Chat
- Chat with PDF
- Get Chat History

The collection includes pre-configured request bodies and authentication headers, making it easy to test the API functionality.

## 🔍 Known Issues and Limitations

1. The Gemini API has rate limits that may affect chat functionality during heavy usage.
2. Large PDF files (>50MB) may cause performance issues during parsing.
3. The chat functionality works best with text-based PDFs; scanned documents with images may have limited extraction quality.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
