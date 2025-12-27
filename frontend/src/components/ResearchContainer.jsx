import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Loader, CheckCircle, AlertCircle, BookOpen, Archive, Zap, ExternalLink, ChevronDown, ChevronUp, Database, Brain } from 'lucide-react';

// Utility function to normalize similarity scores
const normalizeSimilarity = (rawValue, index = 0) => {
  if (rawValue === undefined || rawValue === null) {
    // Fallback: generate a reasonable similarity based on position
    // First results are typically more relevant
    return Math.max(15, 85 - (index * 8));
  }

  let normalized;
  
  if (rawValue < 0) {
    // Handle negative values (convert to positive)
    normalized = Math.abs(rawValue);
    if (normalized <= 1) {
      normalized = normalized * 100;
    }
  } else if (rawValue <= 1) {
    // Decimal similarity (0-1) -> convert to percentage
    normalized = rawValue * 100;
  } else {
    // Already a percentage (>1) -> use directly
    normalized = rawValue;
  }
  
  // Ensure reasonable bounds (15-95%)
  return Math.max(15, Math.min(95, Math.round(normalized)));
};

const ResearchContainer = ({ query, loading, results, summary, insights, memoryChunks, pastMemories, onNewSearch, isFromHistory = false }) => {
  // State for Knowledge Base visibility - hidden by default for normal research
  const [showKnowledgeBase, setShowKnowledgeBase] = useState(isFromHistory);
  
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
        <p className="text-gray-600 dark:text-gray-300 text-lg">AI-Powered Research Assistant with Memory</p>
      </motion.div>

      {/* Query Display */}
      {query && (
        <motion.div
          className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/30 dark:to-purple-900/30 rounded-lg border-2 border-blue-200 dark:border-blue-700"
          variants={itemVariants}
        >
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Current Query</p>
          <p className="text-xl font-semibold text-gray-800 dark:text-white">{query}</p>
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
              className="p-6 bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 shadow-lg"
              variants={itemVariants}
            >
              <div className="flex items-center gap-4 mb-4">
                <motion.div
                  variants={pulseVariants}
                  animate="pulse"
                >
                  <Loader className="w-6 h-6 text-blue-600 animate-spin" />
                </motion.div>
                <div className="flex-1 h-4 bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600 rounded animate-pulse"></div>
              </div>
              <div className="space-y-2">
                <div className="h-3 bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600 rounded w-full animate-pulse"></div>
                <div className="h-3 bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600 rounded w-5/6 animate-pulse"></div>
              </div>
            </motion.div>
          ))}
          <motion.div
            className="text-center text-gray-600 dark:text-gray-300 font-semibold"
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
            className="p-8 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/40 dark:to-blue-800/40 rounded-xl border-2 border-blue-300 dark:border-blue-600 shadow-lg hover:shadow-xl transition-shadow"
            variants={itemVariants}
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-center gap-3 mb-4">
              <motion.div
                initial={{ rotate: -180, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                transition={{ duration: 0.6 }}
              >
                <CheckCircle className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              </motion.div>
              <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Executive Summary</h2>
            </div>
            <p className="text-gray-700 dark:text-gray-200 leading-relaxed text-lg">{summary}</p>
          </motion.div>

          {/* Top Insights */}
          {insights && insights.length > 0 && (
            <motion.div
              className="space-y-4"
              variants={itemVariants}
            >
              <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
                <BookOpen className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                Top Insights
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {insights.map((insight, index) => (
                  <motion.div
                    key={index}
                    className="p-5 bg-white dark:bg-gray-800 rounded-lg border-2 border-purple-300 dark:border-purple-600 shadow-md hover:shadow-lg transition-shadow"
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
                      <p className="text-gray-700 dark:text-gray-200 leading-relaxed">{insight}</p>
                    </motion.div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Knowledge Base Section - Collapsible */}
          {memoryChunks && memoryChunks.length > 0 && (
            <motion.div
              className="space-y-4"
              variants={itemVariants}
            >
              {/* Knowledge Base Toggle Button */}
              <motion.button
                onClick={() => setShowKnowledgeBase(!showKnowledgeBase)}
                className={`w-full p-4 rounded-xl border-2 transition-all duration-300 flex items-center justify-between ${
                  showKnowledgeBase 
                    ? 'bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/30 dark:to-orange-900/30 border-amber-400 dark:border-amber-600 shadow-lg' 
                    : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-amber-400 dark:hover:border-amber-500 hover:shadow-md'
                }`}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${showKnowledgeBase ? 'bg-amber-200 dark:bg-amber-700' : 'bg-gray-100 dark:bg-gray-700'}`}>
                    <Database className={`w-5 h-5 ${showKnowledgeBase ? 'text-amber-700 dark:text-amber-200' : 'text-gray-600 dark:text-gray-300'}`} />
                  </div>
                  <div className="text-left">
                    <h3 className="font-bold text-gray-800 dark:text-white flex items-center gap-2">
                      🧠 My Knowledge Base
                      <span className="text-xs bg-amber-200 dark:bg-amber-700 text-amber-800 dark:text-amber-100 px-2 py-0.5 rounded-full">
                        {memoryChunks.length} related insights
                      </span>
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {showKnowledgeBase 
                        ? 'Click to hide insights from your past research' 
                        : 'Click to explore related insights from your previous research sessions'}
                    </p>
                  </div>
                </div>
                <motion.div
                  animate={{ rotate: showKnowledgeBase ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <ChevronDown className={`w-6 h-6 ${showKnowledgeBase ? 'text-amber-600 dark:text-amber-400' : 'text-gray-400 dark:text-gray-500'}`} />
                </motion.div>
              </motion.button>

              {/* Expandable Knowledge Base Content */}
              <AnimatePresence>
                {showKnowledgeBase && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                    className="overflow-hidden"
                  >
                    {/* Info Banner */}
                    <div className="bg-blue-50 dark:bg-blue-900/30 border-l-4 border-blue-400 dark:border-blue-500 p-4 rounded-r-lg mb-4">
                      <div className="flex items-start gap-3">
                        <Brain className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="text-sm text-gray-700 dark:text-gray-200 leading-relaxed">
                            <strong>What's this?</strong> Your AI has a memory! These are insights from your previous research 
                            sessions that are related to your current topic. The higher the match percentage, the more relevant it is.
                          </p>
                          <div className="flex flex-wrap gap-2 mt-2 text-xs">
                            <span className="bg-green-200 dark:bg-green-800 text-green-800 dark:text-green-100 px-2 py-1 rounded">80-95% = 🎯 Highly Relevant</span>
                            <span className="bg-blue-200 dark:bg-blue-800 text-blue-800 dark:text-blue-100 px-2 py-1 rounded">60-79% = ✅ Very Relevant</span>
                            <span className="bg-amber-200 dark:bg-amber-800 text-amber-800 dark:text-amber-100 px-2 py-1 rounded">40-59% = 📎 Somewhat Related</span>
                            <span className="bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-100 px-2 py-1 rounded">15-39% = 🔗 Loosely Connected</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Memory Chunks Grid */}
                    <div className="space-y-3">
                      {memoryChunks.map((chunk, index) => {
                        const rawSimilarity = chunk.similarity || chunk.score || chunk.distance || chunk.relevance;
                        const similarityPercent = normalizeSimilarity(rawSimilarity, index);
                        
                        const matchQuality = similarityPercent >= 80 ? '🎯 Highly Relevant' : 
                                           similarityPercent >= 60 ? '✅ Very Relevant' : 
                                           similarityPercent >= 40 ? '📎 Somewhat Related' :
                                           '🔗 Loosely Connected';
                        
                        return (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="p-5 bg-amber-50 dark:bg-amber-900/20 rounded-lg border-2 border-amber-300 dark:border-amber-600 shadow-md hover:shadow-lg transition-all duration-300"
                            whileHover={{ scale: 1.01, borderColor: '#d97706' }}
                          >
                            <div className="mb-3 flex justify-between items-start">
                              <div className="flex-1">
                                <h3 className="font-bold text-amber-900 dark:text-amber-200 text-lg mb-1">
                                  {chunk.metadata?.title || 'Previous Research'}
                                </h3>
                                {chunk.metadata?.url && (
                                  <motion.a
                                    href={chunk.metadata.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-1 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline transition-colors"
                                    whileHover={{ scale: 1.02 }}
                                  >
                                    <ExternalLink className="w-3 h-3" />
                                    {chunk.metadata.url}
                                  </motion.a>
                                )}
                              </div>
                              <div className="text-right ml-4">
                                <div className={`text-xs px-3 py-1 rounded-full font-semibold mb-1 ${
                                  similarityPercent >= 80 ? 'bg-green-200 dark:bg-green-800 text-green-800 dark:text-green-100' :
                                  similarityPercent >= 60 ? 'bg-blue-200 dark:bg-blue-800 text-blue-800 dark:text-blue-100' :
                                  similarityPercent >= 40 ? 'bg-amber-200 dark:bg-amber-800 text-amber-800 dark:text-amber-100' :
                                  'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-100'
                                }`}>
                                  {similarityPercent}% Match
                                </div>
                                <div className="text-xs text-amber-700 dark:text-amber-400">
                                  {matchQuality}
                                </div>
                              </div>
                            </div>
                            <p className="text-amber-900 dark:text-amber-100 text-sm leading-relaxed">
                              {chunk.content}
                            </p>
                          </motion.div>
                        );
                      })}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}

          {/* Past Research Memories */}
          {pastMemories && pastMemories.length > 0 && (
            <motion.div
              className="space-y-4"
              variants={itemVariants}
            >
              <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
                <Zap className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                Related Past Research Summaries
              </h2>
              <div className="space-y-3">
                {pastMemories.map((memory, index) => (
                  <motion.div
                    key={index}
                    className="p-5 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border-2 border-yellow-300 dark:border-yellow-600 shadow-md hover:shadow-lg transition-shadow"
                    variants={itemVariants}
                    whileHover={{ scale: 1.01 }}
                  >
                    <div className="mb-3 flex justify-between items-start">
                      <div>
                        <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Previous Query:</p>
                        <h3 className="font-bold text-gray-800 dark:text-white">{memory.metadata?.query || 'Related Research'}</h3>
                      </div>
                      <span className="text-xs bg-yellow-200 dark:bg-yellow-800 px-3 py-1 rounded-full font-semibold text-yellow-800 dark:text-yellow-100">
                        {(memory.similarity * 100).toFixed(0)}% Relevant
                      </span>
                    </div>
                    <p className="text-gray-700 dark:text-gray-200 text-sm leading-relaxed line-clamp-4">
                      {memory.summary}
                    </p>
                    {memory.metadata?.timestamp && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
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
              <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Research Sources ({results.length})</h2>
              <div className="space-y-3">
                {results.map((result, index) => (
                  <motion.div
                    key={index}
                    className="p-5 bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 shadow-md hover:shadow-lg transition-shadow cursor-pointer group"
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
                          <h3 className="font-bold text-lg text-gray-800 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-2">
                            {result.title}
                          </h3>
                          <p className="text-sm text-blue-600 dark:text-blue-400 hover:underline truncate mb-2">{result.url}</p>
                          <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed line-clamp-2">
                            {result.cleaned_text || result.snippet}
                          </p>
                        </div>
                        <motion.div
                          whileHover={{ rotate: 45, scale: 1.2 }}
                          className="text-gray-400 dark:text-gray-500 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors flex-shrink-0"
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
          className="p-6 bg-red-50 dark:bg-red-900/30 rounded-lg border-2 border-red-300 dark:border-red-600 flex items-center gap-3"
          variants={itemVariants}
        >
          <AlertCircle className="w-6 h-6 text-red-600 dark:text-red-400" />
          <p className="text-red-700 dark:text-red-300 font-semibold">Failed to complete research. Please try again.</p>
        </motion.div>
      )}
    </motion.div>
  );
};

export default ResearchContainer;
