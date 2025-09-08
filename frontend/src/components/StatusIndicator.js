import React from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, AlertCircle, XCircle, RefreshCw } from 'lucide-react';

const StatusBar = styled(motion.div)`
  padding: 0.75rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.875rem;
  font-weight: 500;
  border-bottom: 1px solid #e5e7eb;
  
  ${props => props.status === 'healthy' && `
    background: linear-gradient(90deg, #d1fae5, #ecfdf5);
    color: #065f46;
    border-bottom-color: #a7f3d0;
  `}
  
  ${props => props.status === 'degraded' && `
    background: linear-gradient(90deg, #fef3c7, #fffbeb);
    color: #92400e;
    border-bottom-color: #fde68a;
  `}
  
  ${props => props.status === 'unhealthy' && `
    background: linear-gradient(90deg, #fecaca, #fef2f2);
    color: #991b1b;
    border-bottom-color: #fca5a5;
  `}
  
  ${props => props.status === 'error' && `
    background: linear-gradient(90deg, #fecaca, #fef2f2);
    color: #991b1b;
    border-bottom-color: #fca5a5;
  `}
`;

const StatusContent = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const StatusActions = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const RetryButton = styled.button`
  background: none;
  border: 1px solid currentColor;
  color: inherit;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  transition: all 0.2s ease;
  
  &:hover {
    background: currentColor;
    color: white;
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

function StatusIndicator({ status, onRetry }) {
  const getStatusConfig = () => {
    switch (status) {
      case 'healthy':
        return {
          icon: CheckCircle,
          message: 'VitaeAgent is ready and operational',
          showRetry: false
        };
      case 'degraded':
        return {
          icon: AlertCircle,
          message: 'VitaeAgent is running with limited functionality',
          showRetry: true
        };
      case 'unhealthy':
        return {
          icon: XCircle,
          message: 'VitaeAgent is experiencing issues',
          showRetry: true
        };
      case 'error':
        return {
          icon: XCircle,
          message: 'Unable to connect to VitaeAgent',
          showRetry: true
        };
      default:
        return {
          icon: RefreshCw,
          message: 'Checking VitaeAgent status...',
          showRetry: false
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  // Don't show status bar for healthy status after initial load
  if (status === 'healthy') {
    return null;
  }

  return (
    <AnimatePresence>
      <StatusBar
        status={status}
        initial={{ height: 0, opacity: 0 }}
        animate={{ height: 'auto', opacity: 1 }}
        exit={{ height: 0, opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        <StatusContent>
          <Icon size={16} />
          {config.message}
        </StatusContent>
        
        <StatusActions>
          {config.showRetry && onRetry && (
            <RetryButton onClick={onRetry}>
              <RefreshCw size={12} />
              Retry
            </RetryButton>
          )}
        </StatusActions>
      </StatusBar>
    </AnimatePresence>
  );
}

export default StatusIndicator;