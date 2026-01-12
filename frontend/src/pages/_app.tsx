import type { AppProps } from 'next/app';
import { useRouter } from 'next/router';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import '../styles/globals.css';
import { useEffect } from 'react';

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  
  const publicRoutes = ['/login', '/signup', '/forgot-password', '/', '/about'];
  const isPublicRoute = publicRoutes.includes(router.pathname);

  useEffect(() => {
    if (!isLoading && !isAuthenticated && !isPublicRoute) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, isPublicRoute, router]);

  if (isLoading) {
    return (
      <div className="loading" style={{ minHeight: '100vh' }}>
        <div className="spinner" />
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated && !isPublicRoute) {
    return null;
  }

  return <>{children}</>;
}

function AppContent({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const publicRoutes = ['/login', '/signup', '/forgot-password', '/', '/about'];
  const isPublicRoute = publicRoutes.includes(router.pathname);

  // Show navigation for all routes except login/signup
  const showNav = !['/login', '/signup', '/forgot-password'].includes(router.pathname);
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {showNav && <Navigation />}
      <main style={{ flex: 1 }}>
        <ProtectedRoute>
          <Component {...pageProps} />
        </ProtectedRoute>
      </main>
      {showNav && <Footer />}
    </div>
  );
}

export default function App(props: AppProps) {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent {...props} />
      </AuthProvider>
    </ThemeProvider>
  );
}
