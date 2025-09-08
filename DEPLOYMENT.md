# VitaeAgent Deployment Guide

## Quick Deployment Options

### Option 1: Railway (Recommended - Easiest)

1. **Sign up**: Go to [railway.app](https://railway.app) and sign up with GitHub
2. **Deploy**: Click "Deploy from GitHub repo" and select `harshameghadri/projectPhenonix`
3. **Configure**: Railway will auto-detect and deploy both services
4. **Environment**: Set these environment variables in Railway dashboard:
   ```
   MODEL_PROVIDER=openai
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   EMBEDDING_PROVIDER=openai
   CHROMA_DB_PATH=./db
   BACKEND_HOST=0.0.0.0
   BACKEND_PORT=8000
   ALLOWED_ORIGINS=https://your-frontend-url.railway.app
   ```

### Option 2: Vercel (Frontend) + Render (Backend)

#### Frontend (Vercel):
1. Go to [vercel.com](https://vercel.com) and connect your GitHub
2. Import `harshameghadri/projectPhenonix`
3. Set build settings:
   - Build Command: `cd frontend && npm run build`
   - Output Directory: `frontend/build`
4. Set environment variables:
   ```
   REACT_APP_BACKEND_URL=https://your-backend-url.onrender.com
   ```

#### Backend (Render):
1. Go to [render.com](https://render.com) and connect GitHub
2. Create new Web Service from `harshameghadri/projectPhenonix`
3. Set build settings:
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set environment variables (see below)

### Option 3: DigitalOcean App Platform

1. Go to [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. Create app from GitHub repo `harshameghadri/projectPhenonix`
3. Configure two components:
   - **Backend**: Python app, auto-detected
   - **Frontend**: Static site, build: `cd frontend && npm run build`, output: `frontend/build`

## Environment Variables for Production

```bash
# Model Configuration (Use OpenAI for production)
MODEL_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Embedding Configuration  
EMBEDDING_PROVIDER=openai

# Database
CHROMA_DB_PATH=./db

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# CORS (update with your frontend URL)
ALLOWED_ORIGINS=https://your-frontend-url.vercel.app,http://localhost:3000
```

## Important Notes

⚠️ **For Production**: Use OpenAI instead of Ollama for easier deployment
⚠️ **API Keys**: Never commit API keys to GitHub - set them as environment variables
⚠️ **CORS**: Update `ALLOWED_ORIGINS` with your actual frontend URL

## Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend  
cd frontend
npm install
npm start
```

## Custom Domain

After deploying, you can add a custom domain in your hosting provider's dashboard:
- Railway: Settings → Domains
- Vercel: Settings → Domains  
- Render: Settings → Custom Domains