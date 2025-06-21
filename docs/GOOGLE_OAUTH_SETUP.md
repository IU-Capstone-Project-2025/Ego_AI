# Google OAuth Setup Guide

This document describes the Google OAuth authentication flow implemented in the EGO:AI application.

## Overview

The application uses Google OAuth 2.0 for user authentication. The flow follows these steps:

1. User clicks "Sign In with Google" or "Sign Up with Google"
2. User is redirected to Google's authorization server
3. User authenticates and grants permissions
4. Google redirects back to our callback endpoint with an authorization code
5. Backend exchanges the code for user information
6. Backend creates/finds user in database and generates JWT token
7. User is redirected to frontend with JWT token
8. Frontend stores token and redirects to main application

## Backend Configuration

### Environment Variables

Update your `.env` file with the following variables:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret" 
GOOGLE_REDIRECT_URI="http://185.207.133.14:8000/api/v1/auth/google/callback"

# Frontend Configuration
FRONTEND_URL="http://185.207.133.14:3000"
BACKEND_CORS_ORIGINS=["http://185.207.133.14:3000", "http://localhost:3000"]
```

### API Endpoints

- `GET /api/v1/auth/google-login` - Initiates Google OAuth flow
- `GET /api/v1/auth/google/callback` - Handles OAuth callback from Google

## Frontend Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://185.207.133.14:8000
```

### Authentication Flow

1. **Login Page**: `RegPage` component handles initial authentication
2. **Callback Handler**: `LoginCallback` component processes OAuth callback
3. **Protected Routes**: `ProtectedRoute` component guards authenticated pages
4. **Auth Utilities**: `api.ts` and `useAuth.ts` provide authentication helpers

### Components

- `RegPage`: Registration/login page with Google OAuth buttons
- `LoginCallback`: Handles OAuth callback and token storage
- `ProtectedRoute`: HOC for protecting authenticated routes
- `Layout`: Navigation with logout functionality

## Google Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable Google+ API and Google OAuth2 API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://185.207.133.14:8000/api/v1/auth/google/callback`
   - `http://localhost:8000/api/v1/auth/google/callback` (for development)

## Security Features

- JWT tokens with expiration
- Secure token storage in localStorage
- CORS protection
- Protected routes requiring authentication
- Automatic token validation and cleanup

## Development vs Production

### Development
- Use `localhost` URLs in environment variables
- CORS allows localhost origins

### Production  
- Use production server URLs (185.207.133.14)
- Update Google OAuth redirect URIs
- Configure proper CORS origins

## Testing the Flow

1. Start backend server: `cd backend && python main.py`
2. Start frontend server: `cd frontend && npm run dev`
3. Navigate to registration page
4. Click "Sign In with Google"
5. Complete Google authentication
6. Verify redirect to calendar page with stored JWT token
