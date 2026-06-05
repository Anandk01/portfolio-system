# OAuth Setup Guide

## Quick Start (For Testing)

**Email/Password login works immediately** - no setup needed!

For OAuth (Google/GitHub), follow these steps:

---

## Google OAuth Setup

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create a new project** (or select existing)
3. **Enable Google+ API**:
   - APIs & Services → Library → Search "Google+ API" → Enable
4. **Create OAuth credentials**:
   - APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID
   - Application type: **Web application**
   - Authorized redirect URIs: `http://localhost:3000/api/auth/callback/google`
5. **Copy credentials**:
   - Copy **Client ID** and **Client Secret**
   - Add to `.env.local`:
     ```
     GOOGLE_CLIENT_ID=your-client-id-here
     GOOGLE_CLIENT_SECRET=your-client-secret-here
     ```

---

## GitHub OAuth Setup

1. **Go to GitHub Settings**: https://github.com/settings/developers
2. **New OAuth App**:
   - Application name: `Profolio AI`
   - Homepage URL: `http://localhost:3000`
   - Authorization callback URL: `http://localhost:3000/api/auth/callback/github`
3. **Generate client secret**
4. **Copy credentials**:
   - Copy **Client ID** and **Client Secret**
   - Add to `.env.local`:
     ```
     GITHUB_CLIENT_ID=your-client-id-here
     GITHUB_CLIENT_SECRET=your-client-secret-here
     ```

---

## After Setup

1. **Restart frontend**: `npm run dev`
2. **Test login**: Click "Continue with Google" or "Continue with GitHub"

---

## Production Deployment

For production (e.g., Vercel):
- Update redirect URIs to your production domain
- Add environment variables in deployment settings
- Example: `https://yourapp.com/api/auth/callback/google`
