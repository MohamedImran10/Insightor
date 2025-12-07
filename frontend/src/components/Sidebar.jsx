import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Plus, MessageSquare, Trash2 } from 'lucide-react';
import { motion } from 'framer-motion';
import HistoryItem from './HistoryItem';

// Sidebar component - simple version
export default function Sidebar({
  isOpen = true,
  onToggle,
  onNewSearch,
  history = [],
  currentHistoryId = null,
  onHistoryItemClick,
  onDeleteHistoryItem,
  user = null,
  isLoadingHistory = false
}) {
  return (
    <>
      {isOpen && (
        <motion.div
          initial={{ x: -300 }}
          animate={{ x: 0 }}
          exit={{ x: -300 }}
          transition={{ duration: 0.3 }}
          className="fixed left-0 top-0 h-screen w-[300px] bg-gray-900 border-r border-gray-700 overflow-hidden z-30"
        >
          <div className="h-full flex flex-col p-4">
            <button onClick={onToggle} className="mb-4 p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-white">
              <ChevronLeft size={20} />
            </button>
            <button onClick={onNewSearch} className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-white font-medium mb-4">
              <Plus size={18} />
              New Search
            </button>
            {user && (
              <div className="p-3 bg-gray-800 rounded-lg mb-4">
                <p className="text-sm text-white truncate">{user.email}</p>
              </div>
            )}
            <div className="flex-1 overflow-y-auto">
              {isLoadingHistory ? (
                <p className="text-gray-400 text-sm">Loading...</p>
              ) : history.length === 0 ? (
                <p className="text-gray-400 text-sm">No history</p>
              ) : (
                history.map(item => (
                  <div key={item.id} className="p-2 bg-gray-800 rounded mb-2 text-gray-200 text-sm truncate">
                    {item.query}
                  </div>
                ))
              )}
            </div>
          </div>
        </motion.div>
      )}
      {!isOpen && (
        <motion.button onClick={onToggle} className="fixed left-0 top-4 p-2 bg-gray-900 rounded-r-lg text-gray-400 z-30">
          <ChevronRight size={20} />
        </motion.button>
      )}
      {isOpen && (
        <div onClick={onToggle} className="fixed inset-0 bg-black/20 z-20 lg:hidden" />
      )}
    </>
  );
}
