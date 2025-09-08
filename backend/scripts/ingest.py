#!/usr/bin/env python3
"""
VitaeAgent Data Ingestion Script
This script serves as the agent's librarian, reading professional documents
and building a persistent vector database for intelligent retrieval.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import requests
import time

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataIngestionEngine:
    """
    The core ingestion engine that processes various data sources and builds
    the agent's knowledge base.
    """
    
    def __init__(self):
        self.data_dir = Path("data")
        self.db_dir = Path("db")
        self.db_dir.mkdir(exist_ok=True)
        
        # Initialize embeddings based on configuration
        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "local").lower()
        
        if embedding_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY is required when using OpenAI embeddings")
            self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            logger.info("Using OpenAI embeddings")
        else:
            # Default to local HuggingFace embeddings
            model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info(f"Using local embeddings: {model_name}")
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.db_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection_name = "vitae_knowledge"
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
        except:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection: {self.collection_name}")

    def load_pdf_documents(self) -> List[Document]:
        """Load and process PDF documents from the data directory."""
        documents = []
        pdf_files = list(self.data_dir.glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            try:
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()
                
                # Add source metadata
                for doc in docs:
                    doc.metadata.update({
                        "source": str(pdf_file.name),
                        "source_type": "pdf",
                        "file_path": str(pdf_file)
                    })
                
                documents.extend(docs)
                logger.info(f"Loaded {len(docs)} pages from {pdf_file.name}")
                
            except Exception as e:
                logger.error(f"Error loading PDF {pdf_file}: {str(e)}")
        
        return documents

    def load_text_documents(self) -> List[Document]:
        """Load and process text documents from the data directory."""
        documents = []
        text_files = list(self.data_dir.glob("*.txt")) + list(self.data_dir.glob("*.md"))
        
        logger.info(f"Found {len(text_files)} text files to process")
        
        for text_file in text_files:
            try:
                loader = TextLoader(str(text_file), encoding='utf-8')
                docs = loader.load()
                
                # Add source metadata
                for doc in docs:
                    doc.metadata.update({
                        "source": str(text_file.name),
                        "source_type": "text",
                        "file_path": str(text_file)
                    })
                
                documents.extend(docs)
                logger.info(f"Loaded {text_file.name}")
                
            except Exception as e:
                logger.error(f"Error loading text file {text_file}: {str(e)}")
        
        return documents

    def scrape_blog_urls(self, urls: List[str]) -> List[Document]:
        """Scrape content from a list of blog URLs."""
        documents = []
        
        logger.info(f"Scraping {len(urls)} blog URLs")
        
        for url in urls:
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to extract the main content
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "header", "footer"]):
                    script.decompose()
                
                # Try common content selectors
                content = None
                selectors = [
                    'article', '.post-content', '.entry-content', 
                    '.content', 'main', '.post-body'
                ]
                
                for selector in selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        content = content_elem.get_text(strip=True)
                        break
                
                if not content:
                    # Fallback to body content
                    content = soup.get_text(strip=True)
                
                if content:
                    # Get title
                    title_elem = soup.find('title')
                    title = title_elem.get_text(strip=True) if title_elem else url
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": url,
                            "source_type": "blog",
                            "title": title,
                            "url": url
                        }
                    )
                    documents.append(doc)
                    logger.info(f"Scraped blog: {title}")
                
                # Be respectful with requests
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping URL {url}: {str(e)}")
        
        return documents

    def fetch_github_repositories(self, username: str) -> List[Document]:
        """Fetch repository information from GitHub."""
        documents = []
        
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            logger.warning("No GitHub token provided, skipping repository fetch")
            return documents
        
        try:
            headers = {"Authorization": f"token {github_token}"}
            
            # Fetch user repositories
            repos_url = f"https://api.github.com/users/{username}/repos"
            response = requests.get(repos_url, headers=headers)
            response.raise_for_status()
            
            repositories = response.json()
            logger.info(f"Found {len(repositories)} repositories for {username}")
            
            for repo in repositories:
                try:
                    # Get repository details
                    repo_name = repo['name']
                    repo_url = repo['html_url']
                    description = repo.get('description', '')
                    language = repo.get('language', '')
                    topics = repo.get('topics', [])
                    
                    # Fetch README if available
                    readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
                    readme_response = requests.get(readme_url, headers=headers)
                    
                    readme_content = ""
                    if readme_response.status_code == 200:
                        readme_data = readme_response.json()
                        # Decode base64 content
                        import base64
                        readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
                    
                    # Create document content
                    content_parts = [
                        f"Repository: {repo_name}",
                        f"URL: {repo_url}",
                        f"Description: {description}",
                        f"Primary Language: {language}",
                        f"Topics: {', '.join(topics)}",
                        f"Stars: {repo['stargazers_count']}",
                        f"Forks: {repo['forks_count']}",
                    ]
                    
                    if readme_content:
                        content_parts.append(f"README:\n{readme_content}")
                    
                    doc = Document(
                        page_content="\n\n".join(content_parts),
                        metadata={
                            "source": f"GitHub: {repo_name}",
                            "source_type": "github",
                            "repo_name": repo_name,
                            "repo_url": repo_url,
                            "language": language,
                            "topics": topics
                        }
                    )
                    documents.append(doc)
                    
                    # Rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error processing repository {repo.get('name', 'unknown')}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error fetching GitHub repositories: {str(e)}")
        
        return documents

    def process_and_store_documents(self, documents: List[Document]):
        """Process documents into chunks and store in vector database."""
        if not documents:
            logger.warning("No documents to process")
            return
        
        logger.info(f"Processing {len(documents)} documents")
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from documents")
        
        # Prepare data for ChromaDB
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        # Generate embeddings and store in batches
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            try:
                # Generate embeddings
                embeddings = self.embeddings.embed_documents(batch_texts)
                
                # Store in ChromaDB
                self.collection.add(
                    documents=batch_texts,
                    metadatas=batch_metadatas,
                    ids=batch_ids,
                    embeddings=embeddings
                )
                
                logger.info(f"Stored batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
                
            except Exception as e:
                logger.error(f"Error storing batch {i//batch_size + 1}: {str(e)}")

    def run_ingestion(self):
        """Main ingestion pipeline."""
        logger.info("Starting VitaeAgent data ingestion...")
        
        all_documents = []
        
        # Load documents from files
        all_documents.extend(self.load_pdf_documents())
        all_documents.extend(self.load_text_documents())
        
        # Load from external sources
        blog_urls_file = self.data_dir / "blog_urls.txt"
        if blog_urls_file.exists():
            with open(blog_urls_file, 'r') as f:
                blog_urls = [line.strip() for line in f if line.strip()]
            all_documents.extend(self.scrape_blog_urls(blog_urls))
        
        # Fetch GitHub repositories
        github_username = os.getenv("GITHUB_USERNAME")
        if github_username:
            all_documents.extend(self.fetch_github_repositories(github_username))
        
        # Process and store all documents
        self.process_and_store_documents(all_documents)
        
        # Print summary
        collection_count = self.collection.count()
        logger.info(f"Ingestion complete! Total chunks in database: {collection_count}")


def main():
    """Main entry point for the ingestion script."""
    try:
        engine = DataIngestionEngine()
        engine.run_ingestion()
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()