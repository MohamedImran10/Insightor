import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { createUserWithEmailAndPassword, updateProfile, signInWithPopup, getAdditionalUserInfo } from 'firebase/auth';
import { auth, googleProvider } from '../firebase';
import { motion } from 'framer-motion';
import { UserPlus, Loader, Eye, EyeOff } from 'lucide-react';
import { useToast } from '../hooks/useToast.jsx';

const Signup = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const navigate = useNavigate();
  const { success, error: showError } = useToast();

  // Force light mode on auth pages
  useEffect(() => {
    document.documentElement.classList.remove('dark');
    document.body.classList.remove('dark');
    
    return () => {
      // Restore dark mode when leaving if it was enabled
      const savedDarkMode = localStorage.getItem('darkMode');
      if (savedDarkMode === 'true') {
        document.documentElement.classList.add('dark');
        document.body.classList.add('dark');
      }
    };
  }, []);
  const handleSignup = async (e) => {
    e.preventDefault();

    // Validate name
    if (!name.trim()) {
      const message = 'Please enter your full name';
      showError(message);
      return;
    }

    // Validate passwords match
    if (password !== confirmPassword) {
      const message = 'Passwords do not match. Please make sure both passwords are identical.';
      showError(message);
      return;
    }

    // Validate password strength
    if (password.length < 6) {
      const message = 'Password must be at least 6 characters long';
      showError(message);
      return;
    }

    // Additional password validation
    if (password.length < 8) {
      const message = 'For better security, use a password with at least 8 characters';
      showError(message);
      return;
    }

    setLoading(true);

    try {
      // Create user with Firebase
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      // Update profile with name
      await updateProfile(user, { displayName: name });

      // Get ID token
      const idToken = await user.getIdToken();

      // Store token in localStorage
      localStorage.setItem('token', idToken);
      localStorage.setItem('user_id', user.uid);
      localStorage.setItem('user_email', user.email);

      console.log('✅ Signup successful:', user.email);
      success(`Welcome to Insightor, ${name}! Your account has been created successfully.`);

      // Redirect to home
      navigate('/');
    } catch (err) {
      console.error('Signup error:', err);
      
      let errorMessage;
      switch (err.code) {
        case 'auth/email-already-in-use':
          errorMessage = 'An account with this email already exists. Please use a different email or try logging in instead.';
          break;
        case 'auth/invalid-email':
          errorMessage = 'Please enter a valid email address.';
          break;
        case 'auth/weak-password':
          errorMessage = 'Password is too weak. Please choose a stronger password with at least 6 characters.';
          break;
        case 'auth/operation-not-allowed':
          errorMessage = 'Email/password accounts are not enabled. Please contact support.';
          break;
        case 'auth/network-request-failed':
          errorMessage = 'Network error. Please check your internet connection and try again.';
          break;
        default:
          errorMessage = 'Account creation failed. Please try again.';
      }
      
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignUp = async () => {
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

      console.log('✅ Google authentication successful:', user.email);
      
      if (isNewUser) {
        success(`Welcome to Insightor, ${user.displayName || user.email}! Your account has been created successfully.`);
      } else {
        // Existing user - show login message
        success(`Welcome back, ${user.displayName || user.email}! You already have an account and have been logged in.`);
      }

      // Redirect to home
      navigate('/');
    } catch (err) {
      console.error('Google Sign-Up error:', err);
      
      let errorMessage;
      switch (err.code) {
        case 'auth/popup-closed-by-user':
          errorMessage = 'Sign-up cancelled. Please try again.';
          break;
        case 'auth/popup-blocked':
          errorMessage = 'Popup blocked. Please allow popups and try again.';
          break;
        case 'auth/network-request-failed':
          errorMessage = 'Network error. Please check your internet connection.';
          break;
        case 'auth/account-exists-with-different-credential':
          errorMessage = 'An account already exists with this email using a different sign-in method. Please try logging in with your email and password instead.';
          break;
        default:
          errorMessage = 'Google authentication failed. Please try again.';
      }
      
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      className="min-h-screen bg-gradient-to-br from-emerald-50 via-green-50 to-blue-100 flex items-center justify-center p-4 relative overflow-hidden"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-40 -right-40 w-80 h-80 bg-green-200 rounded-full mix-blend-multiply filter blur-xl opacity-70"
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 22,
            repeat: Infinity,
            repeatType: "reverse"
          }}
        />
        <motion.div
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-70"
          animate={{
            scale: [1.2, 1, 1.2],
            rotate: [360, 180, 0],
          }}
          transition={{
            duration: 28,
            repeat: Infinity,
            repeatType: "reverse"
          }}
        />
        <motion.div
          className="absolute top-40 left-1/2 w-80 h-80 bg-emerald-200 rounded-full mix-blend-multiply filter blur-xl opacity-70"
          animate={{
            scale: [1, 1.3, 1],
            x: [-50, 50, -50],
          }}
          transition={{
            duration: 18,
            repeat: Infinity,
            repeatType: "reverse"
          }}
        />
      </div>
      <motion.div
        className="w-full max-w-md bg-white/90 backdrop-blur-lg rounded-3xl shadow-2xl p-6 border border-white/20 relative z-10"
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
        <div className="text-center mb-2">
          {/* Insightor Logo/Brand */}
          <motion.div
            className="mb-2"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.8 }}
          >
            <motion.h1 
              className="text-3xl font-extrabold bg-gradient-to-r from-green-600 via-emerald-600 to-blue-600 bg-clip-text text-transparent mb-1 leading-tight py-2"
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
              Built for deeper research, driven by agentic intelligence
            </motion.p>
          </motion.div>

          <motion.div
            className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-r from-green-500 via-emerald-500 to-blue-500 rounded-2xl mb-1 shadow-xl"
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
              boxShadow: "0 20px 40px -12px rgba(34, 197, 94, 0.4)"
            }}
            whileTap={{ scale: 0.95 }}
          >
            <UserPlus className="w-7 h-7 text-white" />
          </motion.div>
          
          <motion.h2 
            className="text-xl font-bold text-gray-800 mb-1"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            Join Insightor
          </motion.h2>
          <motion.p 
            className="text-gray-600 text-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
          >
            Start your intelligent research journey
          </motion.p>
        </div>

        {/* Form */}
        <form onSubmit={handleSignup} className="space-y-2">
          {/* Name */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8, type: "spring", stiffness: 100 }}
            whileHover={{ scale: 1.02 }}
          >
            <label className="block text-xs font-bold text-gray-700 mb-0.5 tracking-wide">Full Name</label>
            <motion.input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="John Doe"
              className="w-full px-3 py-2 border-2 border-gray-300 rounded-xl focus:outline-none focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all duration-300 bg-gray-50 focus:bg-white text-gray-800 placeholder-gray-400"
              required
              whileFocus={{ scale: 1.02 }}
            />
          </motion.div>

          {/* Email */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.9, type: "spring", stiffness: 100 }}
            whileHover={{ scale: 1.02 }}
          >
            <label className="block text-xs font-bold text-gray-700 mb-0.5 tracking-wide">Email Address</label>
            <motion.input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              className="w-full px-3 py-2 border-2 border-gray-300 rounded-xl focus:outline-none focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all duration-300 bg-gray-50 focus:bg-white text-gray-800 placeholder-gray-400"
              required
              whileFocus={{ scale: 1.02 }}
            />
          </motion.div>

          {/* Password */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.0, type: "spring", stiffness: 100 }}
            whileHover={{ scale: 1.02 }}
          >
            <label className="block text-xs font-bold text-gray-700 mb-0.5 tracking-wide">Password</label>
            <div className="relative">
              <motion.input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3 py-2 pr-12 border-2 border-gray-300 rounded-xl focus:outline-none focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all duration-300 bg-gray-50 focus:bg-white text-gray-800"
                required
                whileFocus={{ scale: 1.02 }}
              />
              <motion.button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 px-4 flex items-center text-gray-400 hover:text-green-500 transition-colors"
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
            <motion.p 
              className="text-xs text-gray-500 mt-0.5 font-medium"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.1 }}
            >
              At least 6 characters
            </motion.p>
          </motion.div>

          {/* Confirm Password */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.1, type: "spring", stiffness: 100 }}
            whileHover={{ scale: 1.02 }}
          >
            <label className="block text-xs font-bold text-gray-700 mb-0.5 tracking-wide">Confirm Password</label>
            <div className="relative">
              <motion.input
                type={showConfirmPassword ? "text" : "password"}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3 py-2 pr-12 border-2 border-gray-300 rounded-xl focus:outline-none focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all duration-300 bg-gray-50 focus:bg-white text-gray-800"
                required
                whileFocus={{ scale: 1.02 }}
              />
              <motion.button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute inset-y-0 right-0 px-4 flex items-center text-gray-400 hover:text-green-500 transition-colors"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <motion.div
                  initial={false}
                  animate={{ rotate: showConfirmPassword ? 0 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </motion.div>
              </motion.button>
            </div>
          </motion.div>

          {/* Submit Button */}
          <motion.button
            type="submit"
            disabled={loading}
            className="w-full mt-3 py-2.5 px-6 bg-gradient-to-r from-green-600 via-emerald-600 to-blue-600 text-white font-bold rounded-xl shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 relative overflow-hidden"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2 }}
            whileHover={{ 
              scale: 1.02,
              boxShadow: "0 20px 40px -12px rgba(34, 197, 94, 0.4)",
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
                Creating account...
              </>
            ) : (
              <>
                <UserPlus className="w-5 h-5" />
                Create Account
              </>
            )}
          </motion.button>
        </form>

        {/* Divider */}
        <div className="my-2 flex items-center gap-3">
          <div className="flex-1 h-px bg-gray-300"></div>
          <span className="text-sm text-gray-500">or</span>
          <div className="flex-1 h-px bg-gray-300"></div>
        </div>

        {/* Google Sign-Up Button */}
        <motion.button
          type="button"
          onClick={handleGoogleSignUp}
          disabled={loading}
          className="w-full py-2.5 px-6 bg-white border-2 border-gray-200 text-gray-700 font-bold rounded-xl hover:bg-gray-50 hover:border-gray-300 hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 mb-2 relative overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3 }}
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

        {/* Login Link */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <p className="text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-green-600 font-semibold hover:underline">
              Sign in
            </Link>
          </p>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default Signup;