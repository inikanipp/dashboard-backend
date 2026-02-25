import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import file_routes

is_production = os.getenv("ENV") == "production"

app = FastAPI(
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json"
)

# app = FastAPI()

app.include_router(file_routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://kanipganteng.browniesqu.my.id"], # URL Frontend Anda
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)