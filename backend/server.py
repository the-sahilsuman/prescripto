import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.mongodb import connect_db, close_db
from config.cloudinary import connect_cloudinary
from routes.admin_route import router as admin_router
from routes.doctor_route import router as doctor_router
from routes.user_route import router as user_router
from routes.auth_route import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    connect_cloudinary()
    yield
    # Shutdown
    await close_db()


app = FastAPI(lifespan=lifespan)

# CORS — build origins list, always include localhost for local dev
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

# Add production URLs from .env if they are set
for url in [os.getenv("FRONTEND_URL"), os.getenv("ADMIN_URL")]:
    if url and url not in origins:
        origins.append(url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(doctor_router, tags=["Doctors"])
app.include_router(user_router, tags=["Users"])


@app.get("/",tag="Root")
async def root():
    return "API WORKING FINE"


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 4000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
