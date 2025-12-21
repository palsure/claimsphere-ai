// Centralized API configuration
// NEXT_PUBLIC_API_URL must be set in environment variables
if (!process.env.NEXT_PUBLIC_API_URL) {
  throw new Error(
    'NEXT_PUBLIC_API_URL environment variable is not set. ' +
    'Please create a .env.local file in the frontend directory with: ' +
    'NEXT_PUBLIC_API_URL=http://localhost:8000 (for local development) or ' +
    'your deployed backend URL (for production)'
  );
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export const apiUrl = (path: string): string => {
  // Remove leading slash if present
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return `${API_BASE_URL}/${cleanPath}`;
};

// Axios instance with base URL
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// For file uploads
export const apiClientMultipart = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

