import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      console.error(`Server Error ${status}:`, data);
      
      switch (status) {
        case 503:
          throw new Error('VitaeAgent is currently unavailable. Please try again later.');
        case 500:
          throw new Error('An internal server error occurred. Please try again.');
        case 400:
          throw new Error(data.error?.message || 'Invalid request.');
        default:
          throw new Error(`Server error: ${status}`);
      }
    } else if (error.request) {
      // Network error
      console.error('Network error:', error.request);
      throw new Error('Unable to connect to VitaeAgent. Please check your connection.');
    } else {
      // Other error
      console.error('Unexpected error:', error.message);
      throw new Error('An unexpected error occurred.');
    }
  }
);

export const vitaeApi = {
  // Send a chat message to the agent
  async sendMessage(query, language = 'en') {
    try {
      const response = await api.post('/chat', {
        query,
        language
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get suggested questions to start the conversation
  async getSuggestedQuestions() {
    try {
      const response = await api.get('/suggestions');
      return response.data.questions;
    } catch (error) {
      console.error('Failed to get suggestions:', error);
      // Return fallback suggestions if API fails
      return [
        "What is your professional background?",
        "Tell me about your most significant project.",
        "What programming languages do you work with?",
        "What are your key achievements?",
        "Describe your leadership experience."
      ];
    }
  },

  // Check the health of the agent
  async checkHealth() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get statistics about the knowledge base
  async getStats() {
    try {
      const response = await api.get('/stats');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get basic API information
  async getInfo() {
    try {
      const response = await api.get('/');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default api;