import React from 'react';
import { X } from 'lucide-react';
import './Alert.css';

function Alert({ type = 'info', message, onClose }) {
  if (!message) return null;

  return (
    <div className={`alert alert-${type}`}>
      <div className="alert-content">{message}</div>
      {onClose && (
        <button className="alert-close" onClick={onClose}>
          <X size={18} />
        </button>
      )}
    </div>
  );
}

export default Alert;
