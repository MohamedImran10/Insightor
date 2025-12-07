import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import SearchInput from '../components/SearchInput.jsx';
import ResearchContainer from '../components/ResearchContainer.jsx';
import { apiPost } from '../api/client.js';

const ResearchApp = () => {
  console.log('🔍 ResearchApp: Rendering...');
  
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [summary, setSummary] = useState('');
  const [insights, setInsights] = useState([]);
  const [memoryChunks, setMemoryChunks] = useState([]);
  const [pastMemories, setPastMemories] = useState([]);
  const [error, setError] = useState('');

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
