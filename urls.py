"""
Core URL-shortening endpoints:
- POST /shorten       : take a long URL, return a short one (requires auth)
- GET  /my-links      : list the authenticated user's short URLs
- GET  /{short_code}  : redirect to the original URL (public, no auth)
"""

import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.shortener import generate_unique_short_code
from app.auth import get_current_user

router = APIRouter(tags=["urls"])

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@router.post("/shorten", response_model=schemas.URLResponse, status_code=201)
def create_short_url(
    payload: schemas.URLCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Create a new shortened URL, owned by the authenticated user.
    Requires an `Authorization: Bearer <token>` header (see /auth/login).

    Example request body:
        { "original_url": "https://example.com/some/very/long/path" }
    """
    short_code = generate_unique_short_code(db)

    url_entry = models.URL(
        short_code=short_code,
        original_url=str(payload.original_url),
        owner_id=current_user.id,
    )

    db.add(url_entry)
    db.commit()
    db.refresh(url_entry)

    return url_entry


@router.get("/my-links", response_model=list[schemas.URLResponse])
def list_my_links(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Return every short URL created by the currently authenticated user."""
    return (
        db.query(models.URL)
        .filter(models.URL.owner_id == current_user.id)
        .order_by(models.URL.created_at.desc())
        .all()
    )


@router.get("/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    """
    Redirect a short code to its original URL.
    Returns 404 if the code doesn't exist or has been deactivated.

    Click tracking (referrer, user-agent, timestamp) gets added in Step 5
    of the roadmap -- for now this just performs the redirect.
    """
    url_entry = (
        db.query(models.URL)
        .filter(models.URL.short_code == short_code, models.URL.is_active == True)  # noqa: E712
        .first()
    )

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=url_entry.original_url, status_code=307)
