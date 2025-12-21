import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: 'user' | 'admin' | 'reviewer';
  createdAt: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Simulated user database (in production, this would be backend API calls)
const USERS_STORAGE_KEY = 'claimsphere_users';
const SESSION_KEY = 'claimsphere_session';

// Demo users for testing
const DEMO_USERS: Record<string, { user: User; password: string }> = {
  'demo@claimsphere.ai': {
    user: {
      id: 'demo_001',
      email: 'demo@claimsphere.ai',
      name: 'Demo User',
      role: 'user',
      createdAt: '2024-01-01T00:00:00.000Z',
    },
    password: 'demo123',
  },
  'admin@claimsphere.ai': {
    user: {
      id: 'admin_001',
      email: 'admin@claimsphere.ai',
      name: 'Admin User',
      role: 'admin',
      createdAt: '2024-01-01T00:00:00.000Z',
    },
    password: 'admin123',
  },
  'reviewer@claimsphere.ai': {
    user: {
      id: 'reviewer_001',
      email: 'reviewer@claimsphere.ai',
      name: 'Claims Reviewer',
      role: 'reviewer',
      createdAt: '2024-01-01T00:00:00.000Z',
    },
    password: 'reviewer123',
  },
};

const initializeDemoUsers = () => {
  if (typeof window === 'undefined') return;
  const stored = localStorage.getItem(USERS_STORAGE_KEY);
  if (!stored) {
    localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(DEMO_USERS));
  } else {
    // Merge demo users with existing users (demo users take precedence for consistency)
    const existingUsers = JSON.parse(stored);
    const mergedUsers = { ...existingUsers, ...DEMO_USERS };
    localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(mergedUsers));
  }
};

const getStoredUsers = (): Record<string, { user: User; password: string }> => {
  if (typeof window === 'undefined') return {};
  initializeDemoUsers(); // Ensure demo users exist
  const stored = localStorage.getItem(USERS_STORAGE_KEY);
  return stored ? JSON.parse(stored) : {};
};

const saveUsers = (users: Record<string, { user: User; password: string }>) => {
  localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(users));
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check for existing session
    const checkSession = () => {
      const session = localStorage.getItem(SESSION_KEY);
      if (session) {
        try {
          const userData = JSON.parse(session);
          setUser(userData);
        } catch {
          localStorage.removeItem(SESSION_KEY);
        }
      }
      setIsLoading(false);
    };
    
    checkSession();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800));
    
    try {
      const users = getStoredUsers();
      const userRecord = users[email.toLowerCase()];
      
      if (!userRecord) {
        throw new Error('No account found with this email');
      }
      
      if (userRecord.password !== password) {
        throw new Error('Incorrect password');
      }
      
      setUser(userRecord.user);
      localStorage.setItem(SESSION_KEY, JSON.stringify(userRecord.user));
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (name: string, email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800));
    
    try {
      const users = getStoredUsers();
      const emailLower = email.toLowerCase();
      
      if (users[emailLower]) {
        throw new Error('An account with this email already exists');
      }
      
      if (password.length < 6) {
        throw new Error('Password must be at least 6 characters');
      }
      
      const newUser: User = {
        id: `user_${Date.now()}`,
        email: emailLower,
        name,
        role: 'user',
        createdAt: new Date().toISOString(),
      };
      
      users[emailLower] = { user: newUser, password };
      saveUsers(users);
      
      setUser(newUser);
      localStorage.setItem(SESSION_KEY, JSON.stringify(newUser));
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem(SESSION_KEY);
  };

  const clearError = () => setError(null);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        signup,
        logout,
        error,
        clearError,
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

