import { useState, useEffect, useCallback } from 'react';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from '../firebase';

/**
 * useAuth hook - manages Firebase authentication state
 * 
 * Usage:
 * const { user, loading, logout } = useAuth();
 * 
 * Returns:
 * - user: Current user object or null
 * - loading: Whether auth state is being checked
 * - logout: Function to sign out user
 */
const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    try {
      // Check if auth object is a mock (Firebase failed to initialize)
      if (auth._isMock) {
        console.warn('⚠️ Using mock auth - Firebase not initialized properly');
        setLoading(false);
        return;
      }

      // Set a timeout to prevent infinite loading
      const timeoutId = setTimeout(() => {
        console.warn('⚠️ Auth state check timed out - proceeding without auth');
        setLoading(false);
      }, 5000);

      // Listen to auth state changes
      const unsubscribe = onAuthStateChanged(
        auth,
        async (currentUser) => {
          clearTimeout(timeoutId);
          try {
            if (currentUser) {
              // User is logged in
              const idToken = await currentUser.getIdToken();
              setUser({
                uid: currentUser.uid,
                email: currentUser.email,
                displayName: currentUser.displayName,
                emailVerified: currentUser.emailVerified,
                photoURL: currentUser.photoURL,
                metadata: {
                  creationTime: currentUser.metadata?.creationTime,
                  lastSignInTime: currentUser.metadata?.lastSignInTime,
                },
                idToken,
              });
              
              // Store token for API requests
              localStorage.setItem('token', idToken);
              localStorage.setItem('user_id', currentUser.uid);
              localStorage.setItem('user_email', currentUser.email);
            } else {
              // User is logged out
              setUser(null);
              localStorage.removeItem('token');
              localStorage.removeItem('user_id');
              localStorage.removeItem('user_email');
            }
          } catch (err) {
            console.error('Auth state change error:', err);
            setError(err.message);
          } finally {
            setLoading(false);
          }
        },
        (err) => {
          clearTimeout(timeoutId);
          console.error('Auth listener error:', err);
          setError(err.message);
          setLoading(false);
        }
      );

      // Cleanup subscription and timeout
      return () => {
        unsubscribe();
        clearTimeout(timeoutId);
      };
    } catch (err) {
      console.error('useAuth initialization error:', err);
      setError(err.message);
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await signOut(auth);
      setUser(null);
      localStorage.removeItem('token');
      localStorage.removeItem('user_id');
      localStorage.removeItem('user_email');
      console.log('✅ Logout successful');
    } catch (err) {
      console.error('Logout error:', err);
      setError(err.message);
    }
  }, []);

  return {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    logout,
  };
};

export default useAuth;
export { useAuth };
