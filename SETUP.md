# 🚀 JobTracker AI - Complete Setup Guide

This guide will help you set up and run JobTracker AI on your local machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher** - [Download](https://www.python.org/downloads/)
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download](https://git-scm.com/downloads/)

## 🔧 Step-by-Step Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/jobtracker-ai.git
cd jobtracker-ai
```

### Step 2: Create Virtual Environment (Optional but Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### Step 5: Setup Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Open `.env` in a text editor and update if needed:
```env
APP_NAME=JobTracker
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/jobtracker
REDIS_URL=redis://localhost:6379
USE_LOCAL_STORAGE=True
```

**Important:** For production, generate a strong SECRET_KEY:
```bash
# On Mac/Linux
openssl rand -hex 32

# On Windows (PowerShell)
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 6: Start Docker Services

Start PostgreSQL and Redis using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- **PostgreSQL** on port 5433
- **Redis** on port 6379
- **FastAPI Backend** on port 8000

**Verify services are running:**
```bash
docker ps
```

You should see three containers running:
- `jobtracker_app`
- `jobtracker_db`
- `jobtracker_redis`

### Step 7: Run Database Migrations

Create the database tables:

```bash
# If using Docker
docker exec -it jobtracker_app alembic upgrade head

# If running locally
alembic upgrade head
```

### Step 8: Verify Backend is Running

Open your browser and visit:
- **API Health Check:** http://localhost:8000/health
- **API Documentation:** http://localhost:8000/docs

You should see the interactive API documentation (Swagger UI).

### Step 9: Start the Frontend

Open a **new terminal** (keep the backend running):

```bash
cd frontend
streamlit run app.py
```

The frontend will open automatically in your browser at http://localhost:8501

## ✅ Verification Checklist

Test that everything is working:

### 1. Backend Health Check
```bash
curl http://localhost:8000/health
```
Expected response: `{"status":"ok","app":"JobTracker"}`

### 2. Database Connection
```bash
docker exec -it jobtracker_db psql -U postgres -d jobtracker -c "\dt"
```
You should see tables: `users`, `jobs`, `resumes`

### 3. Redis Connection
```bash
docker exec -it jobtracker_redis redis-cli ping
```
Expected response: `PONG`

### 4. Frontend Access
Visit http://localhost:8501 - You should see the login/register page

## 🎯 First Time Usage

### 1. Register a New Account
1. Go to http://localhost:8501
2. Click "Register" tab
3. Fill in:
   - Full Name: Your Name
   - Email: your.email@example.com
   - Password: (choose a strong password)
4. Click "Register"

### 2. Login
1. Use your email and password to login
2. You'll be redirected to the dashboard

### 3. Add Your First Job
1. Navigate to "Jobs" page
2. Click "Add New Job"
3. Fill in job details
4. Click "Add Job"

### 4. Upload a Resume
1. Navigate to "Resume" page
2. Click "Upload New Resume"
3. Select a PDF or DOCX file
4. Optionally link to a job
5. Click "Upload Resume"

### 5. Analyze Resume
1. On the Resume page, find your uploaded resume
2. Click "Analyze"
3. Select a job to match against
4. Click "Analyze Now"
5. View match score and suggestions

## 🐛 Troubleshooting

### Issue: Port Already in Use

**Error:** `Port 5433 is already allocated`

**Solution:**
```bash
# Stop all Docker containers
docker-compose down

# Check what's using the port
# Windows
netstat -ano | findstr :5433

# Mac/Linux
lsof -i :5433

# Change port in docker-compose.yml if needed
```

### Issue: Database Connection Failed

**Error:** `could not connect to server`

**Solution:**
```bash
# Check if PostgreSQL container is running
docker ps

# View container logs
docker logs jobtracker_db

# Restart containers
docker-compose restart
```

### Issue: Redis Connection Failed

**Error:** `Error connecting to Redis`

**Solution:**
```bash
# Check if Redis container is running
docker ps

# Test Redis connection
docker exec -it jobtracker_redis redis-cli ping

# Restart Redis
docker-compose restart redis
```

### Issue: spaCy Model Not Found

**Error:** `Can't find model 'en_core_web_sm'`

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: Module Not Found

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Make sure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt
```

### Issue: Alembic Migration Failed

**Error:** `Target database is not up to date`

**Solution:**
```bash
# Check current migration status
alembic current

# View migration history
alembic history

# Upgrade to latest
alembic upgrade head

# If still failing, reset database (WARNING: Deletes all data)
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

## 🔄 Common Commands

### Start Everything
```bash
# Start Docker services
docker-compose up -d

# Start frontend (in separate terminal)
cd frontend
streamlit run app.py
```

### Stop Everything
```bash
# Stop Docker services
docker-compose down

# Stop frontend: Press Ctrl+C in the terminal
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker logs -f jobtracker_app
docker logs -f jobtracker_db
docker logs -f jobtracker_redis
```

### Reset Database (Deletes All Data!)
```bash
docker-compose down -v
docker-compose up -d
docker exec -it jobtracker_app alembic upgrade head
```

### Run Tests
```bash
# Test all endpoints
python test_all_endpoints.py

# Test rate limiter
python test_rate_limiter.py

# Test jobs endpoints
python test_jobs_endpoints.py
```

## 📊 Development Workflow

### Making Code Changes

1. **Backend changes:**
   - Edit files in `app/` directory
   - Backend auto-reloads (if using `--reload` flag)
   - Test at http://localhost:8000/docs

2. **Frontend changes:**
   - Edit files in `frontend/` directory
   - Streamlit auto-reloads on save
   - Refresh browser to see changes

3. **Database schema changes:**
   ```bash
   # Create new migration
   alembic revision --autogenerate -m "description of change"
   
   # Apply migration
   alembic upgrade head
   ```

### Adding New Dependencies

1. Install the package:
   ```bash
   pip install package-name
   ```

2. Update requirements.txt:
   ```bash
   pip freeze > requirements.txt
   ```

3. Rebuild Docker image:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

## 🌐 Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:8501 | (Register new account) |
| Backend API | http://localhost:8000 | N/A |
| API Docs | http://localhost:8000/docs | N/A |
| PostgreSQL | localhost:5433 | postgres/postgres |
| Redis | localhost:6379 | (no password) |

## 📝 Next Steps

1. ✅ Complete the setup above
2. 📖 Read the [README.md](README.md) for feature overview
3. 🎯 Try the [API Documentation](http://localhost:8000/docs)
4. 🧪 Run the test suite
5. 🚀 Start building!

## 💡 Tips

- Keep Docker Desktop running while developing
- Use the API docs at `/docs` to test endpoints
- Check logs if something isn't working
- The frontend auto-reloads on file changes
- Use `docker-compose restart` to restart services

## 🆘 Need Help?

- Check the [Troubleshooting](#-troubleshooting) section above
- Review logs: `docker-compose logs -f`
- Open an issue on GitHub
- Check existing issues for solutions

---

Happy coding! 🎉
