import React from 'react';
import { AlertCircle, CheckCircle, XCircle } from 'lucide-react';

const Toast = ({ type, message, onClose }) => {
  const getToastStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-green-600 border-green-500';
      case 'error':
        return 'bg-red-600 border-red-500';
      case 'info':
        return 'bg-blue-600 border-blue-500';
      default:
        return 'bg-gray-600 border-gray-500';
    }
  };

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5" />;
      case 'error':
        return <XCircle className="w-5 h-5" />;
      case 'info':
        return <AlertCircle className="w-5 h-5" />;
      default:
        return <AlertCircle className="w-5 h-5" />;
    }
  };

  return (
    <div className={`fixed top-4 right-4 max-w-sm p-4 rounded-lg border ${getToastStyles()} text-white shadow-lg z-50 animate-slide-in`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {getIcon()}
          <span className="text-sm font-medium">{message}</span>
        </div>
        <button
          onClick={onClose}
          className="ml-4 text-white hover:text-gray-200 focus:outline-none"
        >
          <XCircle className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default Toast;
