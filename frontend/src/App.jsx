import React, { useState, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Login from './pages/Login.jsx';
import Signup from './pages/Signup.jsx';
import ResearchApp from './pages/ResearchApp.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import Sidebar from './components/Sidebar.jsx';
import useAuth from './hooks/useAuth.js';
import useHistory from './hooks/useHistory.js';
import { ToastProvider } from './hooks/useToast.jsx';
import { LogOut, Menu } from 'lucide-react';

const AppLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const [showMenu, setShowMenu] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Debug logging
  console.log('🔍 AppLayout render - user:', user ? 'exists' : 'null');

  // Must have user to display this layout (ProtectedRoute ensures this)
  if (!user) {
    console.log('❌ AppLayout: No user, returning null');
    return null;
  }

  console.log('✅ AppLayout: Rendering layout for user');

  // Show header with logout for authenticated users
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Sidebar - Disabled temporarily */}
      {/* <Sidebar ... /> */}

      {/* Main Content Wrapper */}
      <div className="flex-1">
        {/* Header */}
        <motion.header
          className="bg-white shadow-md sticky top-0 z-40"
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
                <p className="font-semibold text-gray-800">{user?.displayName || user?.email}</p>
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
              <p className="font-semibold text-gray-800">{user?.email}</p>
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
        <div className="flex-1">
          {console.log('🎯 AppLayout: Rendering children:', children)}
          {children}
        </div>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <ToastProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Protected Routes - Wrapped with AppLayout */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <ResearchApp />
                </AppLayout>
              </ProtectedRoute>
            }
          />

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ToastProvider>
  );
};

export default App;
