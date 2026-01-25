from fastapi import FastAPI
from api.image_controller import router as image_router
from api.user_practice_controller import router as user_practice_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI English Speaking Backend")

app.include_router(image_router, prefix="/api/image", tags=["Image Task"])
app.include_router(user_practice_router, prefix="/api/user-practice", tags=["User Practice"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok"}
