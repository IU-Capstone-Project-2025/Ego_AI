# Frontend Integration Guide for EgoAI Backend

This quick guide contains all the necessary information for connecting a frontend application to the EgoAI backend.

## 1. Basic Setup

### Environment Variables

In your frontend's `.env` (or `.env.local`) file, you need to define the following variable:

```env
# API URL
# (Use REACT_APP_... or VITE_... depending on your bundler)
REACT_APP_API_URL=http://localhost:8000
```

### API Endpoint

All API requests should be sent to: **`{REACT_APP_API_URL}/api/v1/...`**

### API Documentation

Complete interactive documentation for all available endpoints is located at:
**[http://localhost:8000/docs](http://localhost:8000/docs)**

Use it to view data models, request parameters, and response examples.

---

## 2. Authentication Process (Google OAuth2)

Authentication is implemented through the backend. The frontend doesn't work with Google SDK directly.

### Step 1: Initiating Login

When a user clicks the "Login with Google" button:

1.  Send a **GET** request to the endpoint:
    ```
    GET {REACT_APP_API_URL}/api/v1/auth/google-login
    ```
2.  The backend will return JSON with a single `url` field:
    ```json
    {
      "url": "https://accounts.google.com/o/oauth2/v2/auth?..."
    }
    ```
3.  Immediately redirect the user to the received `url`:
    ```javascript
    window.location.href = response.data.url;
    ```

### Step 2: Handling User Return

1.  After successful Google login, the backend will redirect the user back to your application, to a special route that you should create, for example, `/login/callback`.
2.  The URL will contain a JWT token as a query parameter:
    ```
    http://localhost:3000/login/callback?token=eyJhbGciOiJIUzI1Ni...
    ```
3.  On this page (`/login/callback`), your task is to extract the token from the URL.
    ```javascript
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    ```

### Step 3: Saving Token and Completing Login

1.  If the token is received, save it in `localStorage`:
    ```javascript
    if (token) {
      localStorage.setItem('accessToken', token);
      // Redirect user to their dashboard
      window.location.href = '/dashboard'; 
    } else {
      // Handle login error
      window.location.href = '/login-error';
    }
    ```

---

## 3. Making Authenticated Requests

For all requests to protected API endpoints (e.g., getting events, creating reminders), you must:

1.  Get the token from `localStorage`.
2.  Add it to the `Authorization` header.

**Example using `axios`:**

```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: `${process.env.REACT_APP_API_URL}/api/v1`
});

// Use interceptor to automatically add token to all requests
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Now you can simply use apiClient for requests
export const fetchMyEvents = () => apiClient.get('/events/');
export const createNewEvent = (eventData) => apiClient.post('/events/', eventData);
```
