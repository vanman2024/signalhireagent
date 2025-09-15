# Quickstart: Autonomous Lead Generation System Development

## Prerequisites
- Python 3.11+
- Supabase account (managed PostgreSQL)
- SignalHire API key
- Railway account (for deployment)

## Single Service Setup
1. Clone repo and ensure existing CLI is working:
   ```bash
   git checkout 003-autonomous-lead-generation
   signalhire doctor  # Verify existing CLI works (runs slower due to checks)
   ```

2. Install dependencies (existing + new MCP server deps):
   ```bash
   pip install -e .[dev]
   # New dependencies: fastapi, uvicorn, apscheduler, sqlalchemy
   ```

3. Set up Supabase and configure environment:
   ```bash
   cp .env.example .env
   # Configure: SUPABASE_URL, SUPABASE_KEY, SIGNALHIRE_API_KEY, ANTHROPIC_API_KEY
   ```

4. Run database migrations:
   ```bash
   python3 -m src.models.workflow init  # Create workflow tables in Supabase
   ```

5. Start single FastAPI service (hosts MCP server + HTTP endpoints + scheduler):
   ```bash
   uvicorn src.services.mcp_server:app --reload --port 8000
   ```

## Testing MCP Tools
Test each MCP tool directly via FastAPI docs at `http://localhost:8000/docs`:

1. **Test search_by_query**:
   ```bash
   curl -X POST "http://localhost:8000/mcp/search_by_query" \
     -H "Content-Type: application/json" \
     -d '{"title": "Software Engineer", "location": "California", "size": 5}'
   ```

2. **Test get_credits**:
   ```bash
   curl -X POST "http://localhost:8000/mcp/get_credits"
   ```

3. **Validate against CLI**: Compare MCP tool output with CLI equivalent:
   ```bash
   # CLI command
   signalhire search --title "Software Engineer" --location "California" --size 5
   # Should match MCP search_by_query output
   ```

## Agent Integration Testing
Once Phase B is implemented:
```bash
# Test agent workflow
python3 -c "
from src.lib.agent_interface import AgentInterface
agent = AgentInterface('claude')
result = agent.execute_workflow('find 5 software engineers in California')
print(result)
"
```

## Running Tests
```bash
# Contract tests (with httpx mocking)
python3 -m pytest tests/contract/ -v

# Live smoke test (uses 1 search credit)
RUN_LIVE=1 python3 -m pytest tests/integration/test_live_smoke.py -v

# All tests
python3 -m pytest
```

## Docker Deployment
Build and run single container:
```bash
docker build -t signalhire-mcp .
docker run -p 8000:8000 \
  -e DATABASE_URL=$DATABASE_URL \
  -e SIGNALHIRE_API_KEY=$SIGNALHIRE_API_KEY \
  signalhire-mcp
```

## Production Deployment to Railway

Railway is the recommended platform because it supports:
- ✅ Single container deployment
- ✅ External database integration (Supabase)
- ✅ Persistent processes (APScheduler works perfectly)
- ✅ Environment variable management
- ✅ Simple GitHub integration

### Railway Setup

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Create Railway project**:
   ```bash
   railway init
   # Note: Using external Supabase database instead of Railway's built-in PostgreSQL
   ```

3. **Configure environment variables in Railway dashboard**:
   ```
   SIGNALHIRE_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key_here
   ```

4. **Create Dockerfile** (if not exists):
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8000
   CMD ["uvicorn", "src.services.mcp_server:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

5. **Deploy**:
   ```bash
   railway up  # Deploys current directory
   ```

### Railway + Supabase Benefits for Autonomous System
- **Persistent Scheduler**: APScheduler runs continuously for autonomous workflows
- **Managed Database**: Supabase provides PostgreSQL with real-time features
- **Automatic HTTPS**: Railway provides secure endpoints
- **Easy Scaling**: Can upgrade resources as needed
- **Monitoring**: Built-in logs and metrics
- **GitHub Integration**: Auto-deploy on git push
- **Database Features**: Supabase adds real-time subscriptions, auth, and dashboard

### Monitoring Production
```bash
# Check logs
railway logs

# Check database (via Supabase dashboard)
# Visit: https://app.supabase.com/project/your-project/editor

# Get deployment URL
railway domain
```

Your autonomous lead generation system will be available at: `https://your-app.railway.app`
