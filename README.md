# URL Shortener

A URL shortener with user accounts and click tracking. The backend is built with FastAPI and uses JWT authentication. Users can sign up, create short links, view their own links, and be redirected through short codes, with every visit recorded as a click.

## Features

- User signup and login with hashed passwords
- JWT-based authentication
- Short code generation using base62 with collision handling
- Redirect from short code to original URL
- Per-user link dashboard (`/my-links`)
- Click tracking for each short link
- Interactive API docs (Swagger UI) out of the box
- Health check endpoint

## Tech Stack

- Python 3.9+
- FastAPI
- SQLAlchemy
- Pydantic
- JWT (python-jose or PyJWT)
- Uvicorn

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── database.py       # DB connection, session factory
│   ├── models.py         # User, URL, Click tables
│   ├── schemas.py        # Pydantic request/response models
│   ├── shortener.py      # base62 short-code generation + collision handling
│   ├── auth.py           # password hashing, JWT creation/verification
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py       # POST /auth/signup, POST /auth/login
│   │   └── urls.py       # POST /shorten, GET /my-links, GET /{short_code}
│   └── main.py           # FastAPI app + health check
├── requirements.txt
└── .env.example
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/url-shortener.git
cd url-shortener/backend
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Then edit `.env`:

```
DATABASE_URL=sqlite:///./urls.db
SECRET_KEY=change-this-to-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
BASE_URL=http://localhost:8000
```

Generate a strong secret key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint         | Auth | Description                      |
|--------|------------------|------|----------------------------------|
| POST   | `/auth/signup`   | No   | Create a new account             |
| POST   | `/auth/login`    | No   | Log in and receive a JWT         |
| POST   | `/shorten`       | Yes  | Create a short URL               |
| GET    | `/my-links`      | Yes  | List the current user's links    |
| GET    | `/{short_code}`  | No   | Redirect to the original URL     |
| GET    | `/health`        | No   | Health check                     |

### Example usage

**Sign up**

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "StrongPass123"}'
```

**Log in**

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "StrongPass123"}'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Shorten a URL**

```bash
curl -X POST http://localhost:8000/shorten \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/link"}'
```

Response:

```json
{
  "short_code": "aB3xYz",
  "short_url": "http://localhost:8000/aB3xYz",
  "original_url": "https://www.example.com/very/long/link"
}
```

**List your links**

```bash
curl http://localhost:8000/my-links \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Visit a short link**

Open `http://localhost:8000/aB3xYz` in a browser. You'll be redirected to the original URL and a click is recorded.

## How It Works

- **Short codes:** each URL gets an auto-incrementing ID or random number that is encoded in base62 (`0-9a-zA-Z`). If a generated code already exists, a new one is generated until it is unique.
- **Authentication:** passwords are hashed before storage. On login, the server issues a signed JWT that must be sent in the `Authorization: Bearer <token>` header for protected routes.
- **Click tracking:** every request to `/{short_code}` stores a record in the `Click` table linked to the URL.

## Database Models

- **User:** id, email, hashed password, created_at
- **URL:** id, original_url, short_code, owner (User), created_at
- **Click:** id, url (URL), clicked_at

## Security Notes

- Never commit your `.env` file. Only `.env.example` belongs in the repo.
- Use a long, random `SECRET_KEY` in production.
- Run behind HTTPS in production.

## Future Improvements

- Custom aliases
- Link expiration
- Click analytics dashboard (by date, country, device)
- Rate limiting
- Docker support
- Frontend UI

## Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit your changes
4. Push and open a pull request

## License

MIT License
