import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { MessageSquare } from 'lucide-react';

const Container = styled.div`
  margin-top: 1rem;
`;

const Header = styled.h3`
  font-size: 1rem;
  color: #4b5563;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
`;

const QuestionsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 0.75rem;
  max-width: 800px;
  margin: 0 auto;
`;

const QuestionButton = styled(motion.button)`
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
  line-height: 1.4;
  color: #374151;
  position: relative;
  overflow: hidden;
  
  &:hover:not(:disabled) {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.15);
    color: #667eea;
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.05), transparent);
    transition: left 0.5s ease;
  }
  
  &:hover::before {
    left: 100%;
  }
`;

const QuestionIcon = styled.div`
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  color: #9ca3af;
  transition: color 0.2s ease;
  
  ${QuestionButton}:hover & {
    color: #667eea;
  }
`;

function SuggestedQuestions({ questions, onQuestionClick, disabled }) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.4,
        ease: "easeOut"
      }
    }
  };

  if (!questions || questions.length === 0) {
    return null;
  }

  return (
    <Container>
      <Header>
        <MessageSquare size={16} />
        Suggested Questions
      </Header>
      
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <QuestionsGrid>
          {questions.map((question, index) => (
            <motion.div key={index} variants={itemVariants}>
              <QuestionButton
                onClick={() => onQuestionClick(question)}
                disabled={disabled}
                whileTap={{ scale: 0.98 }}
              >
                {question}
                <QuestionIcon>
                  <MessageSquare size={14} />
                </QuestionIcon>
              </QuestionButton>
            </motion.div>
          ))}
        </QuestionsGrid>
      </motion.div>
    </Container>
  );
}

export default SuggestedQuestions;