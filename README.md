# 🚀 Agents Backend (Production)

Scalable multi-agent AI backend. FastAPI + Celery + Redis + LLM Agents.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-black)](https://fastapi.tiangolo.com)
[![Celery](https://img.shields.io/badge/Celery-5.4-green)](https://docs.celeryq.dev)

## ✨ Features
- **Multi-Agent Orchestration** (ReACT pattern)
- **Async Task Queue** (Celery + Redis)
- **Production Ready** (Docker Compose)
- **Specialized Agents**: Manager, Developer, Tester

## 🚀 Quickstart
```bash
git clone https://github.com/vedant-saini/agents-backend-prod
cd agents-backend-prod
cp .env.example .env
docker-compose up -d
curl http://localhost:8000/health
```

## 🏗️ Architecture
See [ARCHITECTURE.md](./ARCHITECTURE.md)

## 📁 Structure
```
agents/     # AI Agents
core/       # Shared logic
server.py   # FastAPI
orchestrator.py # Coordinator
docker-compose.yml
```

## 🔧 Dev
```bash
pip install -r requirements.txt
docker-compose up redis
celery -A server worker &
uvicorn server:app --reload
```

## 🌐 API
```
GET  /health
POST /tasks  
GET  /tasks/{id}
```

## 🔒 Env
```
OPENAI_API_KEY=sk-...
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```

MIT License.
