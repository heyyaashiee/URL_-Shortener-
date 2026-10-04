"""
FastAPI application entry point.

For now this just:
1. Creates the database tables (users, urls, clicks) if they don't exist
2. Exposes a health-check endpoint so you can confirm the server + DB work

The /shorten and /{short_code} endpoints come in Step 2 of the roadmap.
"""

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import engine, Base, get_db
from app import models  # noqa: F401  (import so models register with Base)
from app.routers import urls

# Creates all tables defined in models.py, if they don't already exist.
# Later you'll likely switch to Alembic migrations for schema changes.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="A URL shortener with click analytics.",
    version="0.1.0",
)

@app.get("/")
def root():
    return {"message": "URL Shortener API is running"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Confirms both the API and the database connection are working.
    Hit this after `uvicorn app.main:app --reload` to sanity-check your setup.
    """
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


# IMPORTANT: this must be included AFTER the routes above.
# app.routers.urls defines a catch-all GET /{short_code} route, which would
# otherwise shadow "/" and "/health" if registered first (FastAPI/Starlette
# matches routes in registration order).
app.include_router(urls.router)
