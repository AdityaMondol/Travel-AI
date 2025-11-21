# Google OAuth 2.0 Setup Guide

This guide will walk you through setting up Google OAuth 2.0 authentication for the AI Agent Army backend.

## Prerequisites

- A Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Enter a project name (e.g., "AI Agent Army")
4. Click **Create**

## Step 2: Enable Google+ API

1. In the Google Cloud Console, navigate to **APIs & Services** → **Library**
2. Search for "Google+ API"
3. Click on it and press **Enable**

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** (unless you have a Google Workspace account)
3. Click **Create**
4. Fill in the required fields:
   - **App name**: AI Agent Army
   - **User support email**: Your email
   - **Developer contact information**: Your email
5. Click **Save and Continue**
6. **Scopes**: Click **Add or Remove Scopes**
   - Add: `openid`
   - Add: `email`
   - Add: `profile`
7. Click **Save and Continue**
8. **Test users** (Optional): Add test email addresses if in testing mode
9. Click **Save and Continue**

## Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Choose **Application type**: **Web application**
4. **Name**: AI Agent Army Web Client
5. **Authorized JavaScript origins**:
   - Add: `http://localhost:8000`
   - Add: `http://127.0.0.1:8000`
   - (Add your production domain when deploying)
6. **Authorized redirect URIs**:
   - Add: `http://localhost:8000/auth/callback`
   - Add: `http://127.0.0.1:8000/auth/callback`
   - (Add your production callback URL when deploying)
7. Click **Create**
8. **Download** the JSON file or copy the **Client ID** and **Client Secret**

## Step 5: Configure Environment Variables

Create or update your `.env` file in the project root:

```bash
# Google OAuth 2.0
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# LLM Provider (optional, for Google Gemini API)
LLM_PROVIDER=google
GOOGLE_API_KEY=your-google-gemini-api-key-here

# Other providers (optional)
NVIDIA_API_KEY=your-nvidia-api-key
OPENROUTER_API_KEY=your-openrouter-api-key

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## Step 6: Test the OAuth Flow

1. Start your application:
   ```bash
   python run.py
   ```

2. Navigate to `http://localhost:8000/auth/login` in your browser

3. You should be redirected to Google's login page

4. After successful login, you'll be redirected back to your app with user information stored in cookies

## Available Endpoints

### Authentication Endpoints

- **`GET /auth/login`**: Initiates the OAuth flow (redirects to Google)
- **`GET /auth/callback`**: OAuth callback endpoint (handles the response from Google)
- **`GET /auth/user`**: Returns the currently logged-in user information
- **`GET /auth/logout`**: Logs out the user (clears cookies)

### Example Usage

```javascript
// Frontend example: Initiate login
window.location.href = '/auth/login';

// Check if user is logged in
fetch('/auth/user')
  .then(res => res.json())
  .then(user => {
    if (user.email) {
      console.log('Logged in as:', user.email);
    } else {
      console.log('Not logged in');
    }
  });

// Logout
window.location.href = '/auth/logout';
```

## Security Considerations

> [!WARNING]
> **Production Deployment**
> - Use HTTPS in production (required by Google OAuth)
> - Store secrets in secure environment variables, not in code
> - Update redirect URIs to your production domain
> - Use secure, HTTPOnly cookies for session management

> [!CAUTION]
> **Client Secret Protection**
> - Never commit `.env` files to version control
> - Keep your `GOOGLE_CLIENT_SECRET` confidential
> - Rotate credentials if they are ever exposed

## Troubleshooting

### Error: "redirect_uri_mismatch"
- Ensure the redirect URI in `.env` exactly matches one configured in Google Cloud Console
- Check for trailing slashes – `http://localhost:8000/auth/callback` ≠ `http://localhost:8000/auth/callback/`

### Error: "Access blocked: This app's request is invalid"
- Complete the OAuth consent screen configuration
- Add your email as a test user if the app is in testing mode

### Error: "Google Client ID not configured"
- Verify `GOOGLE_CLIENT_ID` is set in `.env`
- Restart the application after updating `.env`

## Production Deployment

When deploying to production:

1. Update **Authorized JavaScript origins** and **Authorized redirect URIs** in Google Cloud Console with your production URLs
2. Update `.env`:
   ```bash
   GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/callback
   ```
3. Ensure your app uses HTTPS (required by Google)
4. Consider implementing a proper session management system (e.g., Redis, database-backed sessions)

## Next Steps

- Integrate OAuth with protected API endpoints
- Implement role-based access control (RBAC)
- Add user profile management
- Set up refresh token handling for long-lived sessions
