# Development Guide

## Code Organization

### Backend Structure
```
backend/
├── api/                    # API route handlers
│   ├── image_controller.py
│   └── user_practice_controller.py
├── db/                     # Database layer
│   ├── database.py        # DB connection
│   ├── init_db.py         # Schema initialization
│   ├── image_practice_task.py
│   └── user_practice_record.py
├── models/                 # External AI service clients
│   ├── asr_client.py
│   ├── qwen_client.py
│   └── qwen_image_max_client.py
├── schemas/                # Pydantic data models
│   └── image_task.py
├── services/               # Business logic
│   ├── evaluation_service.py
│   ├── image_task_repository.py
│   ├── image_task_service.py
│   ├── local_audio.py
│   ├── oss_client.py
│   ├── practice_record_repository.py
│   ├── practice_service.py
│   └── speech_service.py
├── main.py                 # Application entry point
└── requirements.txt        # Python dependencies
```

### Frontend Structure
```
frontend/
├── app/                    # Next.js app directory
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   ├── globals.css        # Global styles
│   └── spinner.css        # Component styles
├── public/                 # Static assets
├── package.json            # Node dependencies
└── tsconfig.json          # TypeScript config
```

---

## Coding Standards

### Python (Backend)

#### Style Guide
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use descriptive variable names

#### Example:
```python
from typing import Optional, Dict, Any

class ImageTaskService:
    def __init__(self) -> None:
        self.qwen = QwenClient()
        
    def generate_image_task(self, difficulty_level: str) -> Dict[str, Any]:
        """
        Generate a new image-based practice task.
        
        Args:
            difficulty_level: One of 'beginner', 'intermediate', 'advanced'
            
        Returns:
            Dictionary containing task details
        """
        semantic_plan = self.qwen.generate_semantic_plan(difficulty_level)
        return {"semantic_plan": semantic_plan}
```

#### Imports Organization
```python
# Standard library
import os
from typing import Optional

# Third-party
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Local
from services.image_task_service import ImageTaskService
from schemas.image_task import ImageTaskRequest
```

### TypeScript (Frontend)

#### Style Guide
- Use TypeScript strict mode
- Prefer functional components
- Use meaningful component names
- Follow React best practices

#### Example:
```typescript
interface TaskProps {
  taskId: number;
  imageUrl: string;
}

export default function TaskCard({ taskId, imageUrl }: TaskProps) {
  const [loading, setLoading] = useState(false);
  
  return (
    <div className="task-card">
      <img src={imageUrl} alt={`Task ${taskId}`} />
    </div>
  );
}
```

---

## Adding New Features

### Adding a New API Endpoint

1. **Define Schema** (`schemas/`)
```python
from pydantic import BaseModel

class NewFeatureRequest(BaseModel):
    field1: str
    field2: int
```

2. **Create Service** (`services/`)
```python
class NewFeatureService:
    def process(self, data: NewFeatureRequest):
        # Business logic here
        return result
```

3. **Add Controller** (`api/`)
```python
from fastapi import APIRouter
from schemas.new_feature import NewFeatureRequest
from services.new_feature_service import NewFeatureService

router = APIRouter()

@router.post("/process")
def process_feature(request: NewFeatureRequest):
    service = NewFeatureService()
    return service.process(request)
```

4. **Register Router** (`main.py`)
```python
from api.new_feature_controller import router as new_feature_router

app.include_router(
    new_feature_router, 
    prefix="/api/new-feature", 
    tags=["New Feature"]
)
```

### Adding a New Database Table

1. **Define Model** (`db/new_table.py`)
```python
from sqlalchemy import Column, Integer, String, DateTime
from db.database import Base
from datetime import datetime

class NewTable(Base):
    __tablename__ = "new_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

2. **Create Repository** (`services/new_table_repository.py`)
```python
from db.database import get_db
from db.new_table import NewTable

class NewTableRepository:
    def create(self, name: str):
        db = next(get_db())
        record = NewTable(name=name)
        db.add(record)
        db.commit()
        return record
```

3. **Update init_db.py**
```python
from db.new_table import NewTable

def init_database():
    Base.metadata.create_all(bind=engine)
```

### Adding a New AI Model Integration

1. **Create Client** (`models/new_ai_client.py`)
```python
import os
from typing import Dict, Any

class NewAIClient:
    def __init__(self):
        self.api_key = os.getenv("NEW_AI_API_KEY")
        self.base_url = "https://api.newai.com"
        
    def generate(self, prompt: str) -> str:
        # API call logic
        response = self._call_api(prompt)
        return response
        
    def _call_api(self, prompt: str) -> str:
        # Implementation
        pass
