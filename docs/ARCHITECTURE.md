# Architecture Documentation

## System Architecture

### Overview
pic-talk follows a client-server architecture with a FastAPI backend and Next.js frontend, integrated with multiple AI services from Alibaba Cloud.

```
┌─────────────────┐
│  Next.js Client │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Server │
│    (Backend)    │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌──────┐
│ Qwen   │ │ Qwen │ │DashScope│ │ OSS  │
│ Client │ │Image │ │  (ASR)  │ │Client│
└────────┘ └──────┘ └────────┘ └──────┘
```

## Backend Architecture

### Layered Architecture

```
┌──────────────────────────────────┐
│     API Layer (Controllers)      │  ← HTTP endpoints
├──────────────────────────────────┤
│     Service Layer                │  ← Business logic
├──────────────────────────────────┤
│     Repository Layer             │  ← Data access
├──────────────────────────────────┤
│     Database Layer               │  ← SQLite storage
└──────────────────────────────────┘

External:
┌──────────────────────────────────┐
│     Models Layer                 │  ← AI client wrappers
└──────────────────────────────────┘
```

### Component Breakdown

#### 1. API Layer (`/api`)
**Purpose**: Handle HTTP requests and responses

**Files**:
- `image_controller.py` - Image task endpoints
- `user_practice_controller.py` - Practice session endpoints

**Responsibilities**:
- Route definition
- Request validation
- Response formatting
- Error handling

#### 2. Service Layer (`/services`)
**Purpose**: Implement business logic

**Key Services**:
- `ImageTaskService` - Task generation orchestration
- `PracticeService` - Practice session management
- `EvaluationService` - Response scoring
- `SpeechService` - Audio processing

**Responsibilities**:
- Coordinate between repositories and models
- Implement business rules
- Handle complex workflows

#### 3. Repository Layer (`/services/*_repository.py`)
**Purpose**: Abstract database operations

**Key Repositories**:
- `ImageTaskRepository` - CRUD for practice tasks
- `PracticeRecordRepository` - CRUD for user records

**Responsibilities**:
- Database queries
- Data persistence
- Transaction management

#### 4. Models Layer (`/models`)
**Purpose**: Integrate external AI services

**Key Clients**:
- `QwenClient` - Text generation (semantic plans, answers)
- `QwenImageMaxClient` - Image generation
- `ASRClient` - Speech-to-text conversion

**Responsibilities**:
- API communication
- Response parsing
- Error handling for external services

#### 5. Database Layer (`/db`)
**Purpose**: Define data structures

**Components**:
- `database.py` - Database connection
- `image_practice_task.py` - Task table definition
- `user_practice_record.py` - Practice record table
- `init_db.py` - Database initialization

## Frontend Architecture

### Next.js App Router Structure

```
app/
├── layout.tsx       # Root layout
├── page.tsx         # Home page
├── globals.css      # Global styles
└── spinner.css      # Loading animations
```

### Component Organization
- Uses Next.js 16 App Router
- Server and Client Components
- TailwindCSS for styling

## Data Flow

### Task Generation Flow
```
1. User requests task
   ↓
2. ImageTaskService.generate_image_task()
   ↓
3. QwenClient.generate_semantic_plan()
   ↓
4. QwenImageMaxClient.generate_image()
   ↓
5. OSSClient.upload_image_from_url()
   ↓
6. QwenClient.generate_standard_answer()
   ↓
7. ImageTaskRepository.save_task()
   ↓
8. Return task to client
```

### Practice Session Flow
```
1. User views task image
   ↓
2. User speaks description
   ↓
3. Frontend captures audio
   ↓
4. POST to /api/user-practice
   ↓
5. SpeechService processes audio
   ↓
6. ASRClient transcribes speech
   ↓
7. EvaluationService scores response
   ↓
8. PracticeRecordRepository saves record
   ↓
9. Return feedback to client
```

## Database Schema

### image_practice_task
- `id` (PRIMARY KEY)
- `semantic_plan` (TEXT) - AI-generated description plan
- `image_url` (TEXT) - OSS URL to practice image
- `standard_answer` (TEXT) - Expected response
- `difficulty_level` (TEXT) - beginner/intermediate/advanced
- `created_at` (TIMESTAMP)

### user_practice_record
- `id` (PRIMARY KEY)
- `task_id` (FOREIGN KEY)
- `user_response` (TEXT) - Transcribed speech
- `score` (FLOAT) - Evaluation score
- `feedback` (TEXT) - AI-generated feedback
- `audio_url` (TEXT) - OSS URL to recorded audio
- `created_at` (TIMESTAMP)

## External Dependencies

### Alibaba Cloud Services
1. **DashScope** - Multi-modal AI platform
   - Qwen models for text generation
   - ASR for speech recognition
   
2. **OSS** - Object Storage Service
   - Image storage
   - Audio file storage

### CORS Configuration
- Allows `http://localhost:3000` (development)
- Credentials enabled
- All methods and headers permitted

## Security Considerations
- API keys stored in `.env` (not committed)
- CORS restricted to specific origins
- Input validation via Pydantic schemas
- Environment-based configuration

## Scalability Notes
- SQLite suitable for development/small scale
- Consider PostgreSQL for production
- OSS provides scalable storage
- Stateless API design enables horizontal scaling
