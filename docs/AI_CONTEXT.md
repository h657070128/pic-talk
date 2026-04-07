# AI Context & Prompts

## Project Context for AI Assistants

This document provides context for AI coding assistants working on the pic-talk project.

---

## Project Summary

**pic-talk** is an AI-powered English speaking practice application that:
- Generates image-based practice tasks using AI
- Records user speech responses
- Transcribes speech using ASR (Automatic Speech Recognition)
- Evaluates responses and provides feedback
- Tracks practice history

**Tech Stack**:
- Backend: FastAPI (Python) + SQLite
- Frontend: Next.js 16 + React 19 + TypeScript + TailwindCSS
- AI Services: Alibaba Cloud DashScope (Qwen models, ASR)
- Storage: Alibaba Cloud OSS

---

## Key Design Decisions

### Architecture Choices

1. **Layered Architecture**: Separation of concerns with API, Service, Repository, and Model layers
   - **Why**: Maintainability, testability, and clear responsibility boundaries

2. **SQLite for Development**: File-based database
   - **Why**: Simple setup, no external dependencies for development
   - **Future**: Migrate to PostgreSQL for production

3. **OSS for Media Storage**: Cloud object storage for images and audio
   - **Why**: Scalability, reliability, and CDN capabilities

4. **FastAPI**: Modern Python web framework
   - **Why**: Automatic API documentation, type validation, async support

5. **Next.js App Router**: Latest Next.js architecture
   - **Why**: Server components, improved performance, modern React patterns

### AI Integration Strategy

1. **Qwen for Text Generation**: Semantic plans and standard answers
   - **Why**: Strong Chinese-English bilingual capabilities, cost-effective

2. **Qwen Image Max for Image Generation**: Visual task creation
   - **Why**: Integrated with DashScope, consistent API

3. **DashScope ASR**: Speech-to-text conversion
   - **Why**: Unified platform, good accuracy for English learning context

---

## Common Development Tasks

### Task 1: Add New API Endpoint

**Context**: API endpoints follow REST conventions and use FastAPI routers.

**Pattern**:
1. Define Pydantic schema in `schemas/`
2. Implement service logic in `services/`
3. Create controller in `api/`
4. Register router in `main.py`

**Example Location**: See `api/image_controller.py` for reference

### Task 2: Modify Database Schema

**Context**: Using SQLAlchemy ORM with declarative base.

**Pattern**:
1. Update model in `db/`
2. Create/update repository in `services/*_repository.py`
3. Re-initialize database (development) or create migration (production)

**Example Location**: See `db/image_practice_task.py` for reference

### Task 3: Integrate New AI Service

**Context**: AI services are wrapped in client classes in `models/`.

**Pattern**:
1. Create client class in `models/`
2. Add API credentials to `.env`
3. Use client in service layer

**Example Location**: See `models/qwen_client.py` for reference

### Task 4: Add Frontend Component

**Context**: Using Next.js 16 App Router with TypeScript and TailwindCSS.

**Pattern**:
1. Create component in `app/` or `components/`
2. Use TypeScript interfaces for props
3. Style with TailwindCSS utility classes

**Example Location**: See `app/page.tsx` for reference

---

## Code Patterns & Conventions

### Backend Patterns

#### Service Pattern
```python
class SomeService:
    def __init__(self):
        self.dependency = Dependency()
    
    def business_method(self, param: str) -> dict:
        # Business logic here
        result = self.dependency.do_something(param)
        return {"result": result}
```

#### Repository Pattern
```python
class SomeRepository:
    def get_by_id(self, id: int):
        db = next(get_db())
        return db.query(Model).filter(Model.id == id).first()
    
    def save(self, data: dict):
        db = next(get_db())
        record = Model(**data)
        db.add(record)
        db.commit()
        return record
```

#### Controller Pattern
```python
from fastapi import APIRouter, HTTPException
from schemas.some_schema import SomeRequest
from services.some_service import SomeService

router = APIRouter()

@router.post("/endpoint")
def endpoint(request: SomeRequest):
    service = SomeService()
    try:
        result = service.business_method(request.param)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Frontend Patterns

#### Component Pattern
```typescript
'use client'

import { useState, useEffect } from 'react'

interface ComponentProps {
  prop1: string
  prop2: number
}

export default function Component({ prop1, prop2 }: ComponentProps) {
  const [state, setState] = useState<string>('')
  
  useEffect(() => {
    // Side effects
  }, [])
  
  return (
    <div className="container">
      {/* JSX */}
    </div>
  )
}
```

#### API Call Pattern
```typescript
async function fetchData() {
  try {
    const response = await fetch('http://localhost:8000/api/endpoint')
    if (!response.ok) throw new Error('Failed to fetch')
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error:', error)
    throw error
  }
}
```

---

## Important Files & Their Purposes

### Backend Critical Files

- `main.py` - Application entry, router registration, CORS config
- `db/database.py` - Database connection and session management
- `db/init_db.py` - Database schema initialization
- `services/image_task_service.py` - Core task generation logic
- `models/qwen_client.py` - AI text generation wrapper
- `models/asr_client.py` - Speech recognition wrapper
- `services/oss_client.py` - Cloud storage operations

### Frontend Critical Files

- `app/layout.tsx` - Root layout, global providers
- `app/page.tsx` - Home page component
- `app/globals.css` - Global styles and TailwindCSS
- `next.config.ts` - Next.js configuration

### Configuration Files

- `backend/.env` - Environment variables (not committed)
- `backend/requirements.txt` - Python dependencies
- `frontend/package.json` - Node dependencies
- `frontend/tsconfig.json` - TypeScript configuration

---

## Environment Variables Reference

### Required Backend Variables
```env
# DashScope (Qwen & ASR)
DASHSCOPE_API_KEY=sk-xxx

