# 🏗️ Multi-Agent Backend Architecture

Production system for scalable AI agent orchestration.

## System Flow
```
Client → FastAPI (server.py) → Celery Queue (Redis) → Agent Workers
                    ↓                    ↓
               Orchestrator       Specialized Agents
                    ↓                    ↓
              Redis (state)       Tool Execution + LLM
                    ↓
               Results → FastAPI
```

## Components

### FastAPI Server (`server.py`)
- HTTP endpoints + async queuing
- `/health`, `/tasks`, `/tasks/{id}`

### Celery + Redis
```
Broker: redis://localhost:6379/0
Backend: redis://localhost:6379/1
```
- Distributed workers
- `celery -A server worker`

### Orchestrator (`orchestrator.py`)
- ReACT: Reason → Act → Observe
- Dynamic agent routing

### Agents (`agents/`)
- **Manager**: Workflow coordination
- **Developer**: Code gen/review  
- **Tester**: Test execution

## Scaling
```yaml
services:
  api:     # 1-4 replicas
  worker:  # 4-16 replicas
  redis:
```

## Folder Structure
```
agents/         # LLM agents
core/           # Utilities
integrations/   # External tools
metrics/        # Observability
utils/
```
