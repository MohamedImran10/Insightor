import React from 'react';
import { motion } from 'framer-motion';
import { Search, Loader, CheckCircle, AlertCircle, BookOpen, Archive, Zap } from 'lucide-react';

const ResearchContainer = ({ query, loading, results, summary, insights, memoryChunks, pastMemories, onNewSearch }) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: 'easeOut' },
    },
  };

  const pulseVariants = {
    pulse: {
      scale: [1, 1.05, 1],
      transition: { duration: 2, repeat: Infinity },
    },
  };

  return (
    <motion.div
      className="w-full max-w-6xl mx-auto p-4 md:p-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Header */}
      <motion.div
        className="mb-8 text-center"
        variants={itemVariants}
      >
        <h1 className="text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-2">
          Insightor
        </h1>
        <p className="text-gray-600 text-lg">AI-Powered Research Assistant with Memory</p>
      </motion.div>

      {/* Query Display */}
      {query && (
        <motion.div
          className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border-2 border-blue-200"
          variants={itemVariants}
        >
          <p className="text-sm text-gray-600 mb-2">Current Query</p>
          <p className="text-xl font-semibold text-gray-800">{query}</p>
        </motion.div>
      )}

      {/* Loading State */}
      {loading && (
        <motion.div
          className="space-y-6"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {[1, 2, 3].map((i) => (
            <motion.div
              key={i}
              className="p-6 bg-white rounded-lg border-2 border-gray-200 shadow-lg"
              variants={itemVariants}
            >
              <div className="flex items-center gap-4 mb-4">
                <motion.div
                  variants={pulseVariants}
                  animate="pulse"
                >
                  <Loader className="w-6 h-6 text-blue-600 animate-spin" />
                </motion.div>
                <div className="flex-1 h-4 bg-gradient-to-r from-gray-200 to-gray-300 rounded animate-pulse"></div>
              </div>
              <div className="space-y-2">
                <div className="h-3 bg-gradient-to-r from-gray-200 to-gray-300 rounded w-full animate-pulse"></div>
                <div className="h-3 bg-gradient-to-r from-gray-200 to-gray-300 rounded w-5/6 animate-pulse"></div>
              </div>
            </motion.div>
          ))}
          <motion.div
            className="text-center text-gray-600 font-semibold"
            variants={itemVariants}
          >
            🔍 Searching the web... 📖 Reading content... 🧠 Generating insights...
          </motion.div>
        </motion.div>
      )}

      {/* Summary Section */}
      {summary && !loading && (
        <motion.div
          className="space-y-6"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Executive Summary */}
          <motion.div
            className="p-8 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border-2 border-blue-300 shadow-lg hover:shadow-xl transition-shadow"
            variants={itemVariants}
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-center gap-3 mb-4">
              <motion.div
                initial={{ rotate: -180, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                transition={{ duration: 0.6 }}
              >
                <CheckCircle className="w-8 h-8 text-blue-600" />
              </motion.div>
              <h2 className="text-2xl font-bold text-gray-800">Executive Summary</h2>
            </div>
            <p className="text-gray-700 leading-relaxed text-lg">{summary}</p>
          </motion.div>

          {/* Top Insights */}
          {insights && insights.length > 0 && (
            <motion.div
              className="space-y-4"
              variants={itemVariants}
            >
              <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                <BookOpen className="w-6 h-6 text-purple-600" />
                Top Insights
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {insights.map((insight, index) => (
                  <motion.div
                    key={index}
                    className="p-5 bg-white rounded-lg border-2 border-purple-300 shadow-md hover:shadow-lg transition-shadow"
                    variants={itemVariants}
                    whileHover={{ scale: 1.05, translateY: -5 }}
                  >
                    <motion.div
                      className="flex items-start gap-3"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 text-white font-bold text-sm flex-shrink-0">
                        {index + 1}
                      </span>
                      <p className="text-gray-700 leading-relaxed">{insight}</p>
                    </motion.div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Relevant Memory Chunks */}
          {memoryChunks && memoryChunks.length > 0 && (
            <motion.div
              className="space-y-4"
              variants={itemVariants}
            >
              <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                <Archive className="w-6 h-6 text-amber-600" />
                Relevant Past Research Chunks
              </h2>
              <div className="space-y-3">
                {memoryChunks.map((chunk, index) => (
                  <motion.div
                    key={index}
                    className="p-5 bg-amber-50 rounded-lg border-2 border-amber-300 shadow-md hover:shadow-lg transition-shadow"
                    variants={itemVariants}
                    whileHover={{ scale: 1.01 }}
                  >
                    <div className="mb-2 flex justify-between items-start">
                      <h3 className="font-bold text-amber-900">{chunk.metadata?.title || 'Previous Research'}</h3>
                      <span className="text-xs bg-amber-200 px-3 py-1 rounded-full font-semibold text-amber-800">
                        {(chunk.similarity * 100).toFixed(0)}% Match
                      </span>
                    </div>
                    {chunk.metadata?.url && (
                      <p className="text-xs text-amber-700 mb-2 truncate">{chunk.metadata.url}</p>
                    )}
                    <p className="text-amber-900 text-sm leading-relaxed line-clamp-3">
                      {chunk.content}
                    </p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Past Research Memories */}
          {pastMemories && pastMemories.length > 0 && (
            <motion.div
              className="space-y-4"
              variants={itemVariants}
            >
              <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                <Zap className="w-6 h-6 text-yellow-600" />
                Related Past Research Summaries
              </h2>
              <div className="space-y-3">
                {pastMemories.map((memory, index) => (
                  <motion.div
                    key={index}
                    className="p-5 bg-yellow-50 rounded-lg border-2 border-yellow-300 shadow-md hover:shadow-lg transition-shadow"
                    variants={itemVariants}
                    whileHover={{ scale: 1.01 }}
                  >
                    <div className="mb-3 flex justify-between items-start">
                      <div>
                        <p className="text-xs text-gray-600 mb-1">Previous Query:</p>
                        <h3 className="font-bold text-gray-800">{memory.metadata?.query || 'Related Research'}</h3>
                      </div>
                      <span className="text-xs bg-yellow-200 px-3 py-1 rounded-full font-semibold text-yellow-800">
                        {(memory.similarity * 100).toFixed(0)}% Relevant
                      </span>
                    </div>
                    <p className="text-gray-700 text-sm leading-relaxed line-clamp-4">
                      {memory.summary}
                    </p>
                    {memory.metadata?.timestamp && (
                      <p className="text-xs text-gray-500 mt-2">
                        📅 {new Date(memory.metadata.timestamp).toLocaleDateString()}
                      </p>
                    )}
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Search Results */}
          {results && results.length > 0 && (
            <motion.div
              className="space-y-4"
              variants={itemVariants}
            >
              <h2 className="text-2xl font-bold text-gray-800">Research Sources ({results.length})</h2>
              <div className="space-y-3">
                {results.map((result, index) => (
                  <motion.div
                    key={index}
                    className="p-5 bg-white rounded-lg border-2 border-gray-200 shadow-md hover:shadow-lg transition-shadow cursor-pointer group"
                    variants={itemVariants}
                    whileHover={{ scale: 1.02, translateX: 5 }}
                    onClick={() => window.open(result.url, '_blank')}
                  >
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-bold text-lg text-gray-800 group-hover:text-blue-600 transition-colors line-clamp-2">
                            {result.title}
                          </h3>
                          <p className="text-sm text-blue-600 hover:underline truncate mb-2">{result.url}</p>
                          <p className="text-gray-600 text-sm leading-relaxed line-clamp-2">
                            {result.cleaned_text || result.snippet}
                          </p>
                        </div>
                        <motion.div
                          whileHover={{ rotate: 45, scale: 1.2 }}
                          className="text-gray-400 group-hover:text-blue-600 transition-colors flex-shrink-0"
                        >
                          ↗
                        </motion.div>
                      </div>
                    </motion.div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* New Search Button */}
          <motion.div
            className="flex justify-center"
            variants={itemVariants}
          >
            <motion.button
              onClick={onNewSearch}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-lg shadow-lg hover:shadow-xl transition-all"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              🔄 Start New Research
            </motion.button>
          </motion.div>
        </motion.div>
      )}

      {/* Error State */}
      {!loading && !summary && query && (
        <motion.div
          className="p-6 bg-red-50 rounded-lg border-2 border-red-300 flex items-center gap-3"
          variants={itemVariants}
        >
          <AlertCircle className="w-6 h-6 text-red-600" />
          <p className="text-red-700 font-semibold">Failed to complete research. Please try again.</p>
        </motion.div>
      )}
    </motion.div>
  );
};

export default ResearchContainer;
