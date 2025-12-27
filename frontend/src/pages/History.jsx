import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.js';
import { apiGet, api } from '../api/client.js';
import { History, ArrowLeft, Trash2, Clock, Search, RefreshCw, Calendar, FileText } from 'lucide-react';

const HistoryPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedHistory, setSelectedHistory] = useState(null);

  // Fetch history
  const fetchHistory = async () => {
    if (!user?.uid) return;
    
    setLoading(true);
    try {
      const response = await apiGet(`/history/${user.uid}?limit=50`);
      if (response.status === 'success') {
        setHistory(response.history || []);
        console.log(`✅ Loaded ${response.history?.length || 0} history entries`);
        // Debug: Log the first history item to see structure
        if (response.history && response.history.length > 0) {
          console.log('📋 First history item structure:', response.history[0]);
        }
      }
    } catch (err) {
      console.error('❌ Error fetching history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [user?.uid]);

  // Delete history item
  const handleDeleteHistory = async (historyId, e) => {
    e.stopPropagation();
    if (!user?.uid) return;
    
    try {
      await api(`/history/${user.uid}/${historyId}`, { method: 'DELETE' });
      setHistory(prev => prev.filter(h => h.id !== historyId));
      if (selectedHistory?.id === historyId) {
        setSelectedHistory(null);
      }
    } catch (err) {
      console.error('❌ Error deleting history:', err);
    }
  };

  // Load history item to research page
  const loadHistoryItem = (item) => {
    console.log('🚀 Loading history item:', item);
    
    // Prepare history data
    const historyData = {
      query: item.query,
      response: item.response,
      sources: item.sources || item.search_results || [],
      insights: item.insights || [],
      memory_chunks: item.memory_chunks || [],
      search_results: item.search_results || item.sources || []
    };
    
    console.log('💾 Prepared history data:', historyData);
    
    // Store in session storage as backup
    sessionStorage.setItem('loadedHistory', JSON.stringify(historyData));
    
    // Navigate with state as primary method
    navigate('/research', { 
      state: { historyData },
      replace: true 
    });
  };

  // Group history by date
  const groupHistoryByDate = (historyItems) => {
    const groups = {};
    historyItems.forEach(item => {
      const date = new Date(item.timestamp).toDateString();
      if (!groups[date]) groups[date] = [];
      groups[date].push(item);
    });
    return groups;
  };

  const historyGroups = groupHistoryByDate(history);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800">
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
      </div>

      <div className="relative z-10 max-w-7xl mx-auto p-4">
        {/* Header */}
        <motion.div
          className="flex items-center justify-between mb-8 pt-4"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center gap-4">
            <motion.button
              onClick={() => navigate('/research')}
              className="p-3 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:border-blue-500 hover:shadow-xl transition-all duration-300"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <ArrowLeft className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            </motion.button>
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-800 dark:text-white flex items-center gap-3">
                <History className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                Search History
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                View and manage your previous research queries
              </p>
            </div>
          </div>
          
          <motion.button
            onClick={fetchHistory}
            className="p-3 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:border-blue-500 hover:shadow-xl transition-all duration-300"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title="Refresh History"
          >
            <RefreshCw className={`w-5 h-5 text-blue-600 dark:text-blue-400 ${loading ? 'animate-spin' : ''}`} />
          </motion.button>
        </motion.div>

        {/* Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* History List */}
          <div className="lg:col-span-2">
            <motion.div
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              {loading ? (
                <div className="p-12 text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600 dark:text-gray-400">Loading your search history...</p>
                </div>
              ) : history.length === 0 ? (
                <div className="p-12 text-center">
                  <Search className="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-600" />
                  <h3 className="text-xl font-semibold text-gray-600 dark:text-gray-300 mb-2">No search history yet</h3>
                  <p className="text-gray-500 dark:text-gray-400 mb-6">Start researching to build your search history</p>
                  <motion.button
                    onClick={() => navigate('/research')}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Start Researching
                  </motion.button>
                </div>
              ) : (
                <div className="max-h-[80vh] overflow-y-auto">
                  {Object.entries(historyGroups).map(([date, items]) => (
                    <div key={date} className="border-b border-gray-100 dark:border-gray-700 last:border-0">
                      {/* Date Header */}
                      <div className="sticky top-0 bg-gray-50 dark:bg-gray-700 px-6 py-3 border-b border-gray-200 dark:border-gray-600 z-10">
                        <div className="flex items-center gap-2 text-gray-700 dark:text-gray-200 font-semibold">
                          <Calendar className="w-4 h-4" />
                          {date}
                        </div>
                      </div>
                      
                      {/* History Items */}
                      <div className="divide-y divide-gray-100 dark:divide-gray-700">
                        {items.map((item) => (
                          <motion.div
                            key={item.id}
                            onClick={() => setSelectedHistory(item)}
                            className={`p-4 cursor-pointer transition-all duration-200 ${
                              selectedHistory?.id === item.id 
                                ? 'bg-blue-100 dark:bg-blue-900/50 border-l-4 border-blue-500' 
                                : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                            }`}
                            whileHover={{ x: 4 }}
                          >
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1 min-w-0">
                                <h3 className="font-semibold text-gray-800 dark:text-white truncate text-lg">
                                  {item.query}
                                </h3>
                                <div className="flex items-center gap-4 mt-2 text-sm text-gray-500 dark:text-gray-400">
                                  <div className="flex items-center gap-1">
                                    <Clock className="w-4 h-4" />
                                    <span>
                                      {new Date(item.timestamp).toLocaleTimeString('en-US', {
                                        hour: '2-digit',
                                        minute: '2-digit'
                                      })}
                                    </span>
                                  </div>
                                  {(item.sources?.length > 0 || item.search_results?.length > 0) ? (
                                    <div className="flex items-center gap-1">
                                      <FileText className="w-4 h-4" />
                                      <span>
                                        {(item.sources?.length || 0) + (item.search_results?.length || 0)} sources
                                      </span>
                                    </div>
                                  ) : (
                                    <div className="flex items-center gap-1 text-orange-500 dark:text-orange-400">
                                      <FileText className="w-4 h-4" />
                                      <span>No sources saved</span>
                                    </div>
                                  )}
                                </div>
                                {item.response && (
                                  <p className="text-gray-600 dark:text-gray-300 text-sm mt-2 line-clamp-2">
                                    {item.response.substring(0, 150)}...
                                  </p>
                                )}
                              </div>
                              <motion.button
                                onClick={(e) => handleDeleteHistory(item.id, e)}
                                className="p-2 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-all"
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
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          </div>

          {/* History Details Panel */}
          <div className="lg:col-span-1">
            <motion.div
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 sticky top-4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <AnimatePresence mode="wait">
                {selectedHistory ? (
                  <motion.div
                    key={selectedHistory.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="p-6"
                  >
                    {/* Header */}
                    <div className="mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
                      <h3 className="font-bold text-lg text-gray-800 dark:text-white mb-2">
                        {selectedHistory.query}
                      </h3>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(selectedHistory.timestamp).toLocaleString()}
                      </div>
                    </div>

                    {/* Summary */}
                    {selectedHistory.response && (
                      <div className="mb-6">
                        <h4 className="font-semibold text-gray-700 dark:text-gray-200 mb-2">Summary</h4>
                        <div className="text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 rounded-lg p-3 max-h-40 overflow-y-auto">
                          {selectedHistory.response}
                        </div>
                      </div>
                    )}

                    {/* Sources */}
                    {((selectedHistory.sources && selectedHistory.sources.length > 0) || 
                      (selectedHistory.search_results && selectedHistory.search_results.length > 0)) && (
                      <div className="mb-6">
                        <h4 className="font-semibold text-gray-700 dark:text-gray-200 mb-2">
                          Sources ({(selectedHistory.sources?.length || 0) + (selectedHistory.search_results?.length || 0)})
                        </h4>
                        <div className="space-y-2 max-h-32 overflow-y-auto">
                          {/* Display sources */}
                          {selectedHistory.sources && selectedHistory.sources.slice(0, 5).map((source, idx) => (
                            <div key={`source-${idx}`} className="text-xs bg-gray-50 dark:bg-gray-700 rounded p-2">
                              <div className="font-medium text-gray-700 dark:text-gray-200 truncate">
                                {source.title || `Source ${idx + 1}`}
                              </div>
                              <div className="text-gray-500 dark:text-gray-400 truncate">
                                {source.url || source.link || 'No URL'}
                              </div>
                            </div>
                          ))}
                          {/* Display search results if different from sources */}
                          {selectedHistory.search_results && selectedHistory.search_results.slice(0, 5).map((result, idx) => (
                            <div key={`result-${idx}`} className="text-xs bg-blue-50 dark:bg-blue-900/30 rounded p-2">
                              <div className="font-medium text-gray-700 dark:text-gray-200 truncate">
                                {result.title || `Result ${idx + 1}`}
                              </div>
                              <div className="text-gray-500 dark:text-gray-400 truncate">
                                {result.url || result.link || 'No URL'}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="space-y-2">
                      <motion.button
                        onClick={() => loadHistoryItem(selectedHistory)}
                        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        Load in Research
                      </motion.button>
                      <motion.button
                        onClick={(e) => handleDeleteHistory(selectedHistory.id, e)}
                        className="w-full px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg font-semibold hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        Delete
                      </motion.button>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="p-8 text-center text-gray-500 dark:text-gray-400"
                  >
                    <History className="w-12 h-12 mx-auto mb-3 opacity-30" />
                    <p className="font-medium">Select a search</p>
                    <p className="text-sm mt-1">Click on any search to view details</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HistoryPage;