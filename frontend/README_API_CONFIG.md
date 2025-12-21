# Frontend API Configuration

## Issue: Frontend calling localhost:3000 instead of localhost:8000

The frontend was using relative URLs (`/api/claims`) which Next.js rewrites were supposed to proxy to the backend, but this wasn't working reliably.

## Solution

All API calls now use the full backend URL directly:
- `http://localhost:8000/api/claims` instead of `/api/claims`

## Configuration

### Environment Variable

Create or update `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Code Changes

All API calls now use:
```typescript
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
fetch(`${apiUrl}/api/claims`)
```

## Updated Files

- `src/pages/index.tsx` - Dashboard page
- `src/pages/claims.tsx` - Claims list page
- `src/pages/analytics.tsx` - Analytics page
- `src/components/ClaimUpload.tsx` - Upload component
- `src/components/ClaimList.tsx` - List component
- `src/components/ClaimAnalytics.tsx` - Analytics component
- `src/components/NaturalLanguageQuery.tsx` - Query component

## Restart Frontend

After these changes, **restart your frontend server**:

```bash
# Stop current server (Ctrl+C)
cd frontend
npm run dev
```

## For Production

Update `.env.local` or set environment variable:

```bash
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

## Alternative: Using API Utility

You can also use the centralized API utility:

```typescript
import { apiUrl } from '@/utils/api';

fetch(apiUrl('api/claims'))
```

