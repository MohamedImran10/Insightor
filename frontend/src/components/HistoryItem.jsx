import React from 'react';
import { MessageSquare } from 'lucide-react';
import { motion } from 'framer-motion';

/**
 * HistoryItem Component - Individual history entry in sidebar
 * 
 * Features:
 * - Display query text (truncated with ellipsis)
 * - Show timestamp
 * - Highlight if active
 * - Hover animation
 */
export default function HistoryItem({
  query = '',
  timestamp = null,
  isActive = false,
  onClick = () => {}
}) {
  // Format timestamp
  const formatTimestamp = (date) => {
    if (!date) return '';
    
    const d = date instanceof Date ? date : new Date(date);
    const now = new Date();
    const diffMs = now - d;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;

    // Format as date
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Truncate query text
  const truncateText = (text, maxLength = 40) => {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`
        w-full text-left p-3 rounded-lg transition-all duration-200
        ${
          isActive
            ? 'bg-blue-600 text-white shadow-lg'
            : 'bg-gray-800 text-gray-200 hover:bg-gray-700'
        }
      `}
      title={query}
    >
      <div className="flex items-start gap-2">
        {/* Icon */}
        <MessageSquare 
          size={16} 
          className={`flex-shrink-0 mt-0.5 ${isActive ? 'text-white' : 'text-gray-400'}`}
        />

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Query Text */}
          <p className="text-sm font-medium truncate leading-tight">
            {truncateText(query)}
          </p>

          {/* Timestamp */}
          {timestamp && (
            <p className={`text-xs mt-1 ${isActive ? 'text-blue-100' : 'text-gray-500'}`}>
              {formatTimestamp(timestamp)}
            </p>
          )}
        </div>
      </div>
    </motion.button>
  );
}
