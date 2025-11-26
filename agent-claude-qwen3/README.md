# Employee Onboarding Multi-Agent System

A multi-agent backend system for employee onboarding using the deepagents framework under langchain.

## Overview

This system guides new employees through the complete onboarding process including:
1. Identity verification via ID photo upload
2. Personal information collection
3. Position responsibility announcement
4. Account provisioning (email, git)
5. Post-onboarding task reminders

The system uses five specialized agents:
- Onboarding Supervisor (orchestrates the flow)
- Identity Verification (processes ID photos)
- Information Collection (gathers employee details)
- Tool Calling (integrates with MCP for account provisioning)
- Q&A (answers employee questions)

## Features

- Multi-agent architecture using deepagents framework
- Vision-language model integration for ID verification
- REST API for integration with other systems
- Interactive chat interface for direct employee interaction
- MCP tool integration for account provisioning
- Comprehensive testing suite

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

## Usage

### Start the Chat Interface

To start the interactive onboarding agent:

```bash
python main.py chat
```

### Start the API Server

To start the REST API server:

```bash
python main.py serve
```

### Run Tests

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

## Project Structure

```
src/
├── agents/                 # Multi-agent implementations
│   ├── supervisor.py
│   ├── identity_verification.py
│   ├── information_collection.py
│   ├── tool_calling.py
│   └── qa.py
├── models/                 # Data models
│   ├── employee.py
│   ├── onboarding_checklist.py
│   └── credentials.py
├── services/               # Business logic services
│   ├── id_verification_service.py
│   ├── position_service.py
│   └── mcp_client.py
├── utils/                  # Utility functions
│   └── validators.py
└── main.py                 # Entry point

tests/
├── unit/                   # Unit tests
├── integration/            # Integration tests
└── e2e/                    # End-to-end tests

specs/001-employee-onboarding-agents/
├── spec.md                 # Feature specification
├── plan.md                 # Implementation plan
├── research.md             # Research findings
├── data-model.md           # Data model documentation
├── quickstart.md           # Quick start guide
├── contracts/              # API contracts
└── tasks.md                # Implementation tasks
```

## API Documentation

See [API Contracts](specs/001-employee-onboarding-agents/contracts/api.yaml) for detailed API documentation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact the development team or open an issue on the repository.
