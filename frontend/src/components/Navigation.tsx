import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '@/contexts/AuthContext';
import Logo from './Logo';
import styles from './Navigation.module.css';

export default function Navigation() {
  const router = useRouter();
  const { user, isAuthenticated, logout, isAgent, isAdmin, hasAnyRole } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
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
  // Check if user can access management panel (agents have full admin capabilities)
  const canAccessManagement = hasAnyRole(['agent', 'admin']);

  return (
    <nav className={styles.nav}>
      <div className={styles.container}>
        <Link href="/" className={styles.logo}>
          <Logo size="small" />
          <span className={styles.logoText}>ClaimSphere</span>
          <span className={styles.aiTag}>AI</span>
        </Link>

        {isAuthenticated && (
          <div className={styles.navLinks}>
            <Link
              href="/"
              className={`${styles.navLink} ${router.pathname === '/' ? styles.active : ''}`}
            >
              <span>📊</span>
              Dashboard
            </Link>
            <Link
              href="/claims"
              className={`${styles.navLink} ${router.pathname.startsWith('/claims') ? styles.active : ''}`}
            >
              <span>📋</span>
              Claims
            </Link>
            {canAccessQueue && (
              <Link
                href="/dashboard/queue"
                className={`${styles.navLink} ${router.pathname === '/dashboard/queue' ? styles.active : ''}`}
              >
                <span>📥</span>
                Queue
              </Link>
            )}
            <Link
              href="/analytics"
              className={`${styles.navLink} ${router.pathname === '/analytics' ? styles.active : ''}`}
            >
              <span>📈</span>
              Analytics
            </Link>
            {canAccessManagement && (
              <Link
                href="/dashboard/admin"
                className={`${styles.navLink} ${router.pathname.startsWith('/dashboard/admin') ? styles.active : ''}`}
              >
                <span>⚙️</span>
                Management
              </Link>
            )}
          </div>
        )}

        <div className={styles.rightSection}>
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
                  <Link href="/settings" className={styles.dropdownItem}>
                    <span>⚙️</span>
                    Preferences
                  </Link>
                  <Link href="/help" className={styles.dropdownItem}>
                    <span>❓</span>
                    Help & Support
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
              <Link href="/" className={styles.mobileNavLink}>
                <span>📊</span> Dashboard
              </Link>
              <Link href="/claims" className={styles.mobileNavLink}>
                <span>📋</span> Claims
              </Link>
              {canAccessQueue && (
                <Link href="/dashboard/queue" className={styles.mobileNavLink}>
                  <span>📥</span> Queue
                </Link>
              )}
              <Link href="/analytics" className={styles.mobileNavLink}>
                <span>📈</span> Analytics
              </Link>
              {canAccessManagement && (
                <Link href="/dashboard/admin" className={styles.mobileNavLink}>
                  <span>⚙️</span> Management
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
