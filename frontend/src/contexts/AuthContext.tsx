/**
 * Authentication Context with Backend API Integration
 * Provides JWT-based auth with RBAC support
 */
import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { authAPI } from '@/utils/api';

// Role types matching backend
export type RoleType = 'user' | 'agent' | 'admin';

// User interface matching backend response
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  is_active: boolean;
  is_verified: boolean;
  roles: RoleType[];
  created_at: string;
  last_login?: string;
  // Computed properties added by AuthContext
  name?: string;
  role?: RoleType;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  hasRole: (role: RoleType) => boolean;
  hasAnyRole: (roles: RoleType[]) => boolean;
  isUser: boolean;
  isAgent: boolean;
  isAdmin: boolean;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Storage keys
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_KEY = 'user';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check for existing session on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem(ACCESS_TOKEN_KEY);
      const storedUser = localStorage.getItem(USER_KEY);
      
      if (token && storedUser) {
        try {
          // Verify token is still valid by calling /me endpoint
          const userData = await authAPI.getMe();
          setUser(userData);
          localStorage.setItem(USER_KEY, JSON.stringify(userData));
        } catch (err) {
          // Token invalid, clear storage
          localStorage.removeItem(ACCESS_TOKEN_KEY);
          localStorage.removeItem(REFRESH_TOKEN_KEY);
          localStorage.removeItem(USER_KEY);
        }
      }
      
      setIsLoading(false);
    };

    initAuth();
  }, []);

  // Login with backend API
  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await authAPI.login(email, password);
      
      // Store tokens
      localStorage.setItem(ACCESS_TOKEN_KEY, response.access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, response.refresh_token);
      localStorage.setItem(USER_KEY, JSON.stringify(response.user));
      
      setUser(response.user);
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Login failed';
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Signup with backend API
  const signup = useCallback(async (name: string, email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Split name into first and last
      const nameParts = name.trim().split(' ');
      const first_name = nameParts[0] || '';
      const last_name = nameParts.slice(1).join(' ') || '';
      
      const response = await authAPI.register({
        email,
        password,
        first_name,
        last_name,
      });
      
      // Store tokens
      localStorage.setItem(ACCESS_TOKEN_KEY, response.access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, response.refresh_token);
      localStorage.setItem(USER_KEY, JSON.stringify(response.user));
      
      setUser(response.user);
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Registration failed';
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Logout
  const logout = useCallback(() => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setUser(null);
    setError(null);
  }, []);

  // Clear error
  const clearError = useCallback(() => setError(null), []);

  // Refresh user data from backend
  const refreshUser = useCallback(async () => {
    try {
      const userData = await authAPI.getMe();
      setUser(userData);
      localStorage.setItem(USER_KEY, JSON.stringify(userData));
    } catch (err) {
      logout();
    }
  }, [logout]);

  // Role checking helpers
  const hasRole = useCallback((role: RoleType): boolean => {
    return user?.roles?.includes(role) ?? false;
  }, [user]);

  const hasAnyRole = useCallback((roles: RoleType[]): boolean => {
    return roles.some(role => user?.roles?.includes(role));
  }, [user]);

  // Convenience role checks
  const isUser = user?.roles?.includes('user') ?? false;
  const isAgent = user?.roles?.includes('agent') ?? false;
  const isAdmin = user?.roles?.includes('admin') ?? false;

  // Computed display name for backwards compatibility
  const userWithName = user ? {
    ...user,
    name: `${user.first_name} ${user.last_name}`.trim(),
    role: user.roles[0] || 'user', // Primary role for display
  } : null;

  return (
    <AuthContext.Provider
      value={{
        user: userWithName as User | null,
        isLoading,
        isAuthenticated: !!user,
        error,
        login,
        signup,
        logout,
        clearError,
        hasRole,
        hasAnyRole,
        isUser,
        isAgent,
        isAdmin,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
