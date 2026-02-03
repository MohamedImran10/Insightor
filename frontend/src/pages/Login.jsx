import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { signInWithEmailAndPassword, signInWithPopup, sendPasswordResetEmail, fetchSignInMethodsForEmail, getAdditionalUserInfo } from 'firebase/auth';
import { auth, googleProvider } from '../firebase';
import { motion } from 'framer-motion';
import { LogIn, Loader, Eye, EyeOff } from 'lucide-react';
import { useToast } from '../hooks/useToast.jsx';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);

  const navigate = useNavigate();
  const { success, error: showError } = useToast();

  // Force light mode on auth pages
  useEffect(() => {
    // Remove dark mode when entering login page
    document.documentElement.classList.remove('dark');
    document.body.classList.remove('dark');
    
    return () => {
      // Don't restore dark mode - let theme context handle it
      // This ensures light theme persists during auth flow
    };
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // First, check if the email is registered
      const signInMethods = await fetchSignInMethodsForEmail(auth, email);
      
      if (signInMethods.length === 0) {
        // Email is not registered
        success('This email is not registered. Please sign up to create an account!');
        setTimeout(() => {
          navigate('/signup');
        }, 2000);
        return;
      }

      // Sign in with Firebase
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      // Get ID token
      const idToken = await user.getIdToken();

      // Store token in localStorage
      localStorage.setItem('token', idToken);
      localStorage.setItem('user_id', user.uid);
      localStorage.setItem('user_email', user.email);

      console.log('✅ Login successful:', user.email);
      success(`Welcome back, ${user.displayName || user.email}!`);

      // Redirect to home
      navigate('/');
    } catch (err) {
      console.error('Login error:', err);
      
      let errorMessage;
      switch (err.code) {
        case 'auth/wrong-password':
          errorMessage = 'Incorrect password. Please check your password and try again.';
          break;
        case 'auth/invalid-email':
          errorMessage = 'Invalid email address format.';
          break;
        case 'auth/user-disabled':
          errorMessage = 'This account has been disabled. Please contact support.';
          break;
        case 'auth/too-many-requests':
          errorMessage = 'Too many failed attempts. Please try again later.';
          break;
        case 'auth/network-request-failed':
          errorMessage = 'Network error. Please check your internet connection.';
          break;
        case 'auth/invalid-credential':
          errorMessage = 'Invalid email or password. Please check your credentials.';
          break;
        default:
          errorMessage = 'Login failed. Please try again.';
      }
      
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setLoading(true);
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const user = result.user;
      
      // Check if this is a new user or existing user
      const additionalUserInfo = getAdditionalUserInfo(result);
      const isNewUser = additionalUserInfo?.isNewUser;

      // Get ID token
      const idToken = await user.getIdToken();

      // Store token in localStorage
      localStorage.setItem('token', idToken);
      localStorage.setItem('user_id', user.uid);
      localStorage.setItem('user_email', user.email);

      console.log('✅ Google Sign-In successful:', user.email, isNewUser ? '(new user)' : '(existing user)');
      
      // Show different message for new vs existing users
      if (isNewUser) {
        success(`Welcome to Insightor, ${user.displayName || user.email}! Your account has been created.`);
      } else {
        success(`Welcome back, ${user.displayName || user.email}!`);
      }

      // Redirect to home
      navigate('/');
    } catch (err) {
      console.error('Google Sign-In error:', err);
      
      let errorMessage;
      switch (err.code) {
        case 'auth/popup-closed-by-user':
          errorMessage = 'Sign-in cancelled. Please try again.';
          break;
        case 'auth/popup-blocked':
          errorMessage = 'Popup blocked. Please allow popups and try again.';
          break;
        case 'auth/network-request-failed':
          errorMessage = 'Network error. Please check your internet connection.';
          break;
        default:
          errorMessage = 'Google Sign-In failed. Please try again.';
      }
      
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordReset = async () => {
    if (!email.trim()) {
      showError('Please enter your email address first');
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      showError('Please enter a valid email address');
      return;
    }

    setResetLoading(true);
    console.log('🔑 Attempting password reset for:', email);
    
    try {
      await sendPasswordResetEmail(auth, email.trim(), {
        url: window.location.origin + '/login',
        handleCodeInApp: false,
      });
      
      console.log('✅ Password reset email sent successfully');
      success('Password reset email sent! Check your inbox and spam folder. If you don\'t see it, add noreply@research-agent-b7cb0.firebaseapp.com to your contacts and try again.');
    } catch (err) {
      console.error('❌ Password reset error:', err);
      console.error('Error code:', err.code);
      console.error('Error message:', err.message);
      
      let errorMessage;
      switch (err.code) {
        case 'auth/user-not-found':
          errorMessage = 'No account found with this email address. Please check the email or sign up first.';
          break;
        case 'auth/invalid-email':
          errorMessage = 'Invalid email address format. Please enter a valid email.';
          break;
        case 'auth/network-request-failed':
          errorMessage = 'Network error. Please check your internet connection and try again.';
          break;
        case 'auth/too-many-requests':
          errorMessage = 'Too many requests. Please wait a few minutes before trying again.';
          break;
        case 'auth/missing-email':
          errorMessage = 'Email address is required.';
          break;
        default:
          errorMessage = `Failed to send password reset email: ${err.message}. Please try again or contact support.`;
      }
      
      showError(errorMessage);
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <motion.div
      className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4 relative overflow-hidden"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-70"
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            repeatType: "reverse"
          }}
        />
        <motion.div
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-70"
          animate={{
            scale: [1.2, 1, 1.2],
            rotate: [360, 180, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            repeatType: "reverse"
          }}
        />
        <motion.div
          className="absolute top-40 left-1/2 w-80 h-80 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-70"
          animate={{
            scale: [1, 1.3, 1],
            x: [-50, 50, -50],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            repeatType: "reverse"
          }}
        />
      </div>
      <motion.div
        className="w-full max-w-md bg-white/90 backdrop-blur-lg rounded-3xl shadow-2xl p-8 border border-white/20 relative z-10"
        initial={{ y: 50, opacity: 0, scale: 0.9 }}
        animate={{ y: 0, opacity: 1, scale: 1 }}
        transition={{ 
          delay: 0.2,
          type: "spring",
          stiffness: 100,
          damping: 15
        }}
        whileHover={{ y: -5 }}
        style={{
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.05)"
        }}
      >
        {/* Header */}
        <div className="text-center mb-6">
          {/* Insightor Logo/Brand */}
          <motion.div
            className="mb-4"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.8 }}
          >
            <motion.h1 
              className="text-4xl font-extrabold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent mb-2 leading-tight py-2"
              animate={{ 
                backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                repeatType: "reverse"
              }}
              style={{
                backgroundSize: "200% 200%",
                lineHeight: "1.2"
              }}
            >
              Insightor
            </motion.h1>
            <motion.p 
              className="text-sm text-gray-500 font-medium tracking-wide"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              Autonomous research, distilled into clarity.
            </motion.p>
          </motion.div>

          <motion.div
            className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500 rounded-2xl mb-4 shadow-xl"
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ 
              delay: 0.4,
              type: "spring",
              stiffness: 200,
              damping: 15
            }}
            whileHover={{ 
              scale: 1.1, 
              rotate: 5,
              boxShadow: "0 20px 40px -12px rgba(139, 92, 246, 0.4)"
            }}
            whileTap={{ scale: 0.95 }}
          >
            <LogIn className="w-8 h-8 text-white" />
          </motion.div>
          
          <motion.h2 
            className="text-2xl font-bold text-gray-800 mb-1"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            Welcome Back
          </motion.h2>
          <motion.p 
            className="text-gray-600 text-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
          >
            Continue your research journey
          </motion.p>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="space-y-3">
          {/* Email */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8, type: "spring", stiffness: 100 }}
            whileHover={{ scale: 1.02 }}
          >
            <label className="block text-sm font-bold text-gray-700 mb-2 tracking-wide">Email Address</label>
            <motion.input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-300 bg-gray-50 focus:bg-white text-gray-800 placeholder-gray-400"
              required
              whileFocus={{ scale: 1.02 }}
            />
          </motion.div>

          {/* Password */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.9, type: "spring", stiffness: 100 }}
            whileHover={{ scale: 1.02 }}
          >
            <label className="block text-sm font-bold text-gray-700 mb-2 tracking-wide">Password</label>
            <div className="relative">
              <motion.input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-3 pr-12 border-2 border-gray-300 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-300 bg-gray-50 focus:bg-white text-gray-800"
                required
                whileFocus={{ scale: 1.02 }}
              />
              <motion.button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 px-4 flex items-center text-gray-400 hover:text-blue-500 transition-colors"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <motion.div
                  initial={false}
                  animate={{ rotate: showPassword ? 0 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </motion.div>
              </motion.button>
            </div>
            
            {/* Forgot Password Link */}
            <motion.div 
              className="text-right mt-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.0 }}
            >
              <button
                type="button"
                onClick={handlePasswordReset}
                disabled={resetLoading}
                className="text-sm text-blue-600 hover:text-blue-700 hover:underline transition-colors disabled:opacity-50"
              >
                {resetLoading ? 'Sending...' : 'Forgot Password?'}
              </button>
            </motion.div>
          </motion.div>

          {/* Submit Button */}
          <motion.button
            type="submit"
            disabled={loading}
            className="w-full mt-5 py-3 px-6 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white font-bold rounded-xl shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 relative overflow-hidden"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0 }}
            whileHover={{ 
              scale: 1.02,
              boxShadow: "0 20px 40px -12px rgba(139, 92, 246, 0.4)",
              backgroundPosition: ["0% 50%", "100% 50%"]
            }}
            whileTap={{ scale: 0.98 }}
            style={{
              backgroundSize: "200% 200%"
            }}
          >
            {loading ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Signing in...
              </>
            ) : (
              <>
                <LogIn className="w-5 h-5" />
                Sign In
              </>
            )}
          </motion.button>
        </form>

        {/* Divider */}
        <div className="my-4 flex items-center gap-3">
          <div className="flex-1 h-px bg-gray-300"></div>
          <span className="text-sm text-gray-500">or</span>
          <div className="flex-1 h-px bg-gray-300"></div>
        </div>

        {/* Google Sign-In Button */}
        <motion.button
          type="button"
          onClick={handleGoogleSignIn}
          disabled={loading}
          className="w-full py-3 px-6 bg-white border-2 border-gray-200 text-gray-700 font-bold rounded-xl hover:bg-gray-50 hover:border-gray-300 hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 mb-4 relative overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.1 }}
          whileHover={{ 
            scale: 1.02,
            boxShadow: "0 10px 30px -12px rgba(0, 0, 0, 0.15)"
          }}
          whileTap={{ scale: 0.98 }}
        >
          {loading ? (
            <Loader className="w-5 h-5 animate-spin" />
          ) : (
            <>
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Continue with Google
            </>
          )}
        </motion.button>

        {/* Sign Up Link */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <p className="text-gray-600">
            Don't have an account?{' '}
            <Link to="/signup" className="text-blue-600 font-semibold hover:underline">
              Sign up
            </Link>
          </p>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default Login;
