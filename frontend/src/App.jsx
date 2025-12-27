import React, { useState, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Login from './pages/Login.jsx';
import Signup from './pages/Signup.jsx';
import ResearchApp from './pages/ResearchApp.jsx';
import History from './pages/History.jsx';
import Profile from './pages/Profile.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import { ToastProvider } from './hooks/useToast.jsx';
import { ThemeProvider } from './hooks/useTheme.jsx';

const App = () => {
  return (
    <ThemeProvider>
      <ToastProvider>
        <Router>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />

          {/* Protected Routes */}
          <Route
            path="/research"
            element={
              <ProtectedRoute>
                <ResearchApp />
              </ProtectedRoute>
            }
          />
          <Route
            path="/history"
            element={
              <ProtectedRoute>
                <History />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />

          {/* Default route */}
          <Route path="/" element={<Navigate to="/research" replace />} />

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/research" replace />} />
        </Routes>
      </Router>
    </ToastProvider>
  </ThemeProvider>
  );
};

export default App;
