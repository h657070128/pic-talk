# API Reference

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required (development mode).

---

## Endpoints

### Health Check

#### `GET /`
Check if the API is running.

**Response**:
```json
{
  "status": "ok"
}
```

---

## Image Task Endpoints

### Generate New Task

#### `GET /api/image/generate`
Generate a new image-based practice task with AI.

**Query Parameters**: None (currently hardcoded to "beginner" difficulty)

**Response**:
```json
{
  "semantic_plan": "A sunny park with children playing on swings...",
  "image_url": "https://oss-url.com/image.jpg",
  "standard_answer": "In this picture, I can see children playing..."
}
```

**Process**:
1. Generates semantic plan using Qwen
2. Creates image using Qwen Image Max
3. Uploads image to OSS
4. Generates standard answer
5. Saves task to database

**Status Codes**:
- `200` - Success
- `500` - Internal server error (AI service failure)

---

### Get Random Task

#### `GET /api/image/get_random_task`
Retrieve a random existing practice task from the database.

**Response**:
```json
{
  "id": 1,
  "semantic_plan": "A sunny park with children playing on swings...",
  "image_url": "https://oss-url.com/image.jpg",
  "standard_answer": "In this picture, I can see children playing...",
  "difficulty_level": "beginner",
  "created_at": "2026-04-07T10:30:00"
}
```

**Status Codes**:
- `200` - Success
- `404` - No tasks found
- `500` - Internal server error

---

## User Practice Endpoints

### Submit Practice

#### `POST /api/user-practice/submit`
Submit a user's practice attempt for evaluation.

**Request Body**:
```json
{
  "task_id": 1,
  "audio_data": "base64_encoded_audio_string"
}
```

**Response**:
```json
{
  "id": 1,
  "task_id": 1,
  "user_response": "In this picture I see children playing...",
  "score": 85.5,
  "feedback": "Good job! Your pronunciation is clear. Try to use more descriptive adjectives...",
  "audio_url": "https://oss-url.com/audio/user_123.wav",
  "created_at": "2026-04-07T11:00:00"
}
```

**Process**:
1. Receives audio data
2. Transcribes using ASR
3. Evaluates against standard answer
4. Uploads audio to OSS
5. Saves practice record
6. Returns feedback

**Status Codes**:
- `200` - Success
- `400` - Invalid request (missing fields)
- `404` - Task not found
- `500` - Internal server error

---

### Get Practice History

#### `GET /api/user-practice/history`
Retrieve user's practice history.

**Query Parameters**:
- `limit` (optional) - Number of records to return (default: 10)
- `offset` (optional) - Pagination offset (default: 0)

**Response**:
```json
{
  "total": 25,
  "records": [
    {
      "id": 1,
      "task_id": 1,
      "score": 85.5,
      "created_at": "2026-04-07T11:00:00"
    },
    ...
  ]
}
```

**Status Codes**:
- `200` - Success
- `500` - Internal server error

---

### Get Practice Details

#### `GET /api/user-practice/{practice_id}`
Get detailed information about a specific practice attempt.

**Path Parameters**:
- `practice_id` - ID of the practice record

**Response**:
```json
{
  "id": 1,
  "task_id": 1,
  "user_response": "In this picture I see children playing...",
  "score": 85.5,
  "feedback": "Good job! Your pronunciation is clear...",
  "audio_url": "https://oss-url.com/audio/user_123.wav",
  "created_at": "2026-04-07T11:00:00",
  "task": {
    "semantic_plan": "A sunny park with children playing...",
    "image_url": "https://oss-url.com/image.jpg",
    "standard_answer": "In this picture, I can see children playing..."
  }
}
```

**Status Codes**:
- `200` - Success
- `404` - Practice record not found
- `500` - Internal server error

---

## Data Models

### ImageTaskRequest
```python
{
  "difficulty_level": str  # "beginner" | "intermediate" | "advanced"
}
```

### PracticeSubmission
```python
{
  "task_id": int,
  "audio_data": str  # Base64 encoded audio
}
```

### ImageTask
```python
{
  "id": int,
  "semantic_plan": str,
  "image_url": str,
  "standard_answer": str,
  "difficulty_level": str,
  "created_at": datetime
}
```

### PracticeRecord
```python
{
  "id": int,
  "task_id": int,
  "user_response": str,
  "score": float,
  "feedback": str,
  "audio_url": str,
  "created_at": datetime
}
```

---

## Error Responses

All endpoints may return error responses in this format:

```json
{
  "detail": "Error message description"
}
```

Common error codes:
- `400` - Bad Request (invalid input)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error (server-side issue)

---

## CORS Configuration

The API allows cross-origin requests from:
- `http://localhost:3000` (development frontend)

Credentials are enabled for all requests.

---

## Rate Limiting
Currently no rate limiting implemented (development mode).

## Notes
- All timestamps are in ISO 8601 format
- Audio data should be base64 encoded WAV format
- Image URLs are publicly accessible OSS URLs
- Scores range from 0-100
