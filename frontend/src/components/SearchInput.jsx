import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Send, Sparkles, Loader } from 'lucide-react';
import { useToast } from '../hooks/useToast';

const SearchInput = ({ onSubmit, loading }) => {
  const [query, setQuery] = useState('');
  const inputRef = useRef(null);
  const { warning } = useToast();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) {
      warning('Please enter a search query to begin your research');
      return;
    }
    if (!loading) {
      onSubmit(query);
      setQuery('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: 'easeOut' },
    },
    focus: {
      scale: 1.02,
      transition: { duration: 0.3 },
    },
  };

  const buttonVariants = {
    hidden: { scale: 0, opacity: 0 },
    visible: {
      scale: 1,
      opacity: 1,
      transition: { duration: 0.4, delay: 0.3 },
    },
    hover: { scale: 1.1 },
    tap: { scale: 0.9 },
  };

  const placeholders = [
    'What are the latest developments in AI?',
    'How does machine learning work?',
    'What is the future of technology?',
    'Tell me about cybersecurity threats',
    'Explain blockchain technology',
  ];

  const [placeholderIndex, setPlaceholderIndex] = React.useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((prev) => (prev + 1) % placeholders.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      className="w-full max-w-4xl mx-auto px-4"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <form onSubmit={handleSubmit} className="relative">
        <motion.div
          className="relative flex items-center gap-2"
          whileFocus="focus"
          variants={containerVariants}
        >
          {/* Main Input Field */}
          <motion.div
            className="flex-1 relative"
            initial={{ boxShadow: 'none' }}
            whileFocus={{
              boxShadow: '0 20px 60px rgba(59, 130, 246, 0.3)',
            }}
          >
            <motion.input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholders[placeholderIndex]}
              disabled={loading}
              className="w-full px-6 py-4 text-lg bg-white dark:bg-gray-800 text-gray-800 dark:text-white border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:ring-2 focus:ring-blue-200 dark:focus:ring-blue-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed placeholder:text-gray-400 dark:placeholder:text-gray-500"
              initial={{ borderColor: '#d1d5db' }}
              animate={{
                borderColor: loading ? '#ef4444' : '#d1d5db',
              }}
            />

            {/* Animated border glow on focus */}
            <motion.div
              className="absolute inset-0 rounded-xl pointer-events-none"
              initial={{ boxShadow: 'none' }}
              whileFocus={{
                boxShadow: 'inset 0 0 0 2px #3b82f6, 0 0 20px rgba(59, 130, 246, 0.2)',
              }}
            />
          </motion.div>

          {/* Send Button */}
          <motion.button
            type="submit"
            disabled={loading || !query.trim()}
            variants={buttonVariants}
            initial="hidden"
            animate="visible"
            whileHover={!loading ? 'hover' : {}}
            whileTap={!loading ? 'tap' : {}}
            className="px-6 py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold rounded-xl shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity }}>
                <Loader className="w-5 h-5" />
              </motion.div>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span className="hidden sm:inline text-sm">Search</span>
              </>
            )}
          </motion.button>
        </motion.div>

        {/* Suggestion Chips */}
        {!query && !loading && (
          <motion.div
            className="mt-3 flex flex-wrap gap-2 justify-center"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            {['AI', 'Machine Learning', 'Tech News', 'Science'].map((chip, index) => (
              <motion.button
                key={chip}
                type="button"
                onClick={() => setQuery(chip)}
                className="px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-blue-100 dark:hover:bg-blue-900/50 text-gray-700 dark:text-gray-300 hover:text-blue-700 dark:hover:text-blue-300 rounded-full text-sm font-medium transition-colors"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 + index * 0.05 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {chip}
              </motion.button>
            ))}
          </motion.div>
        )}

        {/* Loading Message */}
        {loading && (
          <motion.div
            className="mt-4 text-center text-gray-600 dark:text-gray-300 flex items-center justify-center gap-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            >
              <Sparkles className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            </motion.div>
            <span>Researching your query...</span>
          </motion.div>
        )}
      </form>
    </motion.div>
  );
};

export default SearchInput;
