#!/bin/bash
# Integration test runner script
# This script sets up the environment and runs CLI integration tests

set -e  # Exit on error

echo "🔧 Setting up test environment..."

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Check for virtual environment or uv
if command -v uv &> /dev/null; then
    echo "✓ Using uv for dependency management"
    echo "📦 Installing dependencies..."
    uv sync --extra dev
    PYTHON_CMD="uv run python"
    PYTEST_CMD="uv run pytest"
elif [ -d "venv" ] || [ -n "$VIRTUAL_ENV" ]; then
    echo "✓ Using existing Python virtual environment"
    PYTHON_CMD="python"
    PYTEST_CMD="pytest"
else
    echo "⚠️  No virtual environment detected"
    echo "   Attempting to use system Python..."
    PYTHON_CMD="python3"
    PYTEST_CMD="python3 -m pytest"

    # Try to install required packages
    echo "📦 Installing required packages..."
    pip3 install --user pytest pytest-asyncio || {
        echo "❌ Failed to install pytest. Please set up a virtual environment."
        exit 1
    }
fi

# Check for Memgraph
echo ""
echo "🔍 Checking Memgraph availability..."
if command -v docker &> /dev/null; then
    if docker ps | grep -q memgraph; then
        echo "✓ Memgraph container is running"
    else
        echo "⚠️  Memgraph container not found. Starting..."
        docker run -d -p 7687:7687 -p 7444:7444 --name memgraph-test memgraph/memgraph-platform || {
            echo "ℹ️  Could not start Memgraph (may already exist or Docker not available)"
        }
    fi
else
    echo "⚠️  Docker not found. Integration tests requiring Memgraph will be skipped."
fi

# Check for .env file
echo ""
echo "🔍 Checking configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Some tests may be skipped."
    echo "   Copy .env.example to .env and add your QWEN_API_KEY"
else
    if grep -q "QWEN_API_KEY=sk-" .env; then
        echo "✓ QWEN_API_KEY configured"
    else
        echo "⚠️  QWEN_API_KEY not set. API-dependent tests will be skipped."
    fi
fi

# Run tests
echo ""
echo "🧪 Running CLI integration tests..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Run basic tests (no dependencies required)
echo ""
echo "📝 Running basic CLI tests..."
$PYTEST_CMD tests/integration/test_cli_basic.py -v --tb=short -x

# Run full integration tests if environment is ready
if [ -f ".env" ] && grep -q "QWEN_API_KEY=sk-" .env; then
    echo ""
    echo "📝 Running full integration tests..."
    $PYTEST_CMD tests/integration/test_cli_integration.py -v --tb=short -k "not test_full_pipeline"
else
    echo ""
    echo "⏭️  Skipping full integration tests (QWEN_API_KEY not configured)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Test run complete!"
