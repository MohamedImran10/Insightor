/**
 * History API - Helper functions for search history endpoints
 * 
 * Handles:
 * - Fetching user's search history
 * - Saving new search entries
 * - Deleting history entries
 */

import { api } from './client';

/**
 * Fetch user's search history
 * @param {string} userId - User ID (must be authenticated)
 * @param {number} limit - Maximum number of entries to return (default: 50)
 * @returns {Promise<Array>} Array of history entries
 */
export const getHistory = async (userId, limit = 50) => {
  try {
    const response = await api.get(`/history/${userId}?limit=${limit}`);
    
    if (response.data?.status === 'success') {
      return response.data.history || [];
    }
    return [];
  } catch (error) {
    console.error('❌ Error fetching history:', error);
    throw error;
  }
};

/**
 * Save a search to user's history
 * @param {Object} data - History entry data
 * @param {string} data.query - Search query
 * @param {string} data.response - Research response/summary
 * @param {Array} data.sources - List of sources used
 * @param {Array} data.search_results - Search results from Tavily (optional)
 * @param {Array} data.insights - Extracted insights (optional)
 * @param {Array} data.memory_chunks - Related memory chunks (optional)
 * @returns {Promise<boolean>} Success status
 */
export const saveHistory = async (data) => {
  try {
    const response = await api.post('/history/save', data);
    
    if (response.data?.saved) {
      console.log('✅ History saved successfully');
      return true;
    }
    return false;
  } catch (error) {
    console.error('❌ Error saving history:', error);
    throw error;
  }
};

/**
 * Delete a specific history entry
 * @param {string} userId - User ID
 * @param {string} entryId - History entry ID to delete
 * @returns {Promise<boolean>} Success status
 */
export const deleteHistoryEntry = async (userId, entryId) => {
  try {
    const response = await api.delete(`/history/${userId}/${entryId}`);
    
    if (response.data?.deleted) {
      console.log('✅ History entry deleted');
      return true;
    }
    return false;
  } catch (error) {
    console.error('❌ Error deleting history:', error);
    throw error;
  }
};

/**
 * Clear all history entries for a user
 * @param {string} userId - User ID
 * @param {Array} historyItems - All history items to delete
 * @returns {Promise<number>} Number of entries deleted
 */
export const clearAllHistory = async (userId, historyItems) => {
  try {
    let deletedCount = 0;
    
    for (const item of historyItems) {
      const success = await deleteHistoryEntry(userId, item.id);
      if (success) deletedCount++;
    }
    
    console.log(`✅ Deleted ${deletedCount} history entries`);
    return deletedCount;
  } catch (error) {
    console.error('❌ Error clearing history:', error);
    throw error;
  }
};

export default {
  getHistory,
  saveHistory,
  deleteHistoryEntry,
  clearAllHistory
};
