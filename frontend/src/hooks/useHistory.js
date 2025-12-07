import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

/**
 * useHistory Hook - Manage user search history
 * 
 * Features:
 * - Fetch user's search history from Firestore
 * - Save new search entries
 * - Delete history entries
 * - Auto-load on user change
 */
export function useHistory(userId) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentHistoryId, setCurrentHistoryId] = useState(null);

  // Fetch search history
  const fetchHistory = useCallback(async (uid = userId, limit = 50) => {
    if (!uid) {
      console.warn('⚠️ No user ID provided for fetching history');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log(`📖 Fetching search history for user ${uid.substring(0, 8)}...`);
      
      const response = await api.get(`/history/${uid}?limit=${limit}`);
      
      if (response.data?.status === 'success') {
        setHistory(response.data.history || []);
        console.log(`✅ Loaded ${response.data.history?.length || 0} history entries`);
      } else {
        console.warn('⚠️ Unexpected response format:', response.data);
        setHistory([]);
      }
    } catch (err) {
      console.error('❌ Error fetching history:', err);
      setError(err.message || 'Failed to fetch history');
      setHistory([]);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Save search to history
  const saveToHistory = useCallback(async (
    query,
    response,
    sources = [],
    searchResults = null,
    insights = null,
    memoryChunks = null
  ) => {
    if (!userId) {
      console.warn('⚠️ No user ID provided for saving history');
      return false;
    }

    try {
      console.log(`💾 Saving search to history: ${query.substring(0, 50)}...`);
      
      const payload = {
        query,
        response,
        sources,
        search_results: searchResults,
        insights,
        memory_chunks: memoryChunks
      };

      const response_data = await api.post('/history/save', payload);
      
      if (response_data.data?.saved) {
        console.log('✅ Search saved to history');
        // Refresh history to get new entry
        await fetchHistory(userId);
        return true;
      } else {
        console.warn('⚠️ History save returned false:', response_data.data);
        return false;
      }
    } catch (err) {
      console.error('❌ Error saving to history:', err);
      setError(err.message || 'Failed to save history');
      return false;
    }
  }, [userId, fetchHistory]);

  // Delete history entry
  const deleteHistoryEntry = useCallback(async (entryId) => {
    if (!userId) {
      console.warn('⚠️ No user ID provided for deleting history');
      return false;
    }

    try {
      console.log(`🗑️ Deleting history entry ${entryId}`);
      
      const response = await api.delete(`/history/${userId}/${entryId}`);
      
      if (response.data?.deleted) {
        console.log('✅ History entry deleted');
        // Remove from local state
        setHistory(prev => prev.filter(item => item.id !== entryId));
        return true;
      } else {
        console.warn('⚠️ Delete failed:', response.data);
        return false;
      }
    } catch (err) {
      console.error('❌ Error deleting history:', err);
      setError(err.message || 'Failed to delete history');
      return false;
    }
  }, [userId]);

  // Clear all history
  const clearAllHistory = useCallback(async () => {
    if (!userId) {
      console.warn('⚠️ No user ID provided for clearing history');
      return false;
    }

    try {
      console.log(`🗑️ Clearing all history for user ${userId.substring(0, 8)}`);
      
      // Delete all entries
      for (const entry of history) {
        await deleteHistoryEntry(entry.id);
      }
      
      console.log('✅ All history cleared');
      return true;
    } catch (err) {
      console.error('❌ Error clearing history:', err);
      setError(err.message || 'Failed to clear history');
      return false;
    }
  }, [userId, history, deleteHistoryEntry]);

  // Auto-fetch history when userId changes - DISABLED for now to prevent crashes
  useEffect(() => {
    if (userId) {
      console.log(`📖 useHistory: User detected ${userId.substring(0, 8)}, but auto-fetch disabled for safety`);
      // TODO: Re-enable when backend is stable
      // fetchHistory(userId);
      setHistory([]); // Empty for now
    } else {
      console.log('⚠️ useHistory: No userId provided, skipping fetch');
      setHistory([]);
    }
  }, [userId]);

  return {
    history,
    loading,
    error,
    currentHistoryId,
    setCurrentHistoryId,
    fetchHistory,
    saveToHistory,
    deleteHistoryEntry,
    clearAllHistory
  };
}

export default useHistory;
