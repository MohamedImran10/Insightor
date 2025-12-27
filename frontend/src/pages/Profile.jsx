import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.js';
import { useTheme } from '../hooks/useTheme.jsx';
import { apiGet } from '../api/client.js';
import { 
  User, 
  Mail, 
  Calendar, 
  ArrowLeft, 
  Shield, 
  Search, 
  Clock, 
  TrendingUp,
  Database,
  LogOut,
  Edit3,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Settings,
  Bell,
  Moon,
  Sun
} from 'lucide-react';

const ProfilePage = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { darkMode, toggleDarkMode } = useTheme();
  const [stats, setStats] = useState({
    totalSearches: 0,
    lastSearchDate: null,
    topTopics: []
  });
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState(true);

  // Fetch user statistics
  const fetchUserStats = async () => {
    if (!user?.uid) return;
    
    setLoading(true);
    try {
      const response = await apiGet(`/history/${user.uid}?limit=100`);
      if (response.status === 'success' && response.history) {
        const history = response.history;
        
        // Calculate stats
        const totalSearches = history.length;
        const lastSearchDate = history.length > 0 ? history[0].timestamp : null;
        
        // Extract top topics (most common words in queries)
        const topicCounts = {};
        history.forEach(item => {
          const words = item.query?.toLowerCase().split(/\s+/) || [];
          words.forEach(word => {
            if (word.length > 3) { // Only count words with more than 3 characters
              topicCounts[word] = (topicCounts[word] || 0) + 1;
            }
          });
        });
        
        const topTopics = Object.entries(topicCounts)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 5)
          .map(([topic, count]) => ({ topic, count }));

        setStats({
          totalSearches,
          lastSearchDate,
          topTopics
        });
      }
    } catch (err) {
      console.error('Error fetching user stats:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUserStats();
  }, [user?.uid]);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error('Error signing out:', err);
    }
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get account age
  const getAccountAge = () => {
    if (!user?.metadata?.creationTime) return 'Unknown';
    const created = new Date(user.metadata.creationTime);
    const now = new Date();
    const diffDays = Math.floor((now - created) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return '1 day';
    if (diffDays < 30) return `${diffDays} days`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months`;
    return `${Math.floor(diffDays / 365)} years`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-20 left-10 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
          animate={{
            x: [0, 20, 0],
            y: [0, -20, 0],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
        <motion.div
          className="absolute bottom-20 right-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
          animate={{
            x: [0, -20, 0],
            y: [0, 20, 0],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto p-4 md:p-8">
        {/* Header */}
        <motion.div
          className="flex items-center justify-between mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center gap-4">
            <motion.button
              onClick={() => navigate('/research')}
              className="p-3 bg-white rounded-xl shadow-lg border border-gray-200 hover:border-blue-500 hover:shadow-xl transition-all duration-300"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </motion.button>
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-800 flex items-center gap-3">
                <User className="w-8 h-8 text-blue-600" />
                My Profile
              </h1>
              <p className="text-gray-600 mt-1">
                Manage your account and view your research activity
              </p>
            </div>
          </div>
          
          <motion.button
            onClick={fetchUserStats}
            className="p-3 bg-white rounded-xl shadow-lg border border-gray-200 hover:border-blue-500 hover:shadow-xl transition-all duration-300"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title="Refresh Stats"
          >
            <RefreshCw className={`w-5 h-5 text-blue-600 ${loading ? 'animate-spin' : ''}`} />
          </motion.button>
        </motion.div>

        {/* Profile Card */}
        <motion.div
          className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          {/* Profile Header */}
          <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 p-8">
            <div className="flex items-center gap-6">
              {/* Avatar */}
              <motion.div
                className="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-xl"
                whileHover={{ scale: 1.05 }}
              >
                {user?.photoURL ? (
                  <img 
                    src={user.photoURL} 
                    alt="Profile" 
                    className="w-full h-full rounded-full object-cover"
                  />
                ) : (
                  <span className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                    {user?.displayName?.charAt(0) || user?.email?.charAt(0) || '?'}
                  </span>
                )}
              </motion.div>
              
              {/* User Info */}
              <div className="text-white">
                <h2 className="text-2xl font-bold mb-1">
                  {user?.displayName || 'Insightor User'}
                </h2>
                <p className="text-blue-100 flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  {user?.email}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  {user?.emailVerified ? (
                    <span className="inline-flex items-center gap-1 text-xs bg-green-500 text-white px-2 py-1 rounded-full">
                      <CheckCircle className="w-3 h-3" />
                      Verified
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-xs bg-yellow-500 text-white px-2 py-1 rounded-full">
                      <AlertCircle className="w-3 h-3" />
                      Not Verified
                    </span>
                  )}
                  <span className="text-xs bg-white/20 px-2 py-1 rounded-full">
                    Member for {getAccountAge()}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Profile Details */}
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Account Info */}
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                  <Shield className="w-5 h-5 text-blue-600" />
                  Account Information
                </h3>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600 flex items-center gap-2">
                      <User className="w-4 h-4" />
                      User ID
                    </span>
                    <span className="text-gray-800 font-mono text-sm">
                      {user?.uid?.slice(0, 12)}...
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600 flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      Joined
                    </span>
                    <span className="text-gray-800 text-sm">
                      {user?.metadata?.creationTime 
                        ? new Date(user.metadata.creationTime).toLocaleDateString()
                        : 'Unknown'}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600 flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      Last Login
                    </span>
                    <span className="text-gray-800 text-sm">
                      {user?.metadata?.lastSignInTime 
                        ? new Date(user.metadata.lastSignInTime).toLocaleDateString()
                        : 'Unknown'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Research Stats */}
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-purple-600" />
                  Research Statistics
                </h3>
                
                {loading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                      <span className="text-gray-600 flex items-center gap-2">
                        <Search className="w-4 h-4" />
                        Total Searches
                      </span>
                      <span className="text-purple-700 font-bold text-lg">
                        {stats.totalSearches}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                      <span className="text-gray-600 flex items-center gap-2">
                        <Clock className="w-4 h-4" />
                        Last Search
                      </span>
                      <span className="text-gray-800 text-sm">
                        {stats.lastSearchDate 
                          ? new Date(stats.lastSearchDate).toLocaleDateString()
                          : 'Never'}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                      <span className="text-gray-600 flex items-center gap-2">
                        <Database className="w-4 h-4" />
                        Knowledge Base
                      </span>
                      <span className="text-purple-700 font-semibold">
                        {stats.totalSearches > 0 ? 'Active' : 'Empty'}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Top Research Topics */}
        {stats.topTopics.length > 0 && (
          <motion.div
            className="bg-white rounded-2xl shadow-xl border border-gray-200 p-6 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-green-600" />
              Your Top Research Topics
            </h3>
            <div className="flex flex-wrap gap-2">
              {stats.topTopics.map((item, index) => (
                <motion.span
                  key={item.topic}
                  className="px-4 py-2 bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 rounded-full font-medium text-sm flex items-center gap-2"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.05 }}
                >
                  {item.topic}
                  <span className="text-xs bg-white px-2 py-0.5 rounded-full text-purple-600">
                    {item.count}
                  </span>
                </motion.span>
              ))}
            </div>
          </motion.div>
        )}

        {/* Settings Section */}
        <motion.div
          className="bg-white rounded-2xl shadow-xl border border-gray-200 p-6 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2 mb-4">
            <Settings className="w-5 h-5 text-gray-600" />
            Preferences
          </h3>
          
          <div className="space-y-4">
            {/* Dark Mode Toggle */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
              <div className="flex items-center gap-3">
                {darkMode ? <Moon className="w-5 h-5 text-purple-600" /> : <Sun className="w-5 h-5 text-yellow-500" />}
                <div>
                  <p className="font-medium text-gray-800">Dark Mode</p>
                  <p className="text-sm text-gray-500">Toggle dark theme for the app</p>
                </div>
              </div>
              <motion.button
                onClick={toggleDarkMode}
                className={`w-14 h-8 rounded-full p-1 transition-colors ${
                  darkMode ? 'bg-purple-600' : 'bg-gray-300'
                }`}
                whileTap={{ scale: 0.95 }}
              >
                <motion.div
                  className="w-6 h-6 bg-white rounded-full shadow-md"
                  animate={{ x: darkMode ? 24 : 0 }}
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                />
              </motion.button>
            </div>

            {/* Notifications Toggle */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
              <div className="flex items-center gap-3">
                <Bell className={`w-5 h-5 ${notifications ? 'text-blue-600' : 'text-gray-400'}`} />
                <div>
                  <p className="font-medium text-gray-800">Notifications</p>
                  <p className="text-sm text-gray-500">Receive research updates (coming soon)</p>
                </div>
              </div>
              <motion.button
                onClick={() => setNotifications(!notifications)}
                className={`w-14 h-8 rounded-full p-1 transition-colors ${
                  notifications ? 'bg-blue-600' : 'bg-gray-300'
                }`}
                whileTap={{ scale: 0.95 }}
              >
                <motion.div
                  className="w-6 h-6 bg-white rounded-full shadow-md"
                  animate={{ x: notifications ? 24 : 0 }}
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                />
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <motion.button
            onClick={() => navigate('/research')}
            className="p-4 bg-white rounded-xl shadow-lg border border-gray-200 hover:border-blue-500 hover:shadow-xl transition-all duration-300 flex items-center gap-3"
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="p-2 bg-blue-100 rounded-lg">
              <Search className="w-5 h-5 text-blue-600" />
            </div>
            <div className="text-left">
              <p className="font-semibold text-gray-800">New Research</p>
              <p className="text-sm text-gray-500">Start a new search</p>
            </div>
          </motion.button>

          <motion.button
            onClick={() => navigate('/history')}
            className="p-4 bg-white rounded-xl shadow-lg border border-gray-200 hover:border-purple-500 hover:shadow-xl transition-all duration-300 flex items-center gap-3"
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="p-2 bg-purple-100 rounded-lg">
              <Clock className="w-5 h-5 text-purple-600" />
            </div>
            <div className="text-left">
              <p className="font-semibold text-gray-800">View History</p>
              <p className="text-sm text-gray-500">Browse past searches</p>
            </div>
          </motion.button>

          <motion.button
            onClick={handleLogout}
            className="p-4 bg-white rounded-xl shadow-lg border border-gray-200 hover:border-red-500 hover:shadow-xl transition-all duration-300 flex items-center gap-3"
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="p-2 bg-red-100 rounded-lg">
              <LogOut className="w-5 h-5 text-red-600" />
            </div>
            <div className="text-left">
              <p className="font-semibold text-gray-800">Sign Out</p>
              <p className="text-sm text-gray-500">Logout from account</p>
            </div>
          </motion.button>
        </motion.div>

        {/* Footer */}
        <motion.div
          className="text-center text-gray-500 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <p>© 2025 Insightor. All rights reserved.</p>
        </motion.div>
      </div>
    </div>
  );
};

export default ProfilePage;
