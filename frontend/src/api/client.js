/**
 * API client with Firebase authentication
 * Automatically includes ID token in Authorization header
 */

import { apiBaseUrl } from '../config';

const API_BASE_URL = apiBaseUrl;

/**
 * Make API request with Firebase token
 * 
 * Usage:
 * const data = await api('/research', {
 *   method: 'POST',
 *   body: { query: 'machine learning' }
 * });
 */
export async function api(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add Authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    // Handle 401 Unauthorized
    if (response.status === 401) {
      console.warn('⚠️  Unauthorized - clearing stored token');
      localStorage.removeItem('token');
      localStorage.removeItem('user_id');
      localStorage.removeItem('user_email');
      throw new Error('Authentication expired. Please login again.');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

/**
 * POST request helper
 */
export async function apiPost(endpoint, data) {
  return api(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * GET request helper
 */
export async function apiGet(endpoint) {
  return api(endpoint, {
    method: 'GET',
  });
}

/**
 * DELETE request helper
 */
export async function apiDelete(endpoint) {
  return api(endpoint, {
    method: 'DELETE',
  });
}

export default api;
