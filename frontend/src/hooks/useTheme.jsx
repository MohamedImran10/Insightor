import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext(null);

export const ThemeProvider = ({ children }) => {
  const [darkMode, setDarkMode] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize theme on mount only
  useEffect(() => {
    // Get saved theme preference
    const savedTheme = localStorage.getItem('darkMode');
    const isDark = savedTheme === 'true';
    
    // Set state
    setDarkMode(isDark);
    
    // Apply to document
    if (isDark) {
      document.documentElement.classList.add('dark');
      document.body.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
      document.body.classList.remove('dark');
    }
    
    setIsInitialized(true);
    console.log('Theme initialized:', isDark ? 'dark' : 'light');
  }, []);

  // Update DOM when darkMode state changes
  useEffect(() => {
    if (!isInitialized) return;
    
    if (darkMode) {
      console.log('Applying dark mode');
      document.documentElement.classList.add('dark');
      document.body.classList.add('dark');
    } else {
      console.log('Applying light mode');
      document.documentElement.classList.remove('dark');
      document.body.classList.remove('dark');
    }
    
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode, isInitialized]);

  const toggleDarkMode = () => {
    console.log('Toggling dark mode from', darkMode, 'to', !darkMode);
    setDarkMode(prev => !prev);
  };

  return (
    <ThemeContext.Provider value={{ darkMode, setDarkMode, toggleDarkMode }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export default useTheme;
