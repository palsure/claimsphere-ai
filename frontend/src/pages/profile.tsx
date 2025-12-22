import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { useAuth } from '@/contexts/AuthContext';
import styles from '@/styles/Profile.module.css';

interface UserStats {
  total_claims: number;
  approved_claims: number;
  pending_claims: number;
  denied_claims: number;
  total_amount: number;
}

export default function ProfilePage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useAuth();
  
  const [isEditing, setIsEditing] = useState(false);
  const [editedName, setEditedName] = useState('');
  const [stats, setStats] = useState<UserStats | null>(null);
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [passwordData, setPasswordData] = useState({
    current: '',
    new: '',
    confirm: ''
  });
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [loading, setLoading] = useState(false);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  // Set initial name when user loads
  useEffect(() => {
    if (user) {
      // Use computed name or construct from first/last name
      let defaultName = user.name || `${user.first_name} ${user.last_name}`.trim();
      if (!defaultName) {
        // Set a default name based on role if not set
        switch (user.role?.toLowerCase()) {
          case 'admin':
            defaultName = 'System Administrator';
            break;
          case 'agent':
            defaultName = 'Claims Agent';
            break;
          default:
            defaultName = 'User';
        }
      }
      setEditedName(defaultName);
      // Fetch user stats
      fetchUserStats();
    }
  }, [user]);

  const fetchUserStats = async () => {
    try {
      // Mock stats for now - in production, fetch from API
      setStats({
        total_claims: 12,
        approved_claims: 8,
        pending_claims: 3,
        denied_claims: 1,
        total_amount: 4850.00
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleSaveProfile = async () => {
    setLoading(true);
    setMessage(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // In production, call your API to update user profile
      // await api.updateProfile({ full_name: editedName });
      
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      setIsEditing(false);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to update profile' });
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwordData.new !== passwordData.confirm) {
      setMessage({ type: 'error', text: 'New passwords do not match' });
      return;
    }

    if (passwordData.new.length < 8) {
      setMessage({ type: 'error', text: 'Password must be at least 8 characters' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // In production, call your API to change password
      // await api.changePassword(passwordData);
      
      setMessage({ type: 'success', text: 'Password changed successfully!' });
      setShowPasswordChange(false);
      setPasswordData({ current: '', new: '', confirm: '' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to change password' });
    } finally {
      setLoading(false);
    }
  };

  if (isLoading || !user) {
    return (
      <main className={styles.main}>
        <div className={styles.container}>
          <div className={styles.loadingState}>
            <div className={styles.spinner}></div>
            <p>Loading profile...</p>
          </div>
        </div>
      </main>
    );
  }

  const getRoleBadgeClass = (role: string) => {
    switch (role?.toLowerCase()) {
      case 'admin':
        return styles.roleAdmin;
      case 'agent':
        return styles.roleAgent;
      default:
        return styles.roleUser;
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role?.toLowerCase()) {
      case 'admin':
        return '👑';
      case 'agent':
        return '🎯';
      default:
        return '👤';
    }
  };

  return (
    <>
      <Head>
        <title>My Profile | ClaimSphere AI</title>
        <meta name="description" content="Manage your profile and settings" />
      </Head>

      <main className={styles.main}>
        <div className={styles.container}>
          {/* Header */}
          <div className={styles.header}>
            <h1 className={styles.title}>
              <span>👤</span>
              My Profile
            </h1>
            <p className={styles.subtitle}>
              Manage your account information and settings
            </p>
          </div>

          {/* Message */}
          {message && (
            <div className={`${styles.message} ${message.type === 'error' ? styles.messageError : styles.messageSuccess}`}>
              <span>{message.type === 'success' ? '✓' : '⚠'}</span>
              {message.text}
            </div>
          )}

          <div className={styles.content}>
            {/* Profile Card */}
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <h2>
                  <span>ℹ️</span>
                  Profile Information
                </h2>
                {!isEditing && (
                  <button
                    onClick={() => setIsEditing(true)}
                    className={styles.editButton}
                  >
                    ✏️ Edit
                  </button>
                )}
              </div>

              <div className={styles.cardBody}>
                <div className={styles.profileFields}>
                  <div className={styles.field}>
                    <label>Full Name</label>
                    {isEditing ? (
                      <input
                        type="text"
                        value={editedName}
                        onChange={(e) => setEditedName(e.target.value)}
                        className={styles.input}
                      />
                    ) : (
                      <p>{user.name || `${user.first_name} ${user.last_name}`.trim() || 'Not set'}</p>
                    )}
                  </div>

                  <div className={styles.field}>
                    <label>Email Address</label>
                    <p>{user.email}</p>
                    <span className={styles.fieldNote}>Email cannot be changed</span>
                  </div>

                  <div className={styles.field}>
                    <label>Role</label>
                    <div>
                      <span className={`${styles.roleBadge} ${getRoleBadgeClass(user.role)}`}>
                        {getRoleIcon(user.role)} {user.role?.toUpperCase()}
                      </span>
                    </div>
                  </div>

                  <div className={styles.field}>
                    <label>Member Since</label>
                    <p>{new Date(user.created_at || Date.now()).toLocaleDateString('en-US', { 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric' 
                    })}</p>
                  </div>
                </div>

                {isEditing && (
                  <div className={styles.cardActions}>
                    <button
                      onClick={handleSaveProfile}
                      className={styles.saveButton}
                      disabled={loading}
                    >
                      {loading ? 'Saving...' : 'Save Changes'}
                    </button>
                    <button
                      onClick={() => {
                        setIsEditing(false);
                        setEditedName(user.name || `${user.first_name} ${user.last_name}`.trim() || user.email?.split('@')[0] || '');
                      }}
                      className={styles.cancelButton}
                      disabled={loading}
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Security Card */}
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <h2>
                  <span>🔒</span>
                  Security
                </h2>
              </div>

              <div className={styles.cardBody}>
                {!showPasswordChange ? (
                  <>
                    <p className={styles.cardDescription}>
                      Keep your account secure by using a strong password
                    </p>
                    <button
                      onClick={() => setShowPasswordChange(true)}
                      className={styles.changePasswordButton}
                    >
                      🔑 Change Password
                    </button>
                  </>
                ) : (
                  <form onSubmit={handleChangePassword} className={styles.passwordForm}>
                    <div className={styles.field}>
                      <label>Current Password</label>
                      <input
                        type="password"
                        value={passwordData.current}
                        onChange={(e) => setPasswordData({ ...passwordData, current: e.target.value })}
                        className={styles.input}
                        required
                      />
                    </div>

                    <div className={styles.field}>
                      <label>New Password</label>
                      <input
                        type="password"
                        value={passwordData.new}
                        onChange={(e) => setPasswordData({ ...passwordData, new: e.target.value })}
                        className={styles.input}
                        required
                        minLength={8}
                      />
                      <span className={styles.fieldNote}>Minimum 8 characters</span>
                    </div>

                    <div className={styles.field}>
                      <label>Confirm New Password</label>
                      <input
                        type="password"
                        value={passwordData.confirm}
                        onChange={(e) => setPasswordData({ ...passwordData, confirm: e.target.value })}
                        className={styles.input}
                        required
                      />
                    </div>

                    <div className={styles.cardActions}>
                      <button
                        type="submit"
                        className={styles.saveButton}
                        disabled={loading}
                      >
                        {loading ? 'Changing...' : 'Change Password'}
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setShowPasswordChange(false);
                          setPasswordData({ current: '', new: '', confirm: '' });
                        }}
                        className={styles.cancelButton}
                        disabled={loading}
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                )}
              </div>
            </div>

            {/* Close Account */}
            <div className={`${styles.card} ${styles.dangerCard}`}>
              <div className={styles.cardHeader}>
                <h2>
                  <span>🚪</span>
                  Close Account
                </h2>
              </div>

              <div className={styles.cardBody}>
                <div className={styles.dangerItem}>
                  <div>
                    <h4>Delete Account</h4>
                    <p>Permanently delete your account and all associated data</p>
                  </div>
                  <button
                    className={styles.dangerButton}
                    onClick={() => alert('Account deletion feature coming soon. Please contact support.')}
                  >
                    Delete Account
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}

