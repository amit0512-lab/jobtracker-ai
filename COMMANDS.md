# 🚀 Quick Command Reference - JobTracker AI

Essential commands for development and deployment.

## 📦 Initial Setup

```bash
# Clone repository
git clone https://github.com/yourusername/jobtracker-ai.git
cd jobtracker-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Setup environment
cp .env.example .env
# Edit .env with your values

# Start Docker services
docker-compose up -d

# Run migrations
alembic upgrade head
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker logs -f jobtracker_app
docker logs -f jobtracker_db
docker logs -f jobtracker_redis

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up -d --build

# Stop and remove volumes (deletes data!)
docker-compose down -v

# Check running containers
docker ps

# Execute command in container
docker exec -it jobtracker_app bash
docker exec -it jobtracker_db psql -U postgres -d jobtracker
docker exec -it jobtracker_redis redis-cli
```

## 🗄️ Database Commands

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current migration
alembic current

# Connect to database
docker exec -it jobtracker_db psql -U postgres -d jobtracker

# Backup database
docker exec jobtracker_db pg_dump -U postgres jobtracker > backup.sql

# Restore database
docker exec -i jobtracker_db psql -U postgres jobtracker < backup.sql
```

## 🔴 Redis Commands

```bash
# Connect to Redis CLI
docker exec -it jobtracker_redis redis-cli

# Inside Redis CLI:
PING                          # Test connection
KEYS *                        # List all keys
GET key_name                  # Get value
DEL key_name                  # Delete key
FLUSHALL                      # Clear all data (careful!)
INFO                          # Server info
```

## 🚀 Running the Application

```bash
# Start backend (development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start backend (production)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Start frontend
cd frontend
streamlit run app.py

# Start frontend on specific port
streamlit run app.py --server.port 8502
```

## 🧪 Testing Commands

```bash
# Run all tests
python test_all_endpoints.py

# Test specific endpoints
python test_jobs_endpoints.py
python test_rate_limiter.py

# Run with pytest (if configured)
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

## 📝 Git Commands

```bash
# Initialize repository
git init

# Check status
git status

# Add files
git add .
git add specific_file.py

# Commit changes
git commit -m "Your message"

# View commit history
git log
git log --oneline

# Create branch
git checkout -b feature-name

# Switch branch
git checkout main

# Merge branch
git merge feature-name

# Push to GitHub
git push origin main

# Pull from GitHub
git pull origin main

# View remotes
git remote -v

# Add remote
git remote add origin https://github.com/username/repo.git
```

## 🔍 Debugging Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list
pip freeze

# Check Docker version
docker --version
docker-compose --version

# Check port usage (Windows)
netstat -ano | findstr :8000
netstat -ano | findstr :5433

# Check port usage (Mac/Linux)
lsof -i :8000
lsof -i :5433

# Kill process on port (Windows)
taskkill /PID <PID> /F

# Kill process on port (Mac/Linux)
kill -9 <PID>

# Check disk space
docker system df

# Clean up Docker
docker system prune -a
docker volume prune
```

## 📊 Monitoring Commands

```bash
# View container stats
docker stats

# View container resource usage
docker stats jobtracker_app

# Check database size
docker exec jobtracker_db psql -U postgres -d jobtracker -c "SELECT pg_size_pretty(pg_database_size('jobtracker'));"

# Check Redis memory usage
docker exec jobtracker_redis redis-cli INFO memory

# View application logs
tail -f app.log

# View Docker logs with timestamp
docker-compose logs -f --timestamps
```

## 🔧 Maintenance Commands

```bash
# Update dependencies
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt

# Clean Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Clean Docker
docker system prune -a --volumes

# Backup everything
tar -czf backup.tar.gz app/ frontend/ migrations/ requirements.txt docker-compose.yml

# Check for security vulnerabilities
pip install safety
safety check
```

## 🌐 API Testing Commands

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","full_name":"Test User","password":"password123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get jobs (with token)
curl http://localhost:8000/api/v1/jobs \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Create job
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title":"Software Engineer","company":"Google","location":"Remote"}'
```

## 📦 Deployment Commands

```bash
# Build Docker image
docker build -t jobtracker-app .

# Tag image for registry
docker tag jobtracker-app username/jobtracker-app:latest

# Push to Docker Hub
docker push username/jobtracker-app:latest

# Pull from Docker Hub
docker pull username/jobtracker-app:latest

# Run production container
docker run -d \
  --name jobtracker \
  -p 8000:8000 \
  --env-file .env.production \
  username/jobtracker-app:latest
```

## 🔐 Security Commands

```bash
# Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Or using OpenSSL
openssl rand -hex 32

# Check for exposed secrets
git log --all --full-history --source -- .env

# Remove file from git history (if accidentally committed)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

## 📱 Quick Shortcuts

```bash
# Full restart
docker-compose down && docker-compose up -d && docker-compose logs -f

# Reset database
docker-compose down -v && docker-compose up -d && alembic upgrade head

# Update and restart
git pull && docker-compose down && docker-compose up -d --build

# Backup before update
docker exec jobtracker_db pg_dump -U postgres jobtracker > backup_$(date +%Y%m%d).sql

# Check everything is running
docker ps && curl http://localhost:8000/health && curl http://localhost:8501
```

## 🆘 Emergency Commands

```bash
# Stop everything immediately
docker-compose down
pkill -f uvicorn
pkill -f streamlit

# Force remove containers
docker rm -f $(docker ps -aq)

# Remove all volumes (DELETES ALL DATA!)
docker volume rm $(docker volume ls -q)

# Reset Docker completely
docker system prune -a --volumes

# Restore from backup
docker exec -i jobtracker_db psql -U postgres jobtracker < backup.sql
```

## 💡 Pro Tips

```bash
# Create aliases for common commands (add to ~/.bashrc or ~/.zshrc)
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dps='docker ps'

# Then use:
dc up -d
dcl
```

## 📚 Useful One-Liners

```bash
# Count lines of code
find app -name "*.py" | xargs wc -l

# Find TODO comments
grep -r "TODO" app/

# Check for print statements
grep -r "print(" app/ --include="*.py"

# List all API endpoints
grep -r "@router" app/api/routes/ --include="*.py"

# Check database table sizes
docker exec jobtracker_db psql -U postgres -d jobtracker -c "\dt+"

# Monitor Redis keys in real-time
docker exec jobtracker_redis redis-cli MONITOR
```

---

**Bookmark this file for quick reference!** 📌
