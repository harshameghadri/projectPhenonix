#!/bin/bash

# VitaeAgent Ollama Setup Script
# This script helps you quickly set up VitaeAgent with Ollama for local AI

set -e

echo "🤖 VitaeAgent Ollama Setup"
echo "=========================="
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed."
    echo "📦 Installing Ollama..."
    
    # Detect OS and install Ollama
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ollama
        else
            curl -fsSL https://ollama.com/install.sh | sh
        fi
    else
        # Linux
        curl -fsSL https://ollama.com/install.sh | sh
    fi
    
    echo "✅ Ollama installed successfully!"
else
    echo "✅ Ollama is already installed."
fi

echo ""

# Check if Ollama service is running
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "🔄 Starting Ollama service..."
    ollama serve &
    sleep 3
    
    # Wait for Ollama to be ready
    echo "⏳ Waiting for Ollama to be ready..."
    for i in {1..10}; do
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            break
        fi
        echo "   Waiting... ($i/10)"
        sleep 2
    done
    
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "✅ Ollama service is running!"
    else
        echo "❌ Failed to start Ollama service. Please run 'ollama serve' manually."
        exit 1
    fi
else
    echo "✅ Ollama service is already running."
fi

echo ""

# Check available models
echo "📋 Checking available models..."
MODELS=$(ollama list | grep -v "NAME" | wc -l)

if [ "$MODELS" -eq 0 ]; then
    echo "📥 No models found. Downloading recommended model..."
    echo "🔄 Downloading llama3.1:8b (this may take a few minutes)..."
    ollama pull llama3.1:8b
    echo "✅ Model downloaded successfully!"
else
    echo "✅ Found $MODELS existing model(s):"
    ollama list
fi

echo ""

# Setup environment file
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from template."
else
    echo "ℹ️  .env file already exists."
fi

# Update .env for Ollama usage
if grep -q "MODEL_PROVIDER=ollama" .env; then
    echo "✅ Environment already configured for Ollama."
else
    echo "🔧 Configuring .env for Ollama..."
    
    # Update or add MODEL_PROVIDER
    if grep -q "MODEL_PROVIDER=" .env; then
        sed -i.bak 's/MODEL_PROVIDER=.*/MODEL_PROVIDER=ollama/' .env
    else
        echo "MODEL_PROVIDER=ollama" >> .env
    fi
    
    # Update or add EMBEDDING_PROVIDER
    if grep -q "EMBEDDING_PROVIDER=" .env; then
        sed -i.bak 's/EMBEDDING_PROVIDER=.*/EMBEDDING_PROVIDER=local/' .env
    else
        echo "EMBEDDING_PROVIDER=local" >> .env
    fi
    
    echo "✅ Environment configured for local Ollama usage."
fi

echo ""

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Created Python virtual environment."
fi

source venv/bin/activate
pip install -r requirements.txt
echo "✅ Python dependencies installed."

cd ..

echo ""

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
echo "✅ Node.js dependencies installed."

cd ..

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Add your professional documents to the 'data/' folder:"
echo "   - PDF files (CV, portfolio, etc.)"
echo "   - Text/Markdown files"
echo "   - Update data/blog_urls.txt with your blog URLs"
echo ""
echo "2. Run data ingestion:"
echo "   cd backend && source venv/bin/activate && python scripts/ingest.py"
echo ""
echo "3. Start the application:"
echo "   docker-compose up --build"
echo "   OR manually:"
echo "   - Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "   - Frontend: cd frontend && npm start"
echo ""
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "📖 For detailed instructions, see:"
echo "   - README.md (general setup)"
echo "   - OLLAMA_SETUP.md (Ollama-specific guide)"
echo ""
echo "🚀 Your VitaeAgent is ready to go with local AI!"