# OSS Storage
OSS_ACCESS_KEY_ID=xxx
OSS_ACCESS_KEY_SECRET=xxx
OSS_BUCKET_NAME=pic-talk-bucket
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com

# Database
DATABASE_URL=sqlite:///./pic_talk.db

# Application
ENVIRONMENT=development
DEBUG=true
```

### Optional Frontend Variables
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Testing Strategy

### Backend Testing
- **Unit Tests**: Test individual services and utilities
- **Integration Tests**: Test API endpoints with TestClient
- **Location**: `backend/tests/` (to be created)

### Frontend Testing
- **Component Tests**: Test React components
- **Integration Tests**: Test user flows
- **Location**: `frontend/__tests__/` (to be created)

---

## Known Limitations & TODOs

### Current Limitations
1. No user authentication/authorization
2. SQLite not suitable for production scale
3. No rate limiting on API endpoints
4. No caching layer
5. Audio processing is synchronous (could be async)
6. No comprehensive error tracking (e.g., Sentry)

### Planned Improvements
1. Add user authentication with JWT
2. Migrate to PostgreSQL
3. Implement Redis caching
4. Add rate limiting middleware
5. Implement async audio processing
6. Add comprehensive logging and monitoring
7. Add automated tests
8. Implement CI/CD pipeline

---

## AI Service Integration Details

### Qwen Client Methods

**generate_semantic_plan(difficulty_level: str) -> str**
- Generates a description plan for image generation
- Input: "beginner", "intermediate", or "advanced"
- Output: Detailed scene description

**generate_standard_answer(semantic_plan: str) -> str**
- Creates expected English response for a scene
- Input: Semantic plan from above
- Output: Natural English description

### ASR Client Methods

**transcribe(audio_file_path: str) -> str**
- Converts speech to text
- Input: Path to WAV audio file
- Output: Transcribed text

### OSS Client Methods

**upload_image_from_url(url: str) -> str**
- Downloads image from URL and uploads to OSS
- Input: Temporary image URL
- Output: Permanent OSS URL

**upload_file(file_path: str, object_name: str) -> str**
- Uploads local file to OSS
- Input: Local file path and desired object name
- Output: OSS URL

---

## Debugging Tips

### Backend Debugging
1. Check FastAPI auto-docs at `/docs` for API testing
2. Enable DEBUG logging in `.env`
3. Use `print()` or `logging.debug()` for quick debugging
4. Check DashScope console for API usage and errors
5. Verify OSS bucket permissions if upload fails

### Frontend Debugging
1. Use React DevTools browser extension
2. Check Network tab for API call failures
3. Console.log for state debugging
4. Verify CORS settings if API calls fail

### Common Issues
- **CORS errors**: Check `allow_origins` in `main.py`
- **API key errors**: Verify `.env` file exists and has correct keys
- **Database errors**: Re-run `init_db.py`
- **Import errors**: Check Python path and virtual environment

---

## Quick Reference Commands

### Backend
```bash
# Start server
uvicorn main:app --reload

# Install dependencies
pip install -r requirements.txt

# Initialize database
python db/init_db.py

# Run tests
pytest
```

### Frontend
```bash
# Start dev server
npm run dev

# Install dependencies
npm install

# Build for production
npm run build

# Run production server
npm start
```

---

## When Making Changes

### Before Modifying Code
1. Understand the layered architecture
2. Check existing patterns in similar files
3. Verify environment variables are set
4. Review related documentation

### After Making Changes
1. Test locally (both backend and frontend)
2. Update relevant documentation
3. Add/update tests if applicable
4. Check for console errors
5. Verify API endpoints in `/docs`

### Code Review Checklist
- [ ] Follows existing code patterns
- [ ] Includes type hints (Python) or types (TypeScript)
- [ ] Handles errors appropriately
- [ ] No hardcoded credentials
- [ ] Documentation updated if needed
- [ ] Tests added/updated if applicable

---

## Project Goals & Vision

### Short-term Goals
- Stable MVP with core features working
- Basic user practice flow functional
- Reliable AI integrations

### Long-term Goals
- Multi-user support with authentication
- Advanced analytics and progress tracking
- Mobile app (React Native)
- Support for multiple languages
- Gamification features
- Social learning features

### Non-Goals
- Not a general-purpose language learning platform
- Not focused on grammar or writing
- Not a replacement for human teachers

---

## Contact & Resources

### Documentation
- Project README: `README.md`
- API Reference: `docs/API_REFERENCE.md`
- Setup Guide: `docs/SETUP_GUIDE.md`
- Architecture: `docs/ARCHITECTURE.md`

### External Resources
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [DashScope API](https://dashscope.aliyun.com/)
- [Alibaba Cloud OSS](https://www.alibabacloud.com/help/en/oss/)
