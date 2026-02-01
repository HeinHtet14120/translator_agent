#!/bin/bash
# Quick Setup Script for AI Video Translator
# This script will help you get started quickly

set -e  # Exit on error

echo "================================================"
echo "  AI Video Translator - Quick Setup"
echo "================================================"
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $python_version"
echo ""

# Check pip
echo "2️⃣  Checking pip..."
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip not found. Please install pip."
    exit 1
fi
echo "✅ pip is available"
echo ""

# Install Python packages
echo "3️⃣  Installing Python packages..."
echo "   This may take a few minutes..."
pip3 install openai-whisper anthropic --quiet 2>/dev/null || pip install openai-whisper anthropic --quiet
echo "✅ Python packages installed"
echo ""

# Check FFmpeg
echo "4️⃣  Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg not found."
    echo ""
    echo "Please install FFmpeg:"
    echo "  • Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  • macOS: brew install ffmpeg"
    echo "  • Windows: Download from https://ffmpeg.org/"
    echo ""
    read -p "Have you installed FFmpeg? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please install FFmpeg and run this script again."
        exit 1
    fi
else
    echo "✅ FFmpeg is installed"
fi
echo ""

# API Key setup
echo "5️⃣  Setting up API Key (optional)..."
echo ""
echo "For best translation quality (especially Burmese/Thai),"
echo "you should get a Claude API key from:"
echo "https://console.anthropic.com/"
echo ""
read -p "Do you have an API key? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Enter your Anthropic API key: " api_key
    echo "export ANTHROPIC_API_KEY=\"$api_key\"" >> ~/.bashrc
    echo "export ANTHROPIC_API_KEY=\"$api_key\"" >> ~/.zshrc 2>/dev/null || true
    export ANTHROPIC_API_KEY="$api_key"
    echo "✅ API key saved"
else
    echo "⚠️  Skipping API key setup."
    echo "   You can still use local translation with --local flag"
    echo "   (Note: Lower quality for Burmese/Thai)"
fi
echo ""

# Test installation
echo "6️⃣  Testing installation..."
python3 video_translator.py --help &> /dev/null && echo "✅ video_translator.py is working" || echo "⚠️  video_translator.py test failed"
echo ""

# Create example config
echo "7️⃣  Creating config file..."
if [ ! -f config.yaml ]; then
    cp config_template.yaml config.yaml
    echo "✅ Created config.yaml (you can customize this)"
else
    echo "⚠️  config.yaml already exists (skipping)"
fi
echo ""

# Success message
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "You're ready to translate videos! Try:"
echo ""
echo "  # Translate a video to Burmese:"
echo "  python3 video_translator.py your_movie.mp4 --source en --targets my"
echo ""
echo "  # Translate to both Burmese and Thai:"
echo "  python3 video_translator.py your_movie.mp4 --source en --targets my th"
echo ""
echo "  # Process multiple videos:"
echo "  python3 batch_translator.py ./movies --source en --targets my th"
echo ""
echo "📚 For more help, see:"
echo "   • README.md - Complete guide"
echo "   • SETUP_GUIDE.md - Detailed setup instructions"
echo ""
echo "Happy translating! 🎬🌍"
echo ""
