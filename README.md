# VitaeAgent - The Living CV

An intelligent, conversational digital professional persona that answers questions about your career, experience, and skills using advanced RAG (Retrieval-Augmented Generation) technology.

## 🌟 Features

- **Intelligent Conversations**: Chat naturally about professional background, projects, and skills
- **Source Citations**: Every response is backed by verifiable sources from your documents
- **Multi-language Support**: Converse in multiple languages with automatic translation
- **Real-time Processing**: Instant responses with comprehensive context understanding
- **Modern UI**: Beautiful, responsive React interface with smooth animations
- **Document Processing**: Supports PDFs, text files, blog posts, and GitHub repositories

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI**: High-performance REST API with automatic documentation
- **LangChain**: Advanced RAG pipeline with document processing
- **ChromaDB**: Vector database for semantic search
- **OpenAI GPT-4**: Intelligent response generation
- **Google Translate**: Multi-language support

### Frontend (React)
- **React 18**: Modern component-based UI
- **Styled Components**: CSS-in-JS styling with animations
- **Framer Motion**: Smooth animations and transitions
- **Axios**: HTTP client for API communication
- **React Markdown**: Rich text rendering with syntax highlighting

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key
- Google Cloud credentials (optional, for translation)

### 1. Environment Setup

```bash
# Clone and enter the project
git clone <your-repo>
cd projectPheonix

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
```

### 2. Add Your Professional Data

Place your professional documents in the `data/` directory:

```
data/
├── cv.pdf                    # Your CV/resume
├── portfolio.pdf             # Project portfolio
├── certifications.pdf        # Professional certificates
├── skills_summary.md         # Skills overview
└── blog_urls.txt            # List of blog post URLs
```

### 3. Backend Setup

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Run data ingestion
python scripts/ingest.py

# Start the backend server
uvicorn app.main:app --reload
```

### 4. Frontend Setup

```bash
# Install Node.js dependencies
cd frontend
npm install

# Start the development server
npm start
```

### 5. Using Docker (Alternative)

```bash
# Start with Docker Compose
docker-compose up --build
```

## 📁 Project Structure

```
projectPheonix/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   └── agent.py          # RAG logic and agent persona
│   ├── scripts/
│   │   └── ingest.py         # Data ingestion pipeline
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API communication
│   │   └── App.js           # Main application
│   └── package.json         # Node.js dependencies
├── data/                    # Your professional documents
├── db/                      # Vector database (auto-created)
└── docker-compose.yml       # Container orchestration
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | ✅ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Cloud credentials file path | ❌ |
| `GITHUB_TOKEN` | GitHub personal access token | ❌ |
| `GITHUB_USERNAME` | Your GitHub username | ❌ |

### Data Sources

1. **Documents**: PDFs and text files in the `data/` directory
2. **Blog Posts**: URLs listed in `data/blog_urls.txt`
3. **GitHub**: Repositories from your GitHub profile (requires token)

## 🔍 Usage Examples

### Starting a Conversation

The VitaeAgent provides suggested questions to get started:

- "What is your professional background?"
- "Tell me about your most significant project."
- "What programming languages do you work with?"
- "Describe your leadership experience."

### Advanced Queries

- "What specific challenges did you face in your cloud migration project?"
- "How many years of Python experience do you have, and in what contexts?"
- "Show me examples of your technical writing and documentation skills."

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Adding New Features

1. **Backend**: Add new endpoints in `app/main.py`
2. **Frontend**: Create new components in `src/components/`
3. **Data Processing**: Extend `scripts/ingest.py` for new data sources

### API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🌐 Deployment

### Production Environment

1. Set environment variables for production
2. Build the frontend: `npm run build`
3. Configure a reverse proxy (nginx/Apache)
4. Use a production WSGI server (Gunicorn/Uvicorn)

### Cloud Deployment

The project is configured for easy deployment on:
- **Backend**: Heroku, Railway, Google Cloud Run
- **Frontend**: Vercel, Netlify
- **Full Stack**: AWS, GCP, Azure with Docker

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For questions or support:
1. Check the API documentation at `/docs`
2. Review the logs for error details
3. Open an issue on GitHub

---

**VitaeAgent** - Transforming static CVs into intelligent, interactive professional experiences. 🚀