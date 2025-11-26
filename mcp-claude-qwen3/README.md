# MCP Account Provisioning Server

A service for provisioning email and git accounts based on Chinese names and ID numbers.

## Features

- Provision email accounts with format: `english_name@email.com`
- Provision git accounts with format: `english_name@git.com`
- Batch account provisioning for multiple employees
- Chinese ID number validation according to GB 11643-1999 standard
- Secure password generation

## Prerequisites

- Python 3.12+
- uv package manager

## Installation

```bash
uv sync
```

## Configuration

Create a `.env` file with the following content:

```env
PORT=9102
```

## Usage

Start the server:

```bash
python src/main.py
```

The server will be available at `http://localhost:9102`

## API Endpoints

### Provision Email Account

```bash
curl -X POST http://localhost:9102/provision/email \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "id_number": "110101199003072958"
  }'
```

Response:

```json
{
  "username": "zhangsan@email.com",
  "password": "A1b2C3d4E5f6!"
}
```

### Provision Git Account

```bash
curl -X POST http://localhost:9102/provision/git \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "id_number": "110101199003072958"
  }'
```

Response:

```json
{
  "username": "zhangsan@git.com",
  "password": "A1b2C3d4E5f6!"
}
```

### Batch Provisioning

```bash
curl -X POST http://localhost:9102/provision/batch \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "name": "张三",
        "id_number": "110101199003072958",
        "account_types": ["email", "git"]
      },
      {
        "name": "李四",
        "id_number": "110101199003073418",
        "account_types": ["email"]
      }
    ]
  }'
```

Response:

```json
{
  "results": [
    {
      "name": "张三",
      "id_number": "110101199003072958",
      "accounts": [
        {
          "username": "zhangsan@email.com",
          "password": "A1b2C3d4E5f6!"
        },
        {
          "username": "zhangsan@git.com",
          "password": "B2c3D4e5F6g7@"
        }
      ],
      "error": null
    },
    {
      "name": "李四",
      "id_number": "110101199003073418",
      "accounts": [
        {
          "username": "lisi@email.com",
          "password": "C3d4E5f6G7h8#"
        }
      ],
      "error": null
    }
  ]
}
```

### Environment Variables

- `API_TOKEN`: Custom authorization token (default: "secret-token")

## MCP Client Configuration

```json
{
  "mcpServers": {
    "finance-data": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://127.0.0.1:9102/mcp", "--header", "Authorization:Bearer secret-token"]
    }
  }
}
```

## use in langchain

```python
MultiServerMCPClient(
    {
        "account_apply": {
            "url": "http://127.0.0.1:9102/mcp",
            "headers": {
                "Authorization":"Bearer secret-token"
            },
            "transport": "streamable_http",
        }
    }
)
```

## Error Responses

- `422 Unprocessable Entity`: Invalid ID number format
- `500 Internal Server Error`: Unexpected server error

## Testing

Run tests:

```bash
pytest
```
