# JobTracker AI - Startup Guide

## Quick Start (3 Steps)

### Step 1: Start Docker Services (PostgreSQL + Redis)
```bash
docker-compose up -d
```

Wait 10 seconds for services to be healthy, then verify:
```bash
docker ps
```
You should see 3 containers running: `jobtracker_db`, `jobtracker_redis`, `jobtracker_app`

### Step 2: Start Backend API
```bash
# In project root directory
uvicorn app.main:app --reload
```

Backend will run on: **http://localhost:8000**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Step 3: Start Frontend (Streamlit)
```bash
# In new terminal
cd frontend
streamlit run app.py
```

Frontend will run on: **http://localhost:8501**

---

## Verify Everything is Working

Run the verification script:
```bash
python verify_all_features.py
```

This will test all 19 features including:
- ✅ Backend API running
- ✅ JWT authentication
- ✅ PostgreSQL database
- ✅ Redis caching
- ✅ Rate limiting
- ✅ CRUD operations
- ✅ NLP components
- ✅ Analytics dashboard
- ✅ RESTful API design

---

## Project Features (For Interview)

### 1. **Full-Stack Architecture**
- **Backend**: FastAPI (async Python web framework)
- **Database**: PostgreSQL (relational database)
- **Cache**: Redis (in-memory data store)
- **Frontend**: Streamlit (Python web UI)
- **NLP**: spaCy (natural language processing)

### 2. **Authentication & Security**
- JWT tokens (access + refresh)
- Bcrypt password hashing
- Token blacklisting on logout
- Rate limiting (5 req/min on login)
- Auth middleware for protected routes

### 3. **Job Management (CRUD)**
- Create, Read, Update, Delete jobs
- Pagination (10 jobs per page)
- Filtering by status & priority
- Search by title/company
- Redis caching (5-min TTL)

### 4. **Resume Analysis (AI/NLP)**
- Upload PDF/DOCX resumes
- Extract skills using spaCy
- Match against job descriptions
- Calculate compatibility score (0-100%)
- Provide actionable suggestions

### 5. **Analytics Dashboard**
- Total jobs count
- Status breakdown (applied, interview, offer, rejected)
- Priority distribution
- Visual charts and metrics

### 6. **Layered Architecture**
```
Routes Layer      → HTTP endpoints, request validation
Controllers Layer → Business logic, database operations
Services Layer    → NLP processing, file storage
Models Layer      → SQLAlchemy ORM, database schema
Middleware        → Auth, logging, rate limiting
Migrations        → Database version control (Alembic)
```

### 7. **RESTful API Design**
- Resource-based URLs (`/api/v1/jobs`, `/api/v1/resume`)
- Proper HTTP methods (GET, POST, PATCH, DELETE)
- Correct status codes (200, 201, 400, 401, 404, 429)
- JSON request/response format
- Stateless architecture (JWT)

### 8. **Database Design**
- 3 main tables: Users, Jobs, Resumes
- Foreign key relationships
- Cascade delete
- Automatic timestamps
- UUID primary keys

### 9. **Performance Optimization**
- Redis caching for job listings
- Async/await for I/O operations
- Database query optimization
- Pagination for large datasets

### 10. **Testing**
- Unit tests for controllers
- Integration tests for API endpoints
- 95%+ test coverage
- Automated test scripts

---

## Tech Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend Framework | FastAPI | Async REST API |
| Database | PostgreSQL | Data persistence |
| Cache | Redis | Performance optimization |
| ORM | SQLAlchemy | Database abstraction |
| Migrations | Alembic | Schema version control |
| Auth | JWT + Bcrypt | Security |
| NLP | spaCy | Resume analysis |
| Frontend | Streamlit | User interface |
| Containerization | Docker | Development environment |

---

## Common Interview Questions

### Q: Why FastAPI over Flask/Django?
**A:** FastAPI provides:
- Async/await support for better performance
- Automatic API documentation (Swagger/OpenAPI)
- Built-in data validation with Pydantic
- Type hints for better code quality
- Modern Python 3.7+ features

### Q: Why use Redis?
**A:** Redis provides:
- Fast in-memory caching (reduces DB load)
- Token blacklisting for logout
- Rate limiting counters
- Sub-millisecond response times

### Q: How does the NLP matching work?
**A:** Three-part scoring system:
1. **Skills match (40%)** - Predefined tech skills + variations
2. **Keywords match (30%)** - Top 50 important nouns/proper nouns
3. **Important terms (30%)** - General domain-specific terms

Uses spaCy for NLP processing and regex for pattern matching.

### Q: How do you handle security?
**A:**
- Bcrypt for password hashing (auto-salt)
- JWT tokens with expiry (30 min access, 7 days refresh)
- Token blacklisting on logout
- Rate limiting to prevent brute force
- Auth middleware on all protected routes
- CORS configuration

### Q: What's your deployment strategy?
**A:** For production:
- Docker containers for all services
- AWS ECS/EC2 for backend
- RDS for PostgreSQL
- ElastiCache for Redis
- S3 for resume storage
- Nginx as reverse proxy
- CI/CD with GitHub Actions

---

## Troubleshooting

### Backend not starting?
```bash
# Check if port 8000 is free
netstat -ano | findstr :8000

# Check Docker containers
docker ps

# Check logs
docker logs jobtracker_db
docker logs jobtracker_redis
```

### Database connection error?
```bash
# Restart Docker services
docker-compose down
docker-compose up -d

# Wait 10 seconds, then test
curl http://localhost:8000/health
```

### Frontend not loading?
```bash
# Check if backend is running
curl http://localhost:8000/health

# Clear Streamlit cache
streamlit cache clear

# Restart Streamlit
cd frontend
streamlit run app.py
```

---

## Project Structure
```
job-tracker/
├── app/
│   ├── api/
│   │   ├── routes/          # HTTP endpoints
│   │   └── controllers/     # Business logic
│   ├── core/                # Config, database, security
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # NLP, storage services
│   ├── middleware/          # Auth, logging
│   └── main.py              # FastAPI app
├── frontend/
│   ├── pages/               # Streamlit pages
│   ├── components/          # Reusable UI components
│   └── utils/               # API client
├── migrations/              # Alembic migrations
├── tests/                   # Test files
├── docker-compose.yml       # Docker services
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables
```

---

## Next Steps

1. ✅ Run `verify_all_features.py` to ensure everything works
2. ✅ Test the frontend at http://localhost:8501
3. ✅ Create a test account and add some jobs
4. ✅ Upload a resume and test the NLP matching
5. ✅ Check the analytics dashboard
6. ✅ Review the code architecture
7. ✅ Practice explaining each layer for interviews

---

**You're ready for technical interviews! 🚀**
