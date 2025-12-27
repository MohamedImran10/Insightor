import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react';

const Toast = ({ type = 'info', message, onClose, autoClose = true }) => {
  const icons = {
    success: CheckCircle,
    error: XCircle,
    warning: AlertCircle,
    info: Info
  };

  // Color classes include dark-mode variants for good contrast in both themes
  const colors = {
    success:
      'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/70 dark:border-green-700 dark:text-green-100',
    error:
      'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/70 dark:border-red-700 dark:text-red-100',
    warning:
      'bg-yellow-50 border-yellow-200 text-yellow-800 dark:bg-yellow-900/60 dark:border-yellow-700 dark:text-yellow-100',
    info:
      'bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-900/70 dark:border-blue-700 dark:text-blue-100'
  };

  const iconColors = {
    success: 'text-green-600 dark:text-green-300',
    error: 'text-red-600 dark:text-red-300',
    warning: 'text-yellow-600 dark:text-yellow-300',
    info: 'text-blue-600 dark:text-blue-300'
  };

  const Icon = icons[type];

  // Auto-close after 5 seconds
  React.useEffect(() => {
    if (autoClose) {
      const timer = setTimeout(() => {
        onClose();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [autoClose, onClose]);

  return (
    <motion.div
      initial={{ opacity: 0, y: -50, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -50, scale: 0.95 }}
      // place the toast below the header so it doesn't visually obscure the user name
      className={`fixed top-20 right-4 z-50 p-4 rounded-lg border-2 shadow-lg min-w-[300px] max-w-md ${colors[type]}`}
    >
      <div className="flex items-start gap-3">
        <Icon className={`w-5 h-5 flex-shrink-0 mt-0.5 ${iconColors[type]}`} />
        <div className="flex-1">
          <p className="text-sm font-medium break-words">{message}</p>
        </div>
        <button
          onClick={onClose}
          className={`p-1 rounded transition-colors ${iconColors[type]} hover:bg-black/10 dark:hover:bg-white/10`}
          aria-label="Close notification"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  );
};

export default Toast;