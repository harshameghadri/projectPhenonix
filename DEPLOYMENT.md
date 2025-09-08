# VitaeAgent Deployment Guide

This guide provides step-by-step instructions for deploying VitaeAgent in various environments.

## 🚀 Quick Deployment Checklist

### Prerequisites
- [ ] OpenAI API key obtained
- [ ] Professional documents prepared
- [ ] Environment variables configured
- [ ] Dependencies installed

### Deployment Steps
- [ ] Data ingestion completed
- [ ] Backend health check passes
- [ ] Frontend builds successfully
- [ ] End-to-end testing completed

## 🐳 Local Development with Docker

### 1. Environment Setup
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your credentials
OPENAI_API_KEY=your_openai_key_here
GITHUB_USERNAME=your_github_username
GITHUB_TOKEN=your_github_token
```

### 2. Prepare Your Data
```bash
# Add your professional documents to data/
cp ~/Documents/cv.pdf data/
cp ~/Documents/portfolio.pdf data/

# Add blog URLs
echo "https://yourblog.com/post1" >> data/blog_urls.txt
```

### 3. Build and Run
```bash
# Build and start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🔧 Manual Development Setup

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run data ingestion
python scripts/ingest.py

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## ☁️ Cloud Deployment

### Option 1: Heroku (Backend + Frontend)

#### Backend Deployment
```bash
# Create Heroku app
heroku create vitae-agent-backend

# Set environment variables
heroku config:set OPENAI_API_KEY=your_key_here
heroku config:set GITHUB_USERNAME=your_username

# Create Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port $PORT" > backend/Procfile

# Deploy
git subtree push --prefix=backend heroku main
```

#### Frontend Deployment (Netlify/Vercel)
```bash
# Build the frontend
cd frontend
npm run build

# Deploy to Netlify
npm install -g netlify-cli
netlify deploy --prod --dir=build

# Set environment variables in Netlify dashboard
REACT_APP_BACKEND_URL=https://your-heroku-app.herokuapp.com
```

### Option 2: Google Cloud Platform

#### Backend on Cloud Run
```bash
# Build Docker image
cd backend
docker build -t gcr.io/PROJECT_ID/vitae-agent-backend .

# Push to Container Registry
docker push gcr.io/PROJECT_ID/vitae-agent-backend

# Deploy to Cloud Run
gcloud run deploy vitae-agent-backend \
  --image gcr.io/PROJECT_ID/vitae-agent-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your_key
```

#### Frontend on Firebase Hosting
```bash
cd frontend

# Build the app
npm run build

# Install Firebase CLI
npm install -g firebase-tools

# Initialize Firebase
firebase init hosting

# Deploy
firebase deploy
```

### Option 3: AWS Deployment

#### Backend on AWS Lambda (Serverless)
```bash
# Install Serverless Framework
npm install -g serverless

# Create serverless.yml in backend/
service: vitae-agent-backend
provider:
  name: aws
  runtime: python3.11
  environment:
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}

functions:
  api:
    handler: app.main.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true

# Deploy
cd backend
serverless deploy
```

#### Frontend on S3 + CloudFront
```bash
cd frontend

# Build the app
npm run build

# Upload to S3 bucket
aws s3 sync build/ s3://your-bucket-name --delete

# Configure CloudFront distribution
# Set origin to S3 bucket
# Enable compression
# Set default root object to index.html
```

## 🔍 Production Configuration

### Environment Variables
```bash
# Production .env
OPENAI_API_KEY=your_production_openai_key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_username

# Database settings
CHROMA_DB_PATH=/app/db

# CORS settings
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Server settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### Performance Optimization

#### Backend Optimizations
```python
# In app/main.py, add caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
```

#### Frontend Optimizations
```bash
# Enable production build optimizations
cd frontend

# Build with optimizations
npm run build

# Analyze bundle size
npm install -g webpack-bundle-analyzer
npx webpack-bundle-analyzer build/static/js/*.js
```

## 🔐 Security Configuration

### Backend Security
```python
# Add to app/main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

### Environment Security
```bash
# Use secret management service
# AWS Secrets Manager, Google Secret Manager, etc.

# Never commit .env files
echo ".env*" >> .gitignore

# Use environment-specific configurations
# .env.production, .env.staging, .env.development
```

## 📊 Monitoring and Logging

### Application Monitoring
```bash
# Add monitoring endpoints
# Health checks: /health
# Metrics: /metrics
# Status: /status

# Set up logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Error Tracking
```bash
# Integration with Sentry (optional)
pip install sentry-sdk

# Add to app/main.py
import sentry_sdk
sentry_sdk.init(dsn="YOUR_SENTRY_DSN")
```

## 🚨 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep -E "(fastapi|langchain|chromadb)"

# Check environment variables
echo $OPENAI_API_KEY

# Check logs
tail -f logs/app.log
```

#### Frontend Build Fails
```bash
# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+

# Build with verbose output
npm run build -- --verbose
```

#### Database Issues
```bash
# Check database directory
ls -la db/

# Reset database
rm -rf db/
python scripts/ingest.py

# Check ChromaDB connection
python -c "import chromadb; print('ChromaDB OK')"
```

### Performance Issues

#### Slow Response Times
1. Check embedding model performance
2. Optimize chunk sizes in ingestion
3. Add caching layer (Redis)
4. Use faster embedding models

#### Memory Issues
1. Reduce batch sizes in ingestion
2. Implement pagination for large datasets
3. Use streaming for large responses
4. Monitor memory usage

## 🔄 Maintenance

### Regular Updates
```bash
# Update dependencies
pip list --outdated
pip install --upgrade package_name

npm outdated
npm update
```

### Data Refresh
```bash
# Re-run ingestion after adding new documents
python scripts/ingest.py

# Backup existing database
cp -r db/ db_backup_$(date +%Y%m%d)/
```

### Monitoring Checklist
- [ ] API response times
- [ ] Error rates
- [ ] Database size growth
- [ ] Memory usage
- [ ] API key usage/costs

## 📞 Support

If you encounter issues:
1. Check the logs first
2. Review this deployment guide
3. Check the main README.md
4. Open an issue on GitHub

---

Happy deploying! 🚀