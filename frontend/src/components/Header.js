import React from 'react';
import styled from 'styled-components';
import { Bot, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

const HeaderContainer = styled.header`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
  position: relative;
  overflow: hidden;
`;

const HeaderContent = styled.div`
  position: relative;
  z-index: 2;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  opacity: 0.9;
  font-weight: 300;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
`;

const IconWrapper = styled.div`
  position: relative;
`;

const SparkleIcon = styled(Sparkles)`
  position: absolute;
  top: -10px;
  right: -10px;
  width: 20px;
  height: 20px;
  opacity: 0.7;
  animation: sparkle 2s ease-in-out infinite;
  
  @keyframes sparkle {
    0%, 100% { transform: scale(1) rotate(0deg); opacity: 0.7; }
    50% { transform: scale(1.2) rotate(180deg); opacity: 1; }
  }
`;

const BackgroundPattern = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0.1;
  background-image: radial-gradient(circle at 20% 50%, white 1px, transparent 1px),
                    radial-gradient(circle at 70% 20%, white 1px, transparent 1px),
                    radial-gradient(circle at 90% 80%, white 1px, transparent 1px);
  background-size: 100px 100px, 150px 150px, 120px 120px;
  animation: float 20s ease-in-out infinite;
  
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }
`;

function Header() {
  return (
    <HeaderContainer>
      <BackgroundPattern />
      <HeaderContent>
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <Title>
            <IconWrapper>
              <Bot size={40} />
              <SparkleIcon />
            </IconWrapper>
            VitaeAgent
          </Title>
          <Subtitle>
            Your intelligent digital professional persona. Ask me anything about my background, experience, and skills.
          </Subtitle>
        </motion.div>
      </HeaderContent>
    </HeaderContainer>
  );
}

export default Header;