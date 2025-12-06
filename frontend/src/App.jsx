import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Login from './pages/Login.jsx';
import Signup from './pages/Signup.jsx';
import ResearchApp from './pages/ResearchApp.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import useAuth from './hooks/useAuth.js';
import { LogOut, Menu } from 'lucide-react';

const AppLayout = ({ children }) => {
  const { user, logout, loading } = useAuth();
  const [showMenu, setShowMenu] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return children;
  }

  // Show header with logout for authenticated users
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Header */}
      <motion.header
        className="bg-white shadow-md sticky top-0 z-50"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
              Insightor
            </h1>
          </div>

          {/* User Info */}
          <div className="hidden md:flex items-center gap-6">
            <div className="text-right">
              <p className="text-sm text-gray-600">Welcome</p>
              <p className="font-semibold text-gray-800">{user.displayName || user.email}</p>
            </div>
            <button
              onClick={logout}
              className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors font-semibold"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>

          {/* Mobile Menu */}
          <div className="md:hidden">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Menu className="w-6 h-6 text-gray-800" />
            </button>
          </div>
        </div>

        {/* Mobile Menu Dropdown */}
        {showMenu && (
          <motion.div
            className="md:hidden bg-white border-t-2 border-gray-200 p-4 space-y-4"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <p className="text-sm text-gray-600">Signed in as</p>
            <p className="font-semibold text-gray-800">{user.email}</p>
            <button
              onClick={() => {
                logout();
                setShowMenu(false);
              }}
              className="w-full flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors font-semibold"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </motion.div>
        )}
      </motion.header>

      {/* Content */}
      <div>{children}</div>
    </div>
  );
};

const App = () => {

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Protected Routes */}
        <Route
          path="/"
          element={
            <AppLayout>
              <ProtectedRoute>
                <ResearchApp />
              </ProtectedRoute>
            </AppLayout>
          }
        />

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
