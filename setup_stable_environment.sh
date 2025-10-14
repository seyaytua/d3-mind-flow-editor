#!/bin/bash
# D3-Mind-Flow-Editor Stable Environment Setup
# Uses Python 3.11 + PySide6 6.6.3

echo "🚀 Setting up D3-Mind-Flow-Editor with stable versions"
echo "======================================================"

# Check if pyenv is available
if command -v pyenv &> /dev/null; then
    echo "✅ pyenv found"
    
    # Install Python 3.11 if not available
    if ! pyenv versions | grep -q "3.11"; then
        echo "📦 Installing Python 3.11..."
        pyenv install 3.11.11
    fi
    
    # Set local Python version
    pyenv local 3.11.11
    echo "✅ Python 3.11 set for this project"
else
    echo "⚠️ pyenv not found. Using system Python..."
    echo "   Consider installing pyenv: brew install pyenv"
fi

# Create stable virtual environment
echo "📦 Creating stable virtual environment..."
python -m venv venv_stable
source venv_stable/bin/activate

echo "📦 Installing stable dependencies..."
pip install --upgrade pip
pip install -r requirements_stable.txt

echo "🌐 Installing Playwright browser..."
python -m playwright install chromium

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run the application:"
echo "  source venv_stable/bin/activate"
echo "  cd src"
echo "  python main.py"
echo ""
echo "Python version: $(python --version)"
echo "PySide6 version: $(pip show PySide6 | grep Version)"