```

2. **Add Environment Variable** (`.env.example`)
```env
NEW_AI_API_KEY=your_api_key_here
```

3. **Use in Service**
```python
from models.new_ai_client import NewAIClient

class SomeService:
    def __init__(self):
        self.ai_client = NewAIClient()
```

---

## Database Operations

### Using SQLAlchemy

#### Query Examples
```python
from db.database import get_db
from db.image_practice_task import ImagePracticeTask

# Get single record
db = next(get_db())
task = db.query(ImagePracticeTask).filter(
    ImagePracticeTask.id == task_id
).first()

# Get multiple records
tasks = db.query(ImagePracticeTask).filter(
    ImagePracticeTask.difficulty_level == "beginner"
).all()

# Create record
new_task = ImagePracticeTask(
    semantic_plan="...",
    image_url="...",
    standard_answer="...",
    difficulty_level="beginner"
)
db.add(new_task)
db.commit()
db.refresh(new_task)

# Update record
task.semantic_plan = "Updated plan"
db.commit()

# Delete record
db.delete(task)
db.commit()
```

---

## Working with AI Services

### Qwen Client Usage

```python
from models.qwen_client import QwenClient

client = QwenClient()

# Generate semantic plan
plan = client.generate_semantic_plan("beginner")

# Generate standard answer
answer = client.generate_standard_answer(plan)
```

### ASR Client Usage

```python
from models.asr_client import ASRClient

client = ASRClient()

# Transcribe audio file
audio_path = "path/to/audio.wav"
transcription = client.transcribe(audio_path)
```

### OSS Client Usage

```python
from services.oss_client import OSSClient

client = OSSClient()

# Upload from URL
oss_url = client.upload_image_from_url(temp_url)

# Upload from file
oss_url = client.upload_file(file_path, object_name)

# Download file
local_path = client.download_file(oss_url)
```

---

## Testing

### Unit Testing

#### Backend Test Example
```python
import pytest
from services.image_task_service import ImageTaskService

def test_generate_image_task():
    service = ImageTaskService()
    result = service.generate_image_task("beginner")
    
    assert "semantic_plan" in result
    assert "image_url" in result
    assert "standard_answer" in result
```

#### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_image_service.py

# Run with coverage
pytest --cov=services tests/
```

### Integration Testing

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_generate_task_endpoint():
    response = client.get("/api/image/generate")
    assert response.status_code == 200
    data = response.json()
    assert "semantic_plan" in data
```

---

## Debugging

### Backend Debugging

#### Enable Debug Logging
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

#### Using Debugger
```python
import pdb

def some_function():
    pdb.set_trace()  # Breakpoint
    # Code continues...
```

### Frontend Debugging

#### Console Logging
```typescript
console.log('Debug:', data);
console.error('Error:', error);
```

#### React DevTools
- Install React Developer Tools browser extension
- Inspect component props and state
- Profile performance

---

## Performance Optimization

### Backend

#### Database Query Optimization
```python
# Bad: N+1 queries
tasks = db.query(ImagePracticeTask).all()
for task in tasks:
    records = db.query(PracticeRecord).filter(
        PracticeRecord.task_id == task.id
    ).all()

# Good: Join query
from sqlalchemy.orm import joinedload

tasks = db.query(ImagePracticeTask).options(
    joinedload(ImagePracticeTask.practice_records)
).all()
```

#### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_task_by_id(task_id: int):
    # Expensive operation
    return result
```

### Frontend

#### Image Optimization
```typescript
import Image from 'next/image'

<Image
  src={imageUrl}
  alt="Task"
  width={500}
  height={300}
  loading="lazy"
/>
```

#### Code Splitting
```typescript
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <p>Loading...</p>
})
```

---

## Git Workflow

### Branch Naming
- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/critical-fix` - Critical production fixes
- `refactor/component-name` - Code refactoring

### Commit Messages
```
feat: Add user practice history endpoint
fix: Resolve CORS issue with audio upload
refactor: Simplify image task service logic
docs: Update API documentation
test: Add unit tests for evaluation service
```

### Pull Request Process
1. Create feature branch
2. Make changes and commit
3. Write/update tests
4. Update documentation
5. Create pull request
6. Code review
7. Merge to main

---

## Environment Management

### Development
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

### Production
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

---

## Common Patterns

### Error Handling
```python
from fastapi import HTTPException

try:
    result = some_operation()
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Dependency Injection
```python
from fastapi import Depends
from db.database import get_db
from sqlalchemy.orm import Session

@router.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(ImagePracticeTask).all()
```

### Async Operations
```python
import asyncio

async def async_operation():
    result = await some_async_call()
    return result
```
