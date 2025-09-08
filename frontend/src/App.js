import React from 'react';
import styled from 'styled-components';
import Chat from './components/Chat';
import Header from './components/Header';
import { motion } from 'framer-motion';

const AppContainer = styled.div`
  width: 100%;
  max-width: 1200px;
  height: 90vh;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

function App() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      <AppContainer>
        <Header />
        <Chat />
      </AppContainer>
    </motion.div>
  );
}

export default App;