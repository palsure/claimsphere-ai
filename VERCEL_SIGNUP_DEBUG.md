# Vercel Signup Debugging Guide

## Changes Made

I've updated the signup page with better error handling and debugging:

### 1. Enhanced Error Logging
- Added console.log statements to track signup flow
- Shows when signup is attempted and when it succeeds
- Logs full error details to browser console

### 2. Visual Feedback
- Added "Creating your account..." message while submitting
- Better error message display with "Error:" prefix
- Shows API URL in console on page load

## How to Debug on Vercel

### Step 1: Check Browser Console
1. Open your Vercel deployment: https://your-app.vercel.app/signup
2. Open Browser DevTools (F12 or Right-click → Inspect)
3. Go to Console tab
4. Try to sign up and watch for these logs:
   - `API URL: <your-backend-url>` (on page load)
   - `Attempting signup with: { fullName, email }` (on submit)
   - `Signup error:` (if there's an error)
   - `Signup successful, redirecting to dashboard` (if successful)

### Step 2: Check Network Tab
1. In DevTools, go to Network tab
2. Try to sign up
3. Look for the `/api/auth/register` request
4. Check:
   - **Status Code**: Should be 200 or 201 for success
   - **Request Payload**: Should show email, password, first_name, last_name
   - **Response**: Should show access_token, refresh_token, and user object

### Step 3: Verify Vercel Environment Variables

The most common issue is incorrect API URL. Check your Vercel environment variables:

1. Go to your Vercel Dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Verify `NEXT_PUBLIC_API_URL` is set to your backend URL:
   - Example: `https://claimsphere-ai-backend.onrender.com`
   - Example: `https://your-backend.onrender.com`
5. Make sure it's set for all environments (Production, Preview, Development)
6. **Important**: After adding/changing environment variables, you MUST redeploy

### Step 4: Common Issues and Fixes

#### Issue: API URL is undefined
**Symptom**: Console shows `API URL: undefined`
**Fix**: 
- Add `NEXT_PUBLIC_API_URL` environment variable in Vercel
- Redeploy after adding

#### Issue: CORS Error
**Symptom**: Console shows "CORS policy" error
**Fix**: 
- Ensure backend CORS is configured to allow your Vercel domain
- Check backend `FRONTEND_URL` environment variable

#### Issue: 401/403 Error
**Symptom**: Network tab shows 401 or 403 response
**Fix**: 
- Check if backend is running and accessible
- Verify backend accepts the request format

#### Issue: Network Error / Failed to Fetch
**Symptom**: Console shows "Network Error" or "Failed to fetch"
**Fix**: 
- Verify backend URL is correct and accessible
- Check if backend requires HTTPS (Vercel always uses HTTPS)
- Test backend URL directly in browser

#### Issue: Page stays on signup, no error shown
**Symptom**: Click submit, nothing happens, page doesn't change
**Possible causes**:
1. JavaScript error preventing form submission
2. API request failing silently
3. Network timeout
**Fix**: Check console for errors, check Network tab for failed requests

## Testing Locally

To verify the changes work locally:

```bash
# In terminal 1: Backend
cd /Users/PalusS0502/Documents/hackathon/ERNIE
source venv/bin/activate
DISABLE_MODEL_SOURCE_CHECK=True uvicorn backend.app:app --reload --port 8000

# In terminal 2: Frontend
cd /Users/PalusS0502/Documents/hackathon/ERNIE/frontend
npm run dev
```

Then visit http://localhost:3000/signup and try to sign up.

## Backend Requirements

The backend registration endpoint should:
- Accept POST request to `/api/auth/register`
- Accept JSON body with: `{ email, password, first_name, last_name, phone? }`
- Return: `{ access_token, refresh_token, user }`
- Status code: 200 or 201 for success

## Next Steps

1. Deploy these changes to Vercel (commit and push)
2. Wait for Vercel to rebuild (usually 1-2 minutes)
3. Open signup page and check browser console
4. Try to sign up and observe the logs
5. Report back what you see in the console/network tabs

## Quick Verification Checklist

- [ ] Vercel environment variable `NEXT_PUBLIC_API_URL` is set
- [ ] Environment variable includes the full URL (https://...)
- [ ] Environment variable does NOT have trailing slash
- [ ] Backend is deployed and accessible
- [ ] Backend CORS allows your Vercel domain
- [ ] Code is committed and pushed to trigger Vercel rebuild
- [ ] Vercel deployment completed successfully
- [ ] Browser console shows correct API URL
- [ ] Network tab shows registration request being sent

## Contact Information

If you're still having issues after checking all the above:
1. Share the console logs (screenshot or copy text)
2. Share the network request details
3. Share the API URL you're using
4. Share any error messages shown on the page

