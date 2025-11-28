#!/bin/bash

# RAG Platform Startup Script

echo "🚀 Starting RAG Platform..."
echo "=========================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check if required environment variables are set
if [ -z "$QWEN_API_KEY" ]; then
    echo "⚠️  Warning: QWEN_API_KEY environment variable not set."
    echo "   Please set it in your .env file or environment."
fi

if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  Warning: DATABASE_URL environment variable not set."
    echo "   Please set it in your .env file or environment."
fi

echo "📋 Available commands:"
echo "  1. Run CLI application: python main.py"
echo "  2. Run demo: python demo.py"
echo "  3. Run example usage: python example_usage.py"
echo "  4. Run complete pipeline demo: python complete_pipeline_demo.py"
echo "  5. Run tests: python -m pytest tests/"
echo "  6. Verify installation: python verify_installation.py"

echo ""
echo "💡 Quick start: Run 'python main.py' to start the CLI application"
echo ""
echo "✅ RAG Platform ready for use!"

# Keep the script running so users can see the output
read -p "Press Enter to exit..."