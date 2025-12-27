import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import SearchInput from '../components/SearchInput.jsx';
import ResearchContainer from '../components/ResearchContainer.jsx';
import { apiPost } from '../api/client.js';

const ResearchApp = () => {
  console.log('🔍 ResearchApp: Rendering...');
  
  const { user } = useAuth();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [summary, setSummary] = useState('');
  const [insights, setInsights] = useState([]);
  const [memoryChunks, setMemoryChunks] = useState([]);
  const [pastMemories, setPastMemories] = useState([]);
  const [error, setError] = useState('');
  
  // Sidebar state
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Fetch history
  const fetchHistory = useCallback(async () => {
    if (!user?.uid) return;
    
    setHistoryLoading(true);
    try {
      const response = await apiGet(`/history/${user.uid}?limit=20`);
      if (response.status === 'success') {
        setHistory(response.history || []);
        console.log(`✅ Loaded ${response.history?.length || 0} history entries`);
      }
    } catch (err) {
      console.error('❌ Error fetching history:', err);
      setHistory([]); // Set empty array on error
    } finally {
      setHistoryLoading(false);
    }
  }, [user?.uid]);

  // Fetch history when sidebar opens
  useEffect(() => {
    if (sidebarOpen && user?.uid) {
      fetchHistory();
    }
  }, [sidebarOpen, user?.uid, fetchHistory]);

  // Load history item
  const handleHistoryClick = (item) => {
    setQuery(item.query);
    setSummary(item.response || '');
    setResults(item.sources || []);
    setInsights(item.insights || []);
    setMemoryChunks(item.memory_chunks || []);
    setSidebarOpen(false);
  };

  // Delete history item
  const handleDeleteHistory = async (historyId, e) => {
    e.stopPropagation();
    if (!user?.uid) return;
    
    try {
      await api(`/history/${user.uid}/${historyId}`, { method: 'DELETE' });
      setHistory(prev => prev.filter(h => h.id !== historyId));
    } catch (err) {
      console.error('❌ Error deleting history:', err);
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
  }, []);

  // Page background animation
  const pageVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { duration: 0.6 },
    },
  };

  return (
    <motion.div
      className="bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 min-h-screen"
      variants={pageVariants}
      initial="hidden"
      animate="visible"
    >
      {/* History Sidebar Toggle Button */}
      {user && (
        <motion.button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="fixed left-4 top-20 z-50 p-3 bg-white rounded-full shadow-lg border-2 border-gray-200 hover:border-blue-500 hover:shadow-xl transition-all duration-300"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          title={sidebarOpen ? "Close History" : "Open History"}
        >
          {sidebarOpen ? (
            <X className="w-5 h-5 text-gray-600" />
          ) : (
            <History className="w-5 h-5 text-blue-600" />
          )}
        </motion.button>
      )}

      {/* History Sidebar */}
      <AnimatePresence>
        {sidebarOpen && user && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/20 z-40"
              onClick={() => setSidebarOpen(false)}
            />
            
            {/* Sidebar Panel */}
            <motion.div
              initial={{ x: -320 }}
              animate={{ x: 0 }}
              exit={{ x: -320 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="fixed left-0 top-0 h-full w-80 bg-white shadow-2xl z-50 flex flex-col"
            >
              {/* Sidebar Header */}
              <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-purple-600">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-white">
                    <History className="w-5 h-5" />
                    <h2 className="font-bold text-lg">Search History</h2>
                  </div>
                  <motion.button
                    onClick={() => setSidebarOpen(false)}
                    className="p-1 rounded-lg hover:bg-white/20 transition-colors"
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                  >
                    <X className="w-5 h-5 text-white" />
                  </motion.button>
                </div>
              </div>

              {/* History List */}
              <div className="flex-1 overflow-y-auto p-3">
                {historyLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                ) : history.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Search className="w-12 h-12 mx-auto mb-3 opacity-30" />
                    <p className="font-medium">No search history yet</p>
                    <p className="text-sm mt-1">Your searches will appear here</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {history.map((item) => (
                      <motion.div
                        key={item.id}
                        onClick={() => handleHistoryClick(item)}
                        className="p-3 bg-gray-50 rounded-xl border border-gray-200 cursor-pointer hover:bg-blue-50 hover:border-blue-300 transition-all duration-200 group"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-gray-800 truncate text-sm">
                              {item.query}
                            </p>
                            <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
                              <Clock className="w-3 h-3" />
                              <span>
                                {new Date(item.timestamp).toLocaleDateString('en-US', {
                                  month: 'short',
                                  day: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </span>
                            </div>
                          </div>
                          <motion.button
                            onClick={(e) => handleDeleteHistory(item.id, e)}
                            className="p-1.5 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-red-100 transition-all"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </motion.button>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>

              {/* Sidebar Footer */}
              <div className="p-3 border-t border-gray-200 bg-gray-50">
                <p className="text-xs text-gray-500 text-center">
                  {history.length} {history.length === 1 ? 'search' : 'searches'} in history
                </p>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Animated Background Elements */}
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
          className="absolute top-40 right-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
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
        <motion.div
          className="absolute bottom-10 left-1/2 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
          animate={{
            x: [0, 20, 0],
            y: [0, 20, 0],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col">
        {/* Header Section */}
        <motion.div
          className={`flex flex-col items-center pt-6 px-4 ${!summary && !loading && !error ? 'min-h-screen justify-between' : 'pb-6'}`}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          {/* Main Content Wrapper */}
          <div className="flex flex-col items-center w-full">
          {/* Logo and Title */}
          <motion.div
            className="text-center mb-4"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.2, type: "spring", stiffness: 80 }}
          >
            <motion.div
              className="inline-flex items-center gap-4 mb-2"
              whileHover={{ scale: 1.08 }}
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.3, type: "spring", stiffness: 100 }}
            >
              <motion.div
                className="w-14 h-14 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 rounded-xl flex items-center justify-center text-white text-2xl font-bold shadow-lg"
                animate={{ 
                  rotate: 360,
                  boxShadow: [
                    "0 4px 20px rgba(59, 130, 246, 0.3)",
                    "0 4px 20px rgba(147, 51, 234, 0.3)",
                    "0 4px 20px rgba(236, 72, 153, 0.3)",
                    "0 4px 20px rgba(59, 130, 246, 0.3)"
                  ]
                }}
                transition={{ 
                  rotate: { duration: 20, repeat: Infinity, ease: 'linear' },
                  boxShadow: { duration: 4, repeat: Infinity, ease: 'easeInOut' }
                }}
                whileHover={{ scale: 1.1, rotate: 180 }}
              >
                🔍
              </motion.div>
              <motion.h1 
                className="text-4xl md:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 leading-tight py-2"
                animate={{ 
                  backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
                }}
                transition={{
                  duration: 4,
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
            </motion.div>
            <motion.p 
              className="text-gray-600 text-lg md:text-xl font-semibold mb-1"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              Your AI-Powered Research Assistant
            </motion.p>
            <motion.p 
              className="text-gray-500 text-sm md:text-base mt-1"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.7 }}
            >
              Search, analyze, and summarize information in seconds using advanced AI
            </motion.p>
          </motion.div>

          {/* Search Input */}
          <SearchInput onSubmit={handleSearch} loading={loading} />

          {/* Feature Highlights */}
          {!summary && !loading && (
            <motion.div
              className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
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
                <motion.div
                  key={index}
                  className="p-6 bg-white rounded-xl border-2 border-gray-200 shadow-xl hover:shadow-2xl transition-all duration-300"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 + index * 0.1 }}
                  whileHover={{ translateY: -8, scale: 1.02 }}
                >
                  <div className="text-4xl mb-3 text-center">{feature.icon}</div>
                  <h3 className="font-bold text-gray-800 mb-2 text-lg text-center">{feature.title}</h3>
                  <p className="text-sm text-gray-600 text-center leading-relaxed">{feature.desc}</p>
                </motion.div>
              ))}
            </motion.div>
          )}
          </div>


        </motion.div>

        {/* Results Section */}
        {(summary || loading || error) && (
          <div className="flex-1 pb-4">
            {error && (
              <motion.div
                className="max-w-6xl mx-auto px-4 py-4"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}  
              >
                <div className="p-6 bg-red-50 border-2 border-red-300 rounded-lg text-red-700 font-semibold text-center">
                  ❌ {error}
                </div>
                <motion.div className="mt-6 flex justify-center">
                  <motion.button
                    onClick={handleNewSearch}
                    className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-lg shadow-lg hover:shadow-xl transition-all"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    🔄 Try Again
                  </motion.button>
                </motion.div>
              </motion.div>
            )}

            {!error && (
              <ResearchContainer
                query={query}
                loading={loading}
                results={results}
                summary={summary}
                insights={insights}
                memoryChunks={memoryChunks}
                pastMemories={pastMemories}
                onNewSearch={handleNewSearch}
              />
            )}
          </div>
        )}
      </div>

      {/* Footer - only show when no results */}
      {!summary && !loading && !error && (
        <motion.footer
          className="relative z-10 py-4 text-center text-gray-500 border-t border-gray-200 bg-white/30 backdrop-blur-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
        >
          <p className="text-xs">
            © 2025 Insightor. Precision-engineered intelligence for real-world research.
          </p>
        </motion.footer>
      )}
    </motion.div>
  );
};

export default ResearchApp;
