import React from 'react';
import { Navigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth.js';
import { motion } from 'framer-motion';
import { Loader } from 'lucide-react';

/**
 * ProtectedRoute - Wrapper for routes that require authentication
 * 
 * Usage:
 * <Route element={<ProtectedRoute><ResearchPage /></ProtectedRoute>} path="/research" />
 */
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, error } = useAuth();

  if (loading) {
    return (
      <motion.div
        className="min-h-screen flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <div className="text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            className="inline-block"
          >
            <Loader className="w-12 h-12 text-blue-600" />
          </motion.div>
          <p className="mt-4 text-gray-600 font-semibold">Loading...</p>
        </div>
      </motion.div>
    );
  }

  // Allow if authenticated or if there's an error (fallback mode)
  if (!isAuthenticated && !error) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
