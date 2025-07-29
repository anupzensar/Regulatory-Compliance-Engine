import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ size = 'w-5 h-5', text = 'Loading...' }) => {
  return (
    <div className="flex items-center space-x-2">
      <Loader2 className={`${size} animate-spin`} />
      <span className="text-sm">{text}</span>
    </div>
  );
};

export default LoadingSpinner;
