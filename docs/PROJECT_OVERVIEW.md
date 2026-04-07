# Project Overview

## Project Name
**pic-talk** - AI-Powered English Speaking Practice Platform

## Purpose
An interactive English learning application that uses AI-generated images and speech recognition to help users practice English speaking skills through visual prompts.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI Services**: 
  - Qwen (Alibaba Cloud) - Text generation and semantic planning
  - Qwen Image Max - AI image generation
  - DashScope - ASR (Automatic Speech Recognition)
- **Storage**: Alibaba Cloud OSS (Object Storage Service)
- **Database**: SQLite (local file-based)
- **Key Libraries**:
  - `uvicorn` - ASGI server
  - `pydantic` - Data validation
  - `httpx` - HTTP client
  - `sounddevice` & `scipy` - Audio processing

### Frontend
- **Framework**: Next.js 16.1.4 (React 19.2.3)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **Build Tool**: Next.js built-in tooling

## Architecture

### High-Level Flow
1. **Task Generation**: AI generates semantic plans and corresponding images
2. **User Practice**: Users view images and speak English descriptions
3. **Speech Recognition**: Audio is captured and transcribed using ASR
4. **Evaluation**: AI evaluates user responses against standard answers
5. **Feedback**: Users receive scores and improvement suggestions

### Key Components

#### Backend Services
- **Image Task Service**: Generates and manages practice tasks
- **Practice Service**: Handles user practice sessions
- **Evaluation Service**: Scores and provides feedback
- **Speech Service**: Manages audio recording and ASR
- **OSS Client**: Handles cloud storage operations

#### API Endpoints
- `/api/image/*` - Image task generation and retrieval
- `/api/user-practice/*` - Practice session management

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 20+
- Alibaba Cloud account with DashScope API access

### Environment Variables
Required in `backend/.env`:
- DashScope API credentials
- OSS configuration
- Other service credentials (see `.env.example`)

### Quick Start

**Backend**:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

## Project Structure
```
pic-talk/
├── backend/          # FastAPI backend
│   ├── api/         # API controllers/routes
│   ├── db/          # Database models and operations
│   ├── models/      # AI client integrations
│   ├── schemas/     # Pydantic schemas
│   └── services/    # Business logic
└── frontend/        # Next.js frontend
    └── app/         # Next.js app directory
```

## Key Features
- AI-generated image-based English practice tasks
- Real-time speech recognition
- Automated evaluation and feedback
- Difficulty level adaptation
- Practice history tracking
