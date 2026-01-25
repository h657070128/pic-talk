from pydantic import BaseModel

class ImageTaskRequest(BaseModel):
    difficulty_level: str = "beginner"
