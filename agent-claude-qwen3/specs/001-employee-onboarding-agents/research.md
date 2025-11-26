# Research Findings: Employee Onboarding Multi-Agent Backend System

## Storage Solution

### Decision
Use SQLite for local development and PostgreSQL for production deployments.

### Rationale
- SQLite is lightweight and requires no additional setup for development
- PostgreSQL provides robust features needed for production (transactions, concurrency, etc.)
- Both are well-supported by SQLAlchemy ORM
- Follows the principle of starting simple and scaling as needed

### Alternatives Considered
- MongoDB: More complex setup, overkill for this relational data
- Redis: Good for caching but not suitable as primary storage
- File-based storage: Not durable enough for production use

## DeepAgents Framework Best Practices

### Decision
Follow the agent composition pattern with a central supervisor coordinating specialized agents.

### Rationale
- DeepAgents is designed for multi-agent systems with clear separation of concerns
- Each agent should have a single responsibility (SRP)
- Communication between agents should go through the supervisor to maintain control
- State management should be centralized in the supervisor

### Implementation Approach
1. Create specialized agents for each onboarding step:
   - IdentityVerificationAgent for ID photo processing
   - InformationCollectionAgent for gathering employee details
   - ToolCallingAgent for MCP integrations
   - QAAgent for answering questions
   - SupervisorAgent to orchestrate the flow

2. Use LangGraph for state management and workflow control
3. Implement proper error handling and recovery mechanisms

## Qwen Model Integration

### Decision
Use Qwen3-Max for general reasoning and Qwen3-VL-Max for vision-language tasks.

### Rationale
- Qwen3-Max provides strong general language understanding for conversations
- Qwen3-VL-Max specializes in image understanding for ID verification
- Both models are accessible through the DashScope API
- Models can be swapped easily through configuration

### Implementation Approach
1. Create model wrapper classes for each Qwen variant
2. Implement retry logic for API calls
3. Add proper error handling for model limitations
4. Cache responses where appropriate to reduce API costs

## MCP Integration Patterns

### Decision
Use synchronous MCP calls with timeout handling for account provisioning.

### Rationale
- Account provisioning is a critical step that shouldn't be deferred
- Synchronous calls provide immediate feedback to users
- Timeout handling prevents the system from hanging indefinitely
- Retry logic can handle transient failures

### Implementation Approach
1. Create an MCP client wrapper with standardized methods
2. Implement timeout and retry mechanisms
3. Log all MCP interactions for debugging and auditing
4. Provide fallback mechanisms for critical provisioning failures