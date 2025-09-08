"""
VitaeAgent Core Intelligence Module
This module contains the RAG logic and agent persona that powers
the intelligent conversational interface with support for both 
Ollama (local) and OpenAI models.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.llms import OpenAI, Ollama
from langchain.chat_models import ChatOpenAI, ChatOllama
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.vectorstores import Chroma
from langchain.retrievers.multi_vector import MultiVectorRetriever
try:
    from google.cloud import translate_v2 as translate
except ImportError:
    translate = None

logger = logging.getLogger(__name__)


class ModelConfig:
    """Configuration class for managing different model providers."""
    
    @staticmethod
    def get_llm():
        """Get the configured language model based on environment variables."""
        provider = os.getenv("MODEL_PROVIDER", "ollama").lower()
        
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
            
            return ChatOpenAI(
                model_name="gpt-4",
                temperature=0.1,
                openai_api_key=api_key
            )
        
        elif provider == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            
            try:
                # Test Ollama connection
                import requests
                response = requests.get(f"{base_url}/api/tags", timeout=5)
                if response.status_code != 200:
                    raise ConnectionError("Cannot connect to Ollama server")
            except Exception as e:
                logger.error(f"Ollama connection failed: {e}")
                raise ConnectionError(f"Cannot connect to Ollama at {base_url}. Make sure Ollama is running.")
            
            return ChatOllama(
                model=model_name,
                base_url=base_url,
                temperature=0.1
            )
        
        else:
            raise ValueError(f"Unsupported model provider: {provider}")
    
    @staticmethod
    def get_embeddings():
        """Get the configured embedding model based on environment variables."""
        provider = os.getenv("EMBEDDING_PROVIDER", "local").lower()
        
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY is required when using OpenAI embeddings")
            
            return OpenAIEmbeddings(openai_api_key=api_key)
        
        elif provider == "local":
            model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            
            return HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")


class VitaeAgent:
    """
    The core VitaeAgent class that handles intelligent conversations
    about professional background using RAG (Retrieval-Augmented Generation).
    Supports both local (Ollama) and cloud (OpenAI) models.
    """
    
    def __init__(self):
        """Initialize the VitaeAgent with all necessary components."""
        self.db_path = Path("db")
        
        # Initialize embeddings based on configuration
        logger.info("Initializing embedding model...")
        try:
            self.embeddings = ModelConfig.get_embeddings()
            logger.info(f"Embedding provider: {os.getenv('EMBEDDING_PROVIDER', 'local')}")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
        
        # Initialize the language model based on configuration
        logger.info("Initializing language model...")
        try:
            self.llm = ModelConfig.get_llm()
            provider = os.getenv("MODEL_PROVIDER", "ollama")
            model = os.getenv("OLLAMA_MODEL", "llama3.1:8b") if provider == "ollama" else "gpt-4"
            logger.info(f"LLM provider: {provider}, model: {model}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
        
        # Initialize ChromaDB client and retriever
        self._init_retriever()
        
        # Initialize Google Translate client (optional)
        self.translator = None
        try:
            if translate and os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                self.translator = translate.Client()
                logger.info("Google Translate initialized")
            else:
                logger.info("Google Translate not configured (translation disabled)")
        except Exception as e:
            logger.warning(f"Google Translate not available: {e}")
        
        # Create the RAG chain
        self._create_rag_chain()

    def _init_retriever(self):
        """Initialize the ChromaDB retriever."""
        try:
            chroma_client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            collection = chroma_client.get_collection("vitae_knowledge")
            
            # Create Langchain Chroma wrapper
            self.vectorstore = Chroma(
                client=chroma_client,
                collection_name="vitae_knowledge",
                embedding_function=self.embeddings
            )
            
            # Create retriever with similarity search
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            logger.info("Successfully initialized retriever")
            
        except Exception as e:
            logger.error(f"Error initializing retriever: {e}")
            raise

    def _create_system_prompt(self) -> str:
        """Create the comprehensive system prompt that defines the agent's persona."""
        return """You are the VitaeAgent, a sophisticated digital professional persona that represents a specific individual's career, skills, and accomplishments. You are NOT a general assistant - you are the digital embodiment of this person's professional identity.

## Core Personality Traits:

**Meticulously Factual**: You never speculate or invent information. Your knowledge is strictly confined to the provided context documents. If information is not in your knowledge base, you clearly state that you don't have that information.

**Proactively Helpful**: You don't just answer questions - you engage meaningfully. If a query is vague, you ask clarifying questions to guide the conversation toward more insightful exchanges.

**Transparent & Trustworthy**: Every key claim you make must be backed by a citation in the format [Source: filename, Page X] or [Source: URL] or [Source: GitHub: repository-name]. This builds immediate trust with users.

**Professional & Engaging**: You communicate in a professional yet personable tone, as if you are the person yourself speaking about their career journey.

## Response Guidelines:

1. **Source Citations**: Always cite your sources for factual claims using the format [Source: document_name] or [Source: URL]. This is critical for building trust.

2. **Scope Boundaries**: Only discuss information from your knowledge base. For questions outside this scope, politely explain that you don't have that information and suggest focusing on areas where you can provide detailed insights.

3. **Proactive Engagement**: When appropriate, suggest related topics or ask clarifying questions to deepen the conversation. For example: "Would you like to know more about the specific technologies used in that project?"

4. **Professional Tone**: Speak as the professional would speak about themselves - confident but not boastful, detailed but not overwhelming.

## Example Response Patterns:

For specific achievements: "In the Project Phoenix initiative, I led a team of 5 developers to implement a cloud migration strategy that reduced infrastructure costs by 40% [Source: portfolio.pdf, Page 3]. The project involved extensive work with AWS services and DevOps practices."

For skill inquiries: "My experience with Python spans over 8 years, including work on machine learning projects, web development with Django and FastAPI, and automation scripts [Source: cv.pdf, Page 1]. Would you like me to elaborate on any specific Python applications?"

For unknown information: "I don't have specific information about that particular framework in my knowledge base. However, I can share details about my experience with related technologies like React and Vue.js [Source: github_projects]."

Remember: You are this person's professional advocate and representative. Your goal is to provide accurate, engaging, and helpful information that showcases their capabilities and experience while maintaining complete honesty about the bounds of your knowledge."""

    def _create_rag_chain(self):
        """Create the RAG chain using LangChain Expression Language (LCEL)."""
        
        # Create the prompt template
        system_prompt = SystemMessagePromptTemplate.from_template(self._create_system_prompt())
        
        human_prompt = HumanMessagePromptTemplate.from_template(
            """Based on the following context about this professional's background, please answer the user's question. Remember to cite your sources.

Context:
{context}

User Question: {question}

Please provide a comprehensive, well-cited response that stays within the bounds of the provided context."""
        )
        
        self.chat_prompt = ChatPromptTemplate.from_messages([
            system_prompt,
            human_prompt
        ])
        
        # Create the RAG chain
        def format_docs(docs):
            """Format documents for context."""
            formatted_docs = []
            for doc in docs:
                source_info = self._extract_source_info(doc.metadata)
                content = f"{doc.page_content}\n[Source: {source_info}]"
                formatted_docs.append(content)
            return "\n\n".join(formatted_docs)
        
        # Create the chain using LCEL
        self.rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.chat_prompt
            | self.llm
            | StrOutputParser()
        )
        
        logger.info("Successfully created RAG chain")

    def _extract_source_info(self, metadata: Dict[str, Any]) -> str:
        """Extract readable source information from document metadata."""
        source_type = metadata.get('source_type', 'unknown')
        
        if source_type == 'pdf':
            source = metadata.get('source', 'Unknown PDF')
            page = metadata.get('page', '')
            return f"{source}" + (f", Page {page + 1}" if page != '' else "")
        
        elif source_type == 'text':
            return metadata.get('source', 'Unknown Text File')
        
        elif source_type == 'blog':
            title = metadata.get('title', 'Blog Post')
            url = metadata.get('url', '')
            return f"{title} - {url}" if url else title
        
        elif source_type == 'github':
            repo_name = metadata.get('repo_name', 'Unknown Repository')
            return f"GitHub: {repo_name}"
        
        else:
            return metadata.get('source', 'Unknown Source')

    def translate_text(self, text: str, target_language: str) -> str:
        """Translate text to the target language using Google Translate."""
        if not self.translator or target_language.lower() in ['en', 'english']:
            return text
        
        try:
            # Detect source language
            detection = self.translator.detect(text)
            source_lang = detection['language']
            
            # Skip translation if already in target language
            if source_lang == target_language:
                return text
            
            # Translate
            result = self.translator.translate(
                text, 
                target_language=target_language,
                source_language=source_lang
            )
            
            return result['translatedText']
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

    def chat(self, query: str, language: str = "en") -> Dict[str, Any]:
        """
        Main chat interface for the VitaeAgent.
        
        Args:
            query: The user's question
            language: Target language for the response
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            # Translate query to English if needed
            english_query = query
            if language.lower() not in ['en', 'english'] and self.translator:
                english_query = self.translate_text(query, 'en')
            
            # Get response from RAG chain
            response = self.rag_chain.invoke(english_query)
            
            # Translate response back to target language if needed
            final_response = response
            if language.lower() not in ['en', 'english'] and self.translator:
                final_response = self.translate_text(response, language)
            
            # Retrieve source documents for additional context
            source_docs = self.retriever.get_relevant_documents(english_query)
            sources = []
            for doc in source_docs:
                source_info = self._extract_source_info(doc.metadata)
                sources.append({
                    "source": source_info,
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                })
            
            return {
                "response": final_response,
                "sources": sources,
                "original_query": query,
                "processed_query": english_query,
                "language": language,
                "source_count": len(sources)
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                "response": "I apologize, but I encountered an error while processing your question. Please try again or rephrase your question.",
                "sources": [],
                "original_query": query,
                "processed_query": query,
                "language": language,
                "error": str(e)
            }

    def get_suggested_questions(self) -> List[str]:
        """Get a list of suggested questions to help users get started."""
        return [
            "What is your professional background?",
            "Tell me about your most significant project.",
            "What programming languages and technologies do you work with?",
            "What are your key achievements in your career?",
            "Describe your leadership experience.",
            "What industries have you worked in?",
            "Tell me about your education and certifications.",
            "What type of challenges do you excel at solving?",
            "Show me examples of your technical work.",
            "What makes you unique as a professional?"
        ]

    def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the agent's components."""
        status = {
            "retriever_ready": False,
            "llm_ready": False,
            "database_count": 0,
            "translator_available": self.translator is not None,
            "model_provider": os.getenv("MODEL_PROVIDER", "ollama"),
            "embedding_provider": os.getenv("EMBEDDING_PROVIDER", "local")
        }
        
        try:
            # Test retriever
            test_results = self.retriever.get_relevant_documents("test")
            status["retriever_ready"] = True
            status["database_count"] = len(test_results)
            
            # Test LLM with a simple query
            test_response = self.llm.predict("Hello")
            status["llm_ready"] = len(test_response) > 0
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            status["error"] = str(e)
        
        return status

    @staticmethod
    def check_ollama_models():
        """Check available Ollama models."""
        try:
            import requests
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            else:
                return []
        except Exception:
            return []


# Global agent instance
_agent_instance = None

def get_agent() -> VitaeAgent:
    """Get or create the global VitaeAgent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = VitaeAgent()
    return _agent_instance