import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext(null);

export const ThemeProvider = ({ children }) => {
  const [darkMode, setDarkMode] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  // Apply theme to DOM
  const applyTheme = (isDark) => {
    if (isDark) {
      document.documentElement.classList.add('dark');
      document.body.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
      document.body.classList.remove('dark');
    }
  };

  // Initialize theme on mount only
  useEffect(() => {
    // Get saved theme preference from localStorage
    const savedTheme = localStorage.getItem('darkMode');
    const isDark = savedTheme === 'true';
    
    // Check current DOM state
    const isDomDark = document.documentElement.classList.contains('dark');
    
    // Use localStorage value as source of truth
    const actualTheme = isDark;
    
    setDarkMode(actualTheme);
    applyTheme(actualTheme);
    
    setIsInitialized(true);
    console.log('Theme initialized from localStorage:', actualTheme ? 'dark' : 'light');
  }, []);

  // Update DOM and localStorage when darkMode state changes
  useEffect(() => {
    if (!isInitialized) return;
    
    applyTheme(darkMode);
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    
    console.log('Theme toggled to:', darkMode ? 'dark' : 'light');
  }, [darkMode, isInitialized]);

  // Monitor DOM changes and sync state (for when Login/Signup remove dark class)
  useEffect(() => {
    const observer = new MutationObserver(() => {
      const isDomDark = document.documentElement.classList.contains('dark');
      // Only update if we're initialized and there's a mismatch
      if (isInitialized && isDomDark !== darkMode) {
        console.log('DOM mismatch detected, syncing:', isDomDark ? 'dark' : 'light');
        setDarkMode(isDomDark);
        localStorage.setItem('darkMode', JSON.stringify(isDomDark));
      }
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    });

    return () => observer.disconnect();
  }, [isInitialized, darkMode]);

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
