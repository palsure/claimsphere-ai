/**
 * Dashboard layout component with role-based navigation
 */
import React, { ReactNode } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth, RoleType } from '../contexts/AuthContext';
import styles from './DashboardLayout.module.css';

interface NavItem {
  label: string;
  href: string;
  icon: string;
  roles?: RoleType[];
}

const navItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: '📊' },
  { label: 'My Claims', href: '/dashboard/claims', icon: '📋', roles: ['user'] },
  { label: 'Submit Claim', href: '/dashboard/claims/new', icon: '➕', roles: ['user'] },
  { label: 'Review Queue', href: '/dashboard/queue', icon: '📥', roles: ['agent', 'admin'] },
  { label: 'All Claims', href: '/dashboard/all-claims', icon: '📁', roles: ['agent', 'admin'] },
  { label: 'Users', href: '/dashboard/users', icon: '👥', roles: ['admin'] },
  { label: 'Plans', href: '/dashboard/plans', icon: '📑', roles: ['admin'] },
  { label: 'Rules', href: '/dashboard/rules', icon: '⚙️', roles: ['admin'] },
  { label: 'Analytics', href: '/dashboard/analytics', icon: '📈', roles: ['admin'] },
  { label: 'Ask AI', href: '/dashboard/query', icon: '🤖' },
];

interface DashboardLayoutProps {
  children: ReactNode;
  title?: string;
}

export default function DashboardLayout({ children, title }: DashboardLayoutProps) {
  const { user, logout, hasAnyRole } = useAuth();
  const router = useRouter();

  const filteredNavItems = navItems.filter(item => {
    if (!item.roles) return true;
    return hasAnyRole(item.roles);
  });

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const getRoleBadge = () => {
    if (!user) return null;
    
    if (user.roles.includes('admin')) {
      return <span className={styles.roleBadgeAdmin}>Admin</span>;
    }
    if (user.roles.includes('agent')) {
      return <span className={styles.roleBadgeAgent}>Agent</span>;
    }
    return <span className={styles.roleBadgeUser}>User</span>;
  };

  return (
    <div className={styles.container}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>🏥</span>
          <span className={styles.logoText}>ClaimSphere</span>
        </div>
        
        <nav className={styles.nav}>
          {filteredNavItems.map(item => (
            <Link
              key={item.href}
              href={item.href}
              className={`${styles.navItem} ${router.pathname === item.href ? styles.active : ''}`}
            >
              <span className={styles.navIcon}>{item.icon}</span>
              <span className={styles.navLabel}>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className={styles.userSection}>
          <div className={styles.userInfo}>
            <div className={styles.userAvatar}>
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </div>
            <div className={styles.userDetails}>
              <span className={styles.userName}>
                {user?.first_name} {user?.last_name}
              </span>
              {getRoleBadge()}
            </div>
          </div>
          <button onClick={handleLogout} className={styles.logoutButton}>
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className={styles.main}>
        {title && (
          <header className={styles.header}>
            <h1 className={styles.title}>{title}</h1>
          </header>
        )}
        <div className={styles.content}>
          {children}
        </div>
      </main>
    </div>
  );
}

