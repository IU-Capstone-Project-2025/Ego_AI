# EgoAI Backend Documentation

This is a detailed guide for setting up, running, testing, and integrating the EgoAI backend. For a quick introduction to the project architecture and understanding how to contribute, see [Developer Guide](./DEVELOPER_GUIDE.md).

## Table of Contents

1.  [Overview](#1-overview)
2.  [Development Environment Setup](#2-development-environment-setup)
    *   [Requirements](#requirements)
    *   [Installation](#installation)
    *   [Environment Variables Setup (.env)](#environment-variables-setup-env)
3.  [Database Management (Alembic)](#3-database-management-alembic)
4.  [Running the Application](#4-running-the-application)
    *   [Development Mode](#development-mode)
    *   [Production Mode (Local)](#production-mode-local)
5.  [Frontend Integration](#5-frontend-integration)
6.  [API Testing (Manual)](#6-api-testing-manual)
7.  [Automated Tests (Pytest)](#7-automated-tests-pytest)
8.  [Project Structure](#8-project-structure)
9.  [Running in Docker](#9-running-in-docker)

---

## 1. Overview

The EgoAI backend is built on FastAPI using SQLAlchemy for ORM and asynchronous interaction with PostgreSQL. It provides a RESTful API for managing users, events, reminders, AI interactions, and user settings. The project follows a clear architecture with separation of concerns (service layer, data access layer) and supports authentication via Google OAuth2.

## 2. Development Environment Setup

### Requirements

*   Python 3.9+
*   pip (Python package manager)
*   PostgreSQL (locally or via Docker)
*   Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/Ego_AI.git
    cd Ego_AI/backend
    ```

2.  **Create and activate virtual environment:**
    *   **Windows:** `python -m venv venv` and `.\\venv\\Scripts\\activate`
    *   **macOS/Linux:** `python3 -m venv venv` and `source venv/bin/activate`

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Environment Variables Setup (.env)

The backend uses environment variables for configuration. Create an `.env` file in the backend root directory (`Ego_AI/backend/`).

**Example `.env` file:**

```env
# Ego_AI/backend/.env

# APPLICATION MODE
# "development" - for local development with --reload (disables CSRF check for OAuth)
# "production" - for running in Docker or locally without --reload (enables full security)
ENVIRONMENT="development"

# FRONTEND URL
# Address where the user will be redirected after successful login
FRONTEND_URL="http://localhost:3000"

# SECURITY
SECRET_KEY="YOUR_VERY_SECRET_KEY" # Generate using: python -c 'import secrets; print(secrets.token_urlsafe(32))'
ACCESS_TOKEN_EXPIRE_MINUTES=11520 # 8 days

# GOOGLE OAUTH
# Get these from Google Cloud Console
GOOGLE_CLIENT_ID="YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="YOUR_GOOGLE_CLIENT_SECRET"
# This URI must be added to "Authorized redirect URIs" in Google OAuth settings
GOOGLE_REDIRECT_URI="http://localhost:8000/api/v1/auth/google/callback"

# POSTGRESQL DATABASE
# Specify full connection URL
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/egoai"
```

**Important:** Replace placeholders (`YOUR_...`) with your actual values.

## 3. Database Management (Alembic)

Alembic is used to manage all database schema migrations.

1.  **Make sure your PostgreSQL server is running.**
2.  **Apply all migrations** to create tables:
    ```bash
    alembic upgrade head
    ```
3.  After changing models in `app/database/models/models.py`, **create a new migration:**
    ```bash
    alembic revision --autogenerate -m "Brief description of changes"
    ```
4.  **Always review** the generated file in `alembic/versions/` before applying.

## 4. Running the Application

### Development Mode

Perfect for writing code. Uses hot reload and less strict security settings for convenience.

1.  In `.env` set `ENVIRONMENT="development"`.
2.  Start the server:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

### Production Mode (Local)

Used for testing the application in a configuration closest to real (no reload, full security).

1.  In `.env` set `ENVIRONMENT="production"`.
2.  Start the server:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

## 5. Frontend Integration

The backend is fully ready for integration with client applications. The Google authentication process and API interaction examples for the frontend team are detailed in a separate guide.

**See [Frontend Integration Guide](./FRONTEND_INTEGRATION.md)**

## 6. API Testing (Manual)

Interactive API documentation is available at `http://localhost:8000/docs` after starting the server. Here you can view all endpoints and test them directly.

## 7. Automated Tests (Pytest)

The project contains a set of integration tests.

*   **Run all tests:**
    ```bash
    pytest
    ```
*   **Run with code coverage analysis:**
    ```bash
    coverage run -m pytest
    coverage report -m
    ```
*   **Create interactive HTML coverage report:**
    ```bash
    coverage html
    ```
    (Report will be in `htmlcov/` folder)

## 8. Project Structure

```
Ego_AI/
└── backend/
    ├── alembic/            # Alembic configuration files and migration scripts
    ├── app/
    │   ├── api/
    │   │   ├── endpoints/  # API endpoints (routes), call services
    │   │   └── router.py   # Main API router
    │   ├── auth/           # Authentication modules (Google OAuth, JWT)
    │   ├── core/           # Core configurations (settings, exceptions, logging)
    │   ├── database/
    │   │   ├── crud/       # CRUD operations (low-level DB access)
    │   │   ├── models/     # SQLAlchemy model definitions
    │   │   ├── schemas/    # Pydantic schemas for data validation
    │   │   └── session.py  # Database session configuration
    │   ├── services/       # Business logic layer. Encapsulates all data handling logic.
    │   └── utils/          # Helper utilities (dependencies, etc.)
    ├── docs/               # Project documentation
    ├── tests/              # Integration tests (pytest)
    ├── .coveragerc         # Code coverage configuration
    ├── alembic.ini         # Main Alembic configuration file
    ├── Dockerfile          # Backend Dockerfile
    ├── main.py            # FastAPI application main file
    └── requirements.txt    # Python dependencies
```

## 9. Running in Docker

To run the entire stack (backend, frontend, PostgreSQL) in Docker Compose, go to the project root directory (`Ego_AI/`) and execute:

```bash
docker-compose up --build -d
```
This is the most reliable and recommended way to run the application in an environment identical to production.

--- 