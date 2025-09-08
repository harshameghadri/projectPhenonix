import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { User, Bot, ExternalLink, FileText, Github } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const MessageContainer = styled(motion.div)`
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: flex-start;
  ${props => props.isUser && `
    flex-direction: row-reverse;
  `}
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: white;
  
  ${props => props.isUser ? `
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  ` : `
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  `}
`;

const MessageBubble = styled.div`
  max-width: 80%;
  padding: 1.25rem 1.5rem;
  border-radius: 18px;
  position: relative;
  word-wrap: break-word;
  
  ${props => props.isUser ? `
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 4px;
  ` : props.isError ? `
    background: #fef2f2;
    color: #dc2626;
    border: 1px solid #fecaca;
    border-bottom-left-radius: 4px;
  ` : `
    background: white;
    color: #374151;
    box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
    border-bottom-left-radius: 4px;
  `}
`;

const MessageContent = styled.div`
  line-height: 1.6;
  
  h1, h2, h3, h4, h5, h6 {
    margin: 1rem 0 0.5rem 0;
    color: ${props => props.isUser ? 'inherit' : '#1f2937'};
  }
  
  p {
    margin: 0.75rem 0;
  }
  
  ul, ol {
    margin: 0.75rem 0;
    padding-left: 1.5rem;
  }
  
  li {
    margin: 0.25rem 0;
  }
  
  code {
    background: ${props => props.isUser ? 'rgba(255,255,255,0.2)' : '#f3f4f6'};
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: 'Fira Code', monospace;
    font-size: 0.9em;
  }
  
  blockquote {
    border-left: 4px solid ${props => props.isUser ? 'rgba(255,255,255,0.3)' : '#e5e7eb'};
    padding-left: 1rem;
    margin: 1rem 0;
    font-style: italic;
  }
`;

const SourcesContainer = styled.div`
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
`;

const SourcesHeader = styled.div`
  font-size: 0.85rem;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const SourcesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const SourceItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 0.85rem;
  color: #4b5563;
  border-left: 3px solid #667eea;
`;

const SourceIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
`;

const SourceText = styled.span`
  flex: 1;
  font-weight: 500;
`;

const Timestamp = styled.div`
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.5rem;
  text-align: ${props => props.isUser ? 'right' : 'left'};
`;

function MessageBubbleComponent({ message }) {
  const isUser = message.type === 'user';
  const isError = message.type === 'error';
  
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getSourceIcon = (source) => {
    const sourceLower = source.toLowerCase();
    
    if (sourceLower.includes('github')) {
      return <Github size={14} />;
    } else if (sourceLower.includes('.pdf')) {
      return <FileText size={14} />;
    } else if (sourceLower.includes('http')) {
      return <ExternalLink size={14} />;
    } else {
      return <FileText size={14} />;
    }
  };

  const customComponents = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      return !inline && match ? (
        <SyntaxHighlighter
          style={vscDarkPlus}
          language={match[1]}
          PreTag="div"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    }
  };

  return (
    <MessageContainer
      isUser={isUser}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Avatar isUser={isUser}>
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </Avatar>
      
      <div style={{ flex: 1, minWidth: 0 }}>
        <MessageBubble isUser={isUser} isError={isError}>
          <MessageContent isUser={isUser}>
            {isUser ? (
              <div>{message.content}</div>
            ) : (
              <ReactMarkdown components={customComponents}>
                {message.content}
              </ReactMarkdown>
            )}
          </MessageContent>
          
          {!isUser && message.sources && message.sources.length > 0 && (
            <SourcesContainer>
              <SourcesHeader>
                <FileText size={14} />
                Sources ({message.sources.length})
              </SourcesHeader>
              <SourcesList>
                {message.sources.map((source, index) => (
                  <SourceItem key={index}>
                    <SourceIcon>
                      {getSourceIcon(source.source)}
                    </SourceIcon>
                    <SourceText>{source.source}</SourceText>
                  </SourceItem>
                ))}
              </SourcesList>
            </SourcesContainer>
          )}
        </MessageBubble>
        
        <Timestamp isUser={isUser}>
          {formatTimestamp(message.timestamp)}
        </Timestamp>
      </div>
    </MessageContainer>
  );
}

export default MessageBubbleComponent;