# VitaeAgent with Ollama - Local AI Setup Guide

This guide will help you set up VitaeAgent using Ollama for completely local, opensource AI models without any API costs or limits.

## 🚀 Quick Start with Ollama

### 1. Install and Setup Ollama

**macOS:**
```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Or using Homebrew
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from [ollama.com](https://ollama.com/download) and run the installer.

### 2. Start Ollama Service

```bash
# Start Ollama (runs on http://localhost:11434 by default)
ollama serve
```

### 3. Download Recommended Models

**For testing/development (faster, lower resource usage):**
```bash
# Download Llama 3.1 8B (recommended for testing)
ollama pull llama3.1:8b

# Alternative: Mistral 7B (also good for testing)
ollama pull mistral:7b
```

**For production (better quality, higher resource usage):**
```bash
# Download Llama 3.1 70B (best quality, requires more RAM/VRAM)
ollama pull llama3.1:70b

# Alternative: CodeLlama for technical conversations
ollama pull codellama:13b
```

### 4. Verify Installation

```bash
# Check available models
ollama list

# Test a model
ollama run llama3.1:8b "Hello, how are you?"
```

## ⚙️ VitaeAgent Configuration

### 1. Environment Setup

Create your `.env` file:
```bash
cp .env.example .env
```

Edit `.env` for Ollama usage:
```env
# Model Configuration - Use Ollama for local AI
MODEL_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Use local embeddings (no API key needed)
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2

# Optional: GitHub integration
GITHUB_USERNAME=your_username
GITHUB_TOKEN=your_token

# Optional: Translation (can be skipped)
# GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

The HuggingFace embeddings model will be downloaded automatically on first run.

### 3. Prepare Your Data

Add your professional documents to the `data/` folder:
```bash
# Example data structure
data/
├── cv.pdf
├── portfolio.pdf
├── projects.md
└── blog_urls.txt
```

### 4. Run Data Ingestion

```bash
cd backend
python scripts/ingest.py
```

This will:
- Process all your documents
- Download the local embedding model (first time only)
- Create a vector database in the `db/` folder

### 5. Start the Application

**Option 1: Docker (Recommended)**
```bash
# Make sure Ollama is running first!
ollama serve

# In another terminal, start the application
docker-compose up --build
```

**Option 2: Manual Start**
```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm install
npm start
```

## 🎯 Recommended Model Configurations

### Development/Testing
- **Model**: `llama3.1:8b` or `mistral:7b`
- **RAM**: 8GB+ recommended
- **Speed**: Fast responses
- **Quality**: Good for testing

### Production
- **Model**: `llama3.1:70b` or `codellama:13b`
- **RAM**: 64GB+ recommended for 70B models
- **Speed**: Slower but higher quality
- **Quality**: Excellent for professional use

### Resource-Constrained Setup
- **Model**: `llama3.1:8b` with quantization
- **RAM**: 4GB minimum
- **Speed**: Good
- **Quality**: Acceptable for basic use

## 🔧 Advanced Configuration

### Custom Ollama Settings

Create a custom Ollama configuration:
```bash
# Set custom Ollama port
export OLLAMA_HOST=0.0.0.0:11435

# Set custom models directory
export OLLAMA_MODELS="/custom/path/to/models"

# Start with custom settings
ollama serve
```

Update your `.env`:
```env
OLLAMA_BASE_URL=http://localhost:11435
```

### Model Performance Tuning

Adjust model parameters for your use case:
```env
# In your .env file, you can specify model parameters
OLLAMA_MODEL=llama3.1:8b
# Models will use default parameters, but you can create custom Modelfiles
```

Create a custom Modelfile for fine-tuning:
```bash
# Create a Modelfile
cat > Modelfile << EOF
FROM llama3.1:8b

# Set custom parameters for professional conversations
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096

# Custom system prompt for professional persona
SYSTEM You are a professional digital assistant representing someone's career and expertise. Always be factual and cite sources.
EOF

# Create custom model
ollama create vitae-agent -f Modelfile

# Use in your .env
# OLLAMA_MODEL=vitae-agent
```

### GPU Acceleration

If you have a compatible GPU:

**NVIDIA GPU:**
```bash
# Ensure CUDA drivers are installed
# Ollama will automatically use GPU if available

# Check GPU usage
nvidia-smi
```

**Apple Silicon (M1/M2/M3):**
```bash
# Ollama automatically uses Metal acceleration
# No additional setup required
```

## 🚨 Troubleshooting

### Common Issues

**1. "Cannot connect to Ollama server"**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

**2. "Model not found"**
```bash
# List available models
ollama list

# Pull the model you need
ollama pull llama3.1:8b
```

**3. "Out of memory"**
```bash
# Try a smaller model
ollama pull llama3.1:8b  # instead of 70b

# Or use quantized versions
ollama pull llama3.1:8b-q4_0
```

**4. Slow responses**
```bash
# Check system resources
top
htop

# Consider switching to a smaller model
# Or adding more RAM/better GPU
```

### Performance Optimization

**1. Memory Management:**
```bash
# Limit concurrent model loading
export OLLAMA_NUM_PARALLEL=1

# Set memory limits
export OLLAMA_MAX_LOADED_MODELS=1
```

**2. Response Speed:**
```bash
# Use smaller context window for faster responses
# Edit your model's num_ctx parameter
ollama show llama3.1:8b --modelfile
```

### Monitoring

**Check Ollama logs:**
```bash
# View Ollama service logs
ollama logs

# Or check system logs
tail -f /var/log/ollama.log
```

**Monitor resource usage:**
```bash
# CPU and memory
htop

# GPU usage (if applicable)
nvidia-smi -l 1
```

## 📊 Model Comparison

| Model | Size | RAM Required | Speed | Quality | Use Case |
|-------|------|-------------|-------|---------|----------|
| `llama3.1:8b` | ~4.7GB | 8GB | Fast | Good | Development/Testing |
| `mistral:7b` | ~4.1GB | 8GB | Fast | Good | Alternative to Llama |
| `codellama:7b` | ~3.8GB | 8GB | Fast | Technical | Code-focused conversations |
| `llama3.1:70b` | ~40GB | 64GB | Slow | Excellent | Production |
| `codellama:13b` | ~7.3GB | 16GB | Medium | Very Good | Technical production |

## 🔐 Privacy Benefits

Using Ollama provides complete privacy:
- ✅ No data sent to external APIs
- ✅ All processing happens locally
- ✅ No API costs or rate limits
- ✅ Complete control over your data
- ✅ Works offline after initial setup

## 🆘 Getting Help

**Ollama Issues:**
- GitHub: [ollama/ollama](https://github.com/ollama/ollama)
- Discord: [Ollama Community](https://discord.gg/ollama)

**VitaeAgent Issues:**
- Check the main README.md
- Review application logs
- Test with a smaller model first

---

**Ready to go completely local with your VitaeAgent!** 🤖