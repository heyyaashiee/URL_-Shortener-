"""
Authentication endpoints:
- POST /auth/signup : create a new user account
- POST /auth/login   : exchange email/password for a JWT access token
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.UserResponse, status_code=201)
def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account. Password is hashed with bcrypt before
    it's stored -- the plain-text password is never saved to the database.
    """
    existing_user = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Exchange email + password for a JWT access token.

    Uses OAuth2PasswordRequestForm (form fields, not JSON) so this works
    directly with Swagger UI's "Authorize" button -- note the form field
    is called "username" even though we're using it for email, that's just
    the OAuth2 spec's naming convention.
    """
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user_id=user.id)
    return schemas.Token(access_token=access_token)
