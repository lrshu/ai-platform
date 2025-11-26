# Quick Start Guide: Employee Onboarding System

## Prerequisites

- Python 3.12+
- uv package manager
- Access to Qwen3-Max and Qwen3-VL-Max models via DashScope
- Access to MCP server for account provisioning

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd employee-onboarding-system
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Set up environment variables:
   Create a `.env` file in the project root:
   ```env
   # QWen Configuration
   QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
   QWEN_API_KEY="your-api-key-here"
   MCP_SERVER="http://127.0.0.1:9012/mcp"

   # Langsmith
   LANGSMITH_API_KEY="your-langsmith-api-key"
   LANGSMITH_PROJECT="employee-onboarding"

   # Database
   DATABASE_URL="sqlite:///./onboarding.db"
   ```

## Running the System

### Start the Chat Interface

To start the interactive onboarding agent:

```bash
python main.py chat
```

This will launch the LangGraph agent system and start an interactive chat session.

### API Server

To start the REST API server:

```bash
python main.py serve
```

The API will be available at `http://localhost:8000`.

## Basic Usage Flow

1. **Start Session**: Begin a new onboarding session
2. **Upload ID**: Provide a clear photo of your government-issued ID
3. **Verify Identity**: Wait for automatic verification of your ID
4. **Provide Information**: Enter your educational background and selected position
5. **Review Responsibilities**: Read about your position's responsibilities
6. **Get Accounts**: Receive your provisioned accounts (email, git, etc.)
7. **Complete Onboarding**: Finish the digital onboarding process
8. **Next Steps**: Follow up with physical onboarding tasks

## Development

### Running Tests

Run all tests:
```bash
pytest
```

Run unit tests only:
```bash
pytest tests/unit
```

Run integration tests:
```bash
pytest tests/integration
```

Run end-to-end tests:
```bash
pytest tests/e2e
```

### Code Structure

- `src/agents/` - Multi-agent implementations
- `src/models/` - Data models
- `src/services/` - Business logic services
- `src/utils/` - Utility functions
- `tests/` - Test suite
- `contracts/` - API contracts

## Configuration

The system can be configured through environment variables:

- `QWEN_API_KEY` - API key for Qwen models
- `MCP_SERVER` - URL for MCP tool server
- `DATABASE_URL` - Database connection string
- `LANGSMITH_API_KEY` - API key for LangSmith tracing

## Troubleshooting

### Common Issues

1. **ID Verification Fails**: Ensure the ID photo is clear, well-lit, and fully visible
2. **Account Provisioning Errors**: Check MCP server connectivity and permissions
3. **Slow Responses**: Verify internet connectivity and Qwen API availability

### Getting Help

For support, check the documentation or contact the development team.