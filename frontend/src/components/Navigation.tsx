import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '@/contexts/AuthContext';
import Logo from './Logo';
import ThemeToggle from './ThemeToggle';
import styles from './Navigation.module.css';

export default function Navigation() {
  const router = useRouter();
  const { user, isAuthenticated, logout, isAgent, isAdmin, hasAnyRole, login, isLoading } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [isDemoLoggingIn, setIsDemoLoggingIn] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const handleDemoLogin = async () => {
    setIsDemoLoggingIn(true);
    try {
      // Use default demo user credentials
      await login('user@example.com', 'password123');
      // Redirect to dashboard after successful login
      router.push('/dashboard');
    } catch (err) {
      console.error('Demo login failed:', err);
      // On error, still redirect to login page where user can see the error
      router.push('/login');
    } finally {
      setIsDemoLoggingIn(false);
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  // Get display name from user
  const displayName = user ? `${user.first_name} ${user.last_name}`.trim() : '';
  const primaryRole = user?.roles?.[0] || 'user';
  const roleLabel = primaryRole.charAt(0).toUpperCase() + primaryRole.slice(1);

  // Check if user can access queue (agents and admins)
  const canAccessQueue = hasAnyRole(['agent', 'admin']);
  // Check if user can access management panel (admins only)
  const canAccessManagement = hasAnyRole(['admin']);

  return (
    <nav className={styles.nav}>
      <div className={styles.container}>
        <Link href="/" className={styles.logo}>
          <Logo size="medium" />
          <div className={styles.logoTextContainer}>
            <div className={styles.logoTitleRow}>
              <span className={styles.logoText}>ClaimSphere</span>
              <span className={styles.aiTag}>AI</span>
            </div>
            <span className={styles.challengeTag}>ERNIE AI Developer Challenge</span>
          </div>
        </Link>

        {isAuthenticated && (
          <div className={styles.navLinks}>
            <Link
              href="/"
              className={`${styles.navLink} ${(router.pathname === '/' || router.pathname === '/about') ? styles.active : ''}`}
            >
              <span>ℹ️</span>
              About
              {(router.pathname === '/' || router.pathname === '/about') && (
                <span className={styles.activeArrow}>▼</span>
              )}
            </Link>
            <Link
              href="/dashboard"
              className={`${styles.navLink} ${router.pathname === '/dashboard' ? styles.active : ''}`}
            >
              <span>📊</span>
              Dashboard
              {router.pathname === '/dashboard' && (
                <span className={styles.activeArrow}>▼</span>
              )}
            </Link>
            <Link
              href="/claims"
              className={`${styles.navLink} ${router.pathname.startsWith('/claims') ? styles.active : ''}`}
            >
              <span>📋</span>
              Claims
              {router.pathname.startsWith('/claims') && (
                <span className={styles.activeArrow}>▼</span>
              )}
            </Link>
            {canAccessQueue && (
              <Link
                href="/dashboard/queue"
                className={`${styles.navLink} ${router.pathname === '/dashboard/queue' ? styles.active : ''}`}
              >
                <span>📥</span>
                Queue
                {router.pathname === '/dashboard/queue' && (
                  <span className={styles.activeArrow}>▼</span>
                )}
              </Link>
            )}
            <Link
              href="/analytics"
              className={`${styles.navLink} ${router.pathname === '/analytics' ? styles.active : ''}`}
            >
              <span>📈</span>
              Analytics
              {router.pathname === '/analytics' && (
                <span className={styles.activeArrow}>▼</span>
              )}
            </Link>
            <Link
              href="/ai-assistant"
              className={`${styles.navLink} ${router.pathname === '/ai-assistant' ? styles.active : ''}`}
            >
              <span>💬</span>
              <span className={styles.navLinkText}>Ask AI</span>
              {router.pathname === '/ai-assistant' && (
                <span className={styles.activeArrow}>▼</span>
              )}
            </Link>
            <Link
              href="/help"
              className={`${styles.navLink} ${router.pathname === '/help' ? styles.active : ''}`}
            >
              <span>🎧</span>
              Support
              {router.pathname === '/help' && (
                <span className={styles.activeArrow}>▼</span>
              )}
            </Link>
            {canAccessManagement && (
              <Link
                href="/dashboard/admin"
                className={`${styles.navLink} ${router.pathname.startsWith('/dashboard/admin') ? styles.active : ''}`}
              >
                <span>⚙️</span>
                Management
                {router.pathname.startsWith('/dashboard/admin') && (
                  <span className={styles.activeArrow}>▼</span>
                )}
              </Link>
            )}
          </div>
        )}

        <div className={styles.rightSection}>
          <ThemeToggle />
          {isAuthenticated ? (
            <div className={styles.userSection} ref={dropdownRef}>
              <button
                className={styles.notificationBtn}
                title="Notifications"
              >
                <span>🔔</span>
                <span className={styles.notificationBadge}>3</span>
              </button>

              <button
                className={styles.userButton}
                onClick={() => setShowDropdown(!showDropdown)}
              >
                <div className={styles.avatar}>
                  <span>{getInitials(displayName || 'U')}</span>
                </div>
                <div className={styles.userInfo}>
                  <span className={styles.userName}>{displayName}</span>
                  <span className={styles.userRole}>{roleLabel}</span>
                </div>
                <span className={styles.dropdownArrow}>▼</span>
              </button>

              {showDropdown && (
                <div className={styles.dropdown}>
                  <div className={styles.dropdownHeader}>
                    <div className={styles.dropdownAvatar}>
                      <span>{getInitials(displayName || 'U')}</span>
                    </div>
                    <div>
                      <div className={styles.dropdownName}>{displayName}</div>
                      <div className={styles.dropdownEmail}>{user?.email}</div>
                    </div>
                  </div>
                  
                  <div className={styles.dropdownDivider} />
                  
                  <div className={styles.dropdownRoleBadge}>
                    <span className={styles.roleBadge}>{roleLabel}</span>
                  </div>
                  
                  <div className={styles.dropdownDivider} />
                  
                  <Link href="/profile" className={styles.dropdownItem}>
                    <span>👤</span>
                    Profile Settings
                  </Link>
                  
                  <div className={styles.dropdownDivider} />
                  
                  <button
                    className={styles.dropdownItem}
                    onClick={handleLogout}
                  >
                    <span>🚪</span>
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className={styles.authButtons}>
              <Link href="/login" className={styles.loginBtn}>
                Sign In
              </Link>
              <button
                onClick={handleDemoLogin}
                disabled={isDemoLoggingIn || isLoading}
                className={styles.demoLoginBtn}
                title="Try the app with demo account"
              >
                {isDemoLoggingIn ? (
                  <>
                    <span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />
                    Logging in...
                  </>
                ) : (
                  <>
                    🚀 Demo Login
                  </>
                )}
              </button>
              <Link href="/signup" className={styles.signupBtn}>
                Get Started
              </Link>
            </div>
          )}

          <button
            className={styles.mobileMenuBtn}
            onClick={() => setShowMobileMenu(!showMobileMenu)}
          >
            {showMobileMenu ? '✕' : '☰'}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {showMobileMenu && (
        <div className={styles.mobileMenu}>
          {isAuthenticated ? (
            <>
              <Link 
                href="/" 
                className={`${styles.mobileNavLink} ${(router.pathname === '/' || router.pathname === '/about') ? styles.active : ''}`}
              >
                <span>ℹ️</span> About
                {(router.pathname === '/' || router.pathname === '/about') && (
                  <span className={styles.activeArrow}>▼</span>
                )}
              </Link>
              <Link 
                href="/dashboard" 
                className={`${styles.mobileNavLink} ${router.pathname === '/dashboard' ? styles.active : ''}`}
              >
                <span>📊</span> Dashboard
                {router.pathname === '/dashboard' && (
                  <span className={styles.activeArrow}>▼</span>
                )}
              </Link>
              <Link 
                href="/claims" 
                className={`${styles.mobileNavLink} ${router.pathname.startsWith('/claims') ? styles.active : ''}`}
              >
                <span>📋</span> Claims
                {router.pathname.startsWith('/claims') && (
                  <span className={styles.activeArrow}>▼</span>
                )}
              </Link>
              {canAccessQueue && (
                <Link 
                  href="/dashboard/queue" 
                  className={`${styles.mobileNavLink} ${router.pathname === '/dashboard/queue' ? styles.active : ''}`}
                >
                  <span>📥</span> Queue
                  {router.pathname === '/dashboard/queue' && (
                    <span className={styles.activeArrow}>▼</span>
                  )}
                </Link>
              )}
              <Link 
                href="/analytics" 
                className={`${styles.mobileNavLink} ${router.pathname === '/analytics' ? styles.active : ''}`}
              >
                <span>📈</span> Analytics
                {router.pathname === '/analytics' && (
                  <span className={styles.activeArrow}>▼</span>
                )}
              </Link>
              <Link 
                href="/ai-assistant" 
                className={`${styles.mobileNavLink} ${router.pathname === '/ai-assistant' ? styles.active : ''}`}
              >
                <span>💬</span> Ask AI
                {router.pathname === '/ai-assistant' && (
                  <span className={styles.activeArrow}>▼</span>
                )}
              </Link>
              <Link 
                href="/help" 
                className={`${styles.mobileNavLink} ${router.pathname === '/help' ? styles.active : ''}`}
              >
                <span>🎧</span> Support
                {router.pathname === '/help' && (
                  <span className={styles.activeArrow}>▼</span>
                )}
              </Link>
              {canAccessManagement && (
                <Link 
                  href="/dashboard/admin" 
                  className={`${styles.mobileNavLink} ${router.pathname.startsWith('/dashboard/admin') ? styles.active : ''}`}
                >
                  <span>⚙️</span> Management
                  {router.pathname.startsWith('/dashboard/admin') && (
                    <span className={styles.activeArrow}>▼</span>
                  )}
                </Link>
              )}
              <div className={styles.mobileDivider} />
              <Link href="/profile" className={styles.mobileNavLink}>
                <span>👤</span> Profile
              </Link>
              <button className={styles.mobileNavLink} onClick={handleLogout}>
                <span>🚪</span> Sign Out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className={styles.mobileNavLink}>
                Sign In
              </Link>
              <button
                onClick={handleDemoLogin}
                disabled={isDemoLoggingIn || isLoading}
                className={styles.mobileNavLink}
              >
                {isDemoLoggingIn ? (
                  <>
                    <span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />
                    Logging in...
                  </>
                ) : (
                  <>
                    🚀 Demo Login
                  </>
                )}
              </button>
              <Link href="/signup" className={styles.mobileNavLink}>
                Get Started
              </Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
}
