import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { Send, Loader, AlertCircle, CheckCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { vitaeApi } from '../services/api';
import MessageBubble from './MessageBubble';
import SuggestedQuestions from './SuggestedQuestions';
import StatusIndicator from './StatusIndicator';

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  scroll-behavior: smooth;
`;

const InputContainer = styled.div`
  padding: 1.5rem 2rem 2rem 2rem;
  border-top: 1px solid #e1e5e9;
  background: white;
`;

const InputWrapper = styled.div`
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  position: relative;
`;

const TextInput = styled.textarea`
  flex: 1;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  font-size: 1rem;
  font-family: inherit;
  resize: none;
  min-height: 50px;
  max-height: 120px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  &::placeholder {
    color: #9ca3af;
  }
`;

const SendButton = styled.button`
  background: ${props => props.disabled ? '#e5e7eb' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
  color: white;
  border: none;
  border-radius: 12px;
  padding: 1rem;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  min-width: 50px;
  height: 50px;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
`;

const WelcomeMessage = styled.div`
  text-align: center;
  padding: 2rem;
  color: #6b7280;
`;

const WelcomeTitle = styled.h2`
  font-size: 1.5rem;
  color: #374151;
  margin-bottom: 1rem;
  font-weight: 600;
`;

const WelcomeText = styled.p`
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
`;

const ErrorMessage = styled(motion.div)`
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
`;

function Chat() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [agentStatus, setAgentStatus] = useState('unknown');
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check agent health on mount
  useEffect(() => {
    checkAgentHealth();
    loadSuggestedQuestions();
  }, []);

  const checkAgentHealth = async () => {
    try {
      const health = await vitaeApi.checkHealth();
      setAgentStatus(health.status);
    } catch (error) {
      console.error('Health check failed:', error);
      setAgentStatus('error');
    }
  };

  const loadSuggestedQuestions = async () => {
    try {
      const questions = await vitaeApi.getSuggestedQuestions();
      setSuggestedQuestions(questions);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    }
  };

  const handleSubmit = async (messageText = inputValue) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await vitaeApi.sendMessage(messageText);
      
      const agentMessage = {
        id: Date.now() + 1,
        type: 'agent',
        content: response.response,
        sources: response.sources || [],
        sourceCount: response.source_count || 0,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setError(error.message);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'I apologize, but I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSuggestedQuestionClick = (question) => {
    handleSubmit(question);
  };

  const dismissError = () => {
    setError(null);
  };

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [inputValue]);

  return (
    <ChatContainer>
      <StatusIndicator status={agentStatus} onRetry={checkAgentHealth} />
      
      <MessagesContainer>
        <AnimatePresence>
          {error && (
            <ErrorMessage
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              onClick={dismissError}
            >
              <AlertCircle size={20} />
              {error}
              <button style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer' }}>
                ×
              </button>
            </ErrorMessage>
          )}
        </AnimatePresence>

        {messages.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <WelcomeMessage>
              <WelcomeTitle>👋 Welcome to VitaeAgent</WelcomeTitle>
              <WelcomeText>
                I'm your intelligent digital professional persona. Ask me anything about my background, 
                experience, projects, skills, or career journey. I'll provide detailed, cited responses 
                based on my comprehensive knowledge base.
              </WelcomeText>
              <SuggestedQuestions
                questions={suggestedQuestions}
                onQuestionClick={handleSuggestedQuestionClick}
                disabled={isLoading || agentStatus === 'error'}
              />
            </WelcomeMessage>
          </motion.div>
        ) : (
          messages.map(message => (
            <MessageBubble
              key={message.id}
              message={message}
            />
          ))
        )}

        {isLoading && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            style={{ display: 'flex', justifyContent: 'center', padding: '1rem' }}
          >
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.5rem',
              background: 'white',
              padding: '0.75rem 1.25rem',
              borderRadius: '20px',
              boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
            }}>
              <Loader size={16} className="animate-spin" />
              <span style={{ color: '#6b7280', fontSize: '0.9rem' }}>
                VitaeAgent is thinking...
              </span>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputContainer>
        <InputWrapper>
          <TextInput
            ref={textareaRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about my experience, skills, projects, or background..."
            disabled={isLoading || agentStatus === 'error'}
          />
          <SendButton
            onClick={() => handleSubmit()}
            disabled={!inputValue.trim() || isLoading || agentStatus === 'error'}
          >
            {isLoading ? (
              <Loader size={20} className="animate-spin" />
            ) : (
              <Send size={20} />
            )}
          </SendButton>
        </InputWrapper>
      </InputContainer>
    </ChatContainer>
  );
}

export default Chat;