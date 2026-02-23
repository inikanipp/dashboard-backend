from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import file_routes

app = FastAPI()

app.include_router(file_routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # URL Frontend Anda
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)