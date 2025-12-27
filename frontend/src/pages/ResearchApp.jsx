import React, { useState, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import SearchInput from '../components/SearchInput.jsx';
import ResearchContainer from '../components/ResearchContainer.jsx';
import { apiPost } from '../api/client.js';
import { History, User, LogOut, Moon, Sun } from 'lucide-react';
import { useAuth } from '../hooks/useAuth.js';
import { useTheme } from '../hooks/useTheme.jsx';

const ResearchApp = () => {
  console.log('🔍 ResearchApp: Rendering...');
  
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [summary, setSummary] = useState('');
  const [insights, setInsights] = useState([]);
  const [memoryChunks, setMemoryChunks] = useState([]);
  const [pastMemories, setPastMemories] = useState([]);
  const [error, setError] = useState('');
  const [historyLoaded, setHistoryLoaded] = useState(false);

  // Load history from session storage or URL state if available
  useEffect(() => {
    const checkAndLoadHistory = () => {
      // First check if data was passed via navigation state
      if (location.state && location.state.historyData) {
        const historyData = location.state.historyData;
        console.log('📋 History data from navigation state:', historyData);
        
        setQuery(historyData.query || '');
        setSummary(historyData.response || '');
        setResults(historyData.search_results || historyData.sources || []);
        setInsights(historyData.insights || []);
        setMemoryChunks(historyData.memory_chunks || []);
        setPastMemories([]);
        setHistoryLoaded(true);
        
        console.log('✅ Loaded history from navigation state:', historyData.query);
        return;
      }
      
      // Then check session storage
      const loadedHistory = sessionStorage.getItem('loadedHistory');
      console.log('🔍 Checking for loaded history in session:', !!loadedHistory);
      
      if (loadedHistory) {
        try {
          const historyData = JSON.parse(loadedHistory);
          console.log('📋 History data found in session:', historyData);
          
          setQuery(historyData.query || '');
          setSummary(historyData.response || '');
          setResults(historyData.search_results || historyData.sources || []);
          setInsights(historyData.insights || []);
          setMemoryChunks(historyData.memory_chunks || []);
          setPastMemories([]);
          setHistoryLoaded(true);
          
          // Clear from session storage
          sessionStorage.removeItem('loadedHistory');
          console.log('✅ Loaded history data from session:', historyData.query);
          console.log('✅ Loaded results:', historyData.search_results || historyData.sources || []);
          console.log('✅ Loaded summary:', historyData.response || '');
        } catch (err) {
          console.error('❌ Error loading history:', err);
        }
      } else {
        console.log('🔍 No history data found in session storage');
      }
    };

    // Check immediately
    checkAndLoadHistory();
    
    // Also check after a small delay to handle timing issues
    const timeoutId = setTimeout(checkAndLoadHistory, 100);
    
    return () => clearTimeout(timeoutId);
  }, [location.state]);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error('Error signing out:', err);
    }
  };

  const handleSearch = useCallback(async (searchQuery) => {
    setQuery(searchQuery);
    setLoading(true);
    setError('');
    setSummary('');
    setResults([]);
    setInsights([]);
    setMemoryChunks([]);
    setPastMemories([]);
    setHistoryLoaded(false);

    try {
      const response = await apiPost('/research', {
        query: searchQuery,
      });

      if (response.status === 'success') {
        setSummary(response.final_summary);
        setResults(response.search_results || []);
        setInsights(response.top_insights || []);
        setMemoryChunks(response.relevant_memory_chunks || []);
        setPastMemories(response.past_research_memories || []);

        console.log('✅ Research completed successfully');
      } else {
        setError(response.error || 'Failed to complete research');
      }
    } catch (err) {
      console.error('Error:', err);
      setError(
        err.message ||
          'Failed to connect to the research service. Make sure the backend is running on port 8000 and you are authenticated.'
      );
    } finally {
      setLoading(false);
    }
  }, []);

  const handleNewSearch = useCallback(() => {
    setQuery('');
    setResults([]);
    setSummary('');
    setInsights([]);
    setMemoryChunks([]);
    setPastMemories([]);
    setError('');
    setHistoryLoaded(false);
  }, []);

  return (
    <motion.div
      className="bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 min-h-screen"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-20 left-10 w-72 h-72 bg-blue-300 dark:bg-blue-600 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-3xl opacity-20"
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
      </div>

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Navigation Header */}
        <motion.div 
          className="flex justify-between items-center p-4 bg-white/80 dark:bg-gray-800/90 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 rounded-lg flex items-center justify-center text-white text-sm font-bold">
              🔍
            </div>
            <span className="font-bold text-xl text-gray-800 dark:text-white">Insightor</span>
          </div>
          
          <div className="flex items-center gap-4">
            <motion.button
              onClick={() => navigate('/history')}
              className="flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/50 text-blue-600 dark:text-blue-300 rounded-lg font-semibold hover:bg-blue-100 dark:hover:bg-blue-900/70 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <History className="w-4 h-4" />
              History
            </motion.button>
            
            {user && (
              <div className="flex items-center gap-3">
                <motion.button
                  onClick={() => navigate('/profile')}
                  className="flex items-center gap-2 text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  title="My Profile"
                >
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                    {user.displayName?.charAt(0) || user.email?.charAt(0) || '?'}
                  </div>
                  <span className="text-sm font-medium hidden md:block text-gray-800 dark:text-gray-100">{user.displayName || user.email?.split('@')[0]}</span>
                </motion.button>
                <motion.button
                  onClick={handleLogout}
                  className="p-2 text-gray-400 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-500 transition-colors"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  title="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </motion.button>
              </div>
            )}
          </div>
        </motion.div>

        {/* Header Section */}
        <div className="flex flex-col items-center pt-6 pb-4 px-4">
          {/* Logo and Title */}
          <div className="text-center mb-4">
            <div className="inline-flex items-center gap-4 mb-2">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 rounded-xl flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                🔍
              </div>
              <h1 className="text-4xl md:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 leading-tight py-2">
                Insightor
              </h1>
            </div>
            <p className="text-gray-600 dark:text-gray-300 text-lg md:text-xl font-semibold mb-1">
              Your AI-Powered Research Assistant
            </p>
            <p className="text-gray-500 dark:text-gray-400 text-sm md:text-base mt-1">
              Search, analyze, and summarize information in seconds using advanced AI
            </p>
          </div>

          {/* Search Input */}
          <SearchInput onSubmit={handleSearch} loading={loading} />

          {/* History Loaded Indicator */}
          {historyLoaded && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 flex items-center justify-between px-4 py-3 bg-green-100 dark:bg-green-900/40 border border-green-300 dark:border-green-700 rounded-lg text-green-700 dark:text-green-300 text-sm font-medium"
            >
              <div className="flex items-center gap-2">
                <History className="w-4 h-4" />
                ✅ Loaded from search history: "{query}"
              </div>
              <motion.button
                onClick={handleNewSearch}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors text-sm"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                🔍 New Research
              </motion.button>
            </motion.div>
          )}

          {/* Feature Highlights */}
          {!summary && !loading && (
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl">
              {[
                {
                  icon: '🔍',
                  title: 'Web Search',
                  desc: 'Find the most relevant information from across the web',
                },
                {
                  icon: '📖',
                  title: 'Content Analysis',
                  desc: 'Extract and clean content from multiple sources',
                },
                {
                  icon: '🧠',
                  title: 'AI Insights',
                  desc: 'Get intelligent summaries powered by Gemini',
                },
              ].map((feature, index) => (
                <div
                  key={index}
                  className="p-6 bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 shadow-xl hover:shadow-2xl transition-all duration-300"
                >
                  <div className="text-4xl mb-3 text-center">{feature.icon}</div>
                  <h3 className="font-bold text-gray-800 dark:text-white mb-2 text-lg text-center">{feature.title}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 text-center leading-relaxed">{feature.desc}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Results Section */}
        {(summary || loading || error) && (
          <div className="flex-1 pb-4">
            {error && (
              <div className="max-w-6xl mx-auto px-4 py-4">
                <div className="p-6 bg-red-50 dark:bg-red-900/30 border-2 border-red-300 dark:border-red-600 rounded-lg text-red-700 dark:text-red-300 font-semibold text-center">
                  ❌ {error}
                </div>
                <div className="mt-6 flex justify-center">
                  <button
                    onClick={handleNewSearch}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                  >
                    Try New Search
                  </button>
                </div>
              </div>
            )}

            {(summary || loading) && !error && (
              <ResearchContainer
                query={query}
                summary={summary}
                results={results}
                insights={insights}
                memoryChunks={memoryChunks}
                pastMemories={pastMemories}
                loading={loading}
                onNewSearch={handleNewSearch}
                isFromHistory={historyLoaded}
              />
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="relative z-10 py-6 text-center text-gray-500 dark:text-gray-400 text-sm">
        © 2025 Insightor. Precision-engineered intelligence for real-world research.
      </footer>
    </motion.div>
  );
};

export default ResearchApp;