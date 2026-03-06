# 💼 JobTracker AI

> AI-powered job application tracking system with intelligent resume analysis and matching

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🔐 Authentication & Security
- JWT-based authentication with access & refresh tokens
- Bcrypt password hashing
- Token blacklisting on logout
- Rate limiting (5 requests/min on login)
- Role-based access control

### 💼 Job Management
- Full CRUD operations for job applications
- Status tracking (Saved, Applied, Interview, Offer, Rejected)
- Priority levels (Low, Medium, High)
- Advanced filtering and search
- Pagination support
- Redis caching for performance

### 📄 Resume Analysis (AI-Powered)
- PDF/DOCX resume parsing
- Automatic skill extraction (100+ tech skills)
- Keyword identification using NLP
- Job description matching with scoring algorithm
- Experience matching (years of experience)
- Missing skills identification
- Actionable improvement suggestions

### ✉️ AI Cover Letter Generator (NEW!)
- GPT-3.5 powered personalized cover letters
- Multiple tone options (Professional, Enthusiastic, Creative, Formal)
- Resume + JD analysis for tailored content
- Real-time editing and customization
- Copy to clipboard functionality
- Template fallback when API unavailable

### 📊 Analytics Dashboard
- Application statistics
- Status distribution charts
- Priority breakdown
- Timeline visualization
- Success rate tracking

## 🛠 Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Database:** PostgreSQL 15
- **Cache:** Redis 7
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **NLP:** spaCy (en_core_web_sm)
- **AI:** OpenAI GPT-3.5 (Cover Letter Generation)
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt

### Frontend
- **Framework:** React 18
- **Styling:** Custom CSS with animations
- **HTTP Client:** Axios
- **Routing:** React Router v6

### DevOps
- **Containerization:** Docker & Docker Compose
- **File Storage:** Local/S3 (configurable)
- **Logging:** Custom middleware
- **Testing:** pytest

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                               │
│                    (Streamlit Frontend)                      │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Routes     │→ │ Controllers  │→ │   Services   │      │
│  │  (API Layer) │  │(Business Logic)│ │(NLP, Storage)│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                  ↓                  ↓              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Middleware  │  │    Models    │  │   Schemas    │      │
│  │(Auth, Logger)│  │  (SQLAlchemy)│  │  (Pydantic)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │     Redis    │    │  S3/Local    │
│  (Database)  │    │    (Cache)   │    │   Storage    │
└──────────────┘    └──────────────┘    └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/amit0512-lab/jobtracker-ai.git
cd jobtracker-ai
```

2. **Create environment file**
```bash
cp .env.example .env
```

Edit `.env` and update the values:
```env
APP_NAME=JobTracker
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/jobtracker
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-your-openai-api-key-here
```

3. **Start Docker services**
```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5433
- Redis on port 6379
- FastAPI backend on port 8000

4. **Run database migrations**
```bash
# If running with Docker
docker exec -it jobtracker_app alembic upgrade head

# If running locally
alembic upgrade head
```

5. **Start the frontend** (in a new terminal)
```bash
cd frontend
pip install -r ../requirements.txt
streamlit run app.py
```

6. **Access the application**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout and blacklist token |
| GET | `/api/v1/auth/profile` | Get current user profile |

### Jobs Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/jobs` | Create new job |
| GET | `/api/v1/jobs` | List jobs (paginated, filtered) |
| GET | `/api/v1/jobs/{id}` | Get job details |
| PATCH | `/api/v1/jobs/{id}` | Update job |
| PATCH | `/api/v1/jobs/{id}/status` | Update job status |
| DELETE | `/api/v1/jobs/{id}` | Delete job |

### Resume Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/resume/upload` | Upload and parse resume |
| GET | `/api/v1/resume` | List user's resumes |
| POST | `/api/v1/resume/{id}/analyze` | Analyze resume vs JD |
| DELETE | `/api/v1/resume/{id}` | Delete resume |

### Cover Letter Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/cover-letter/generate` | Generate AI cover letter |
| GET | `/api/v1/cover-letter` | List all cover letters |
| GET | `/api/v1/cover-letter/{id}` | Get cover letter details |
| GET | `/api/v1/cover-letter/job/{job_id}` | Get letters for specific job |
| PATCH | `/api/v1/cover-letter/{id}` | Update cover letter |
| DELETE | `/api/v1/cover-letter/{id}` | Delete cover letter |

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/dashboard` | Get dashboard stats |

**Full API Documentation:** Visit http://localhost:8000/docs after starting the backend

## 📁 Project Structure

```
jobtracker-ai/
├── app/
│   ├── api/
│   │   ├── controllers/      # Business logic
│   │   │   ├── auth_controller.py
│   │   │   ├── job_controller.py
│   │   │   ├── resume_controller.py
│   │   │   └── analytics_controller.py
│   │   └── routes/           # API endpoints
│   │       ├── auth.py
│   │       ├── jobs.py
│   │       ├── resume.py
│   │       └── analytics.py
│   ├── core/                 # Core configurations
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── redis.py
│   │   └── security.py
│   ├── middleware/           # Custom middleware
│   │   ├── auth_middleware.py
│   │   └── logger_middleware.py
│   ├── models/               # Database models
│   │   ├── user.py
│   │   ├── job.py
│   │   └── resume.py
│   ├── schemas/              # Pydantic schemas
│   │   ├── auth.py
│   │   ├── job.py
│   │   └── resume.py
│   ├── services/             # External services
│   │   ├── nlp/
│   │   │   ├── resume_parser.py
│   │   │   └── jd_matcher.py
│   │   └── storage/
│   │       └── s3_service.py
│   └── main.py               # FastAPI app entry
├── frontend/
│   ├── components/           # Reusable components
│   ├── pages/                # Streamlit pages
│   ├── utils/                # Helper functions
│   └── app.py                # Main Streamlit app
├── migrations/               # Alembic migrations
├── tests/                    # Test files
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🎯 Key Features Explained

### 1. NLP-Powered Resume Matching

The system uses spaCy for natural language processing:

```python
# Extract skills from resume
skills = ResumeParser.extract_skills(resume_text)
# Output: ['Python', 'FastAPI', 'PostgreSQL', 'Docker', ...]

# Match against job description
match_result = JDMatcher.calculate_match_score(resume_text, jd_text)
# Output: {
#   "match_score": 78.5,
#   "matched_keywords": ['python', 'api', 'database'],
#   "missing_keywords": ['kubernetes', 'aws'],
#   "suggestions": [...]
# }
```

**Scoring Algorithm:**
- 30% - Technical skills match
- 35% - Keyword overlap
- 35% - Important terms match

### 2. JWT Authentication Flow

```
1. User registers → Password hashed with bcrypt
2. User logs in → Receives access token (30 min) + refresh token (7 days)
3. API requests → Include Bearer token in Authorization header
4. Token expires → Use refresh token to get new access token
5. User logs out → Token blacklisted in Redis
```

### 3. Rate Limiting

Prevents brute force attacks:
- Login endpoint: 5 requests per minute
- Other endpoints: 60 requests per minute
- IP-based tracking using Redis

### 4. Caching Strategy

Redis caching for performance:
- Job listings cached for 5 minutes
- Analysis results cached for 10 minutes
- Automatic cache invalidation on updates

## 🧪 Testing

Run the test suite:

```bash
# Test all endpoints
python test_all_endpoints.py

# Test rate limiter
python test_rate_limiter.py

# Test jobs endpoints
python test_jobs_endpoints.py
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | JobTracker |
| `APP_ENV` | Environment (development/production) | development |
| `DEBUG` | Debug mode | True |
| `SECRET_KEY` | JWT secret key | (required) |
| `DATABASE_URL` | PostgreSQL connection string | (required) |
| `REDIS_URL` | Redis connection string | (required) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | 7 |
| `USE_LOCAL_STORAGE` | Use local storage vs S3 | True |

## 📸 Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Job Management
![Jobs](docs/screenshots/jobs.png)

### Resume Analysis
![Resume Analysis](docs/screenshots/resume-analysis.png)

## 🚢 Deployment

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed production deployment guide including:
- AWS deployment (EC2, RDS, ElastiCache, S3)
- SSL certificate setup
- Load balancer configuration
- CI/CD pipeline with GitHub Actions

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Amit Sharma**
- GitHub: [@amit0512-lab](https://github.com/amit0512-lab)
- LinkedIn: [Amit Sharma](https://www.linkedin.com/in/amit-sharma-28461a249)
- Email: knpknp599@gmail.com

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- spaCy for NLP capabilities
- Streamlit for rapid frontend development
- PostgreSQL and Redis for robust data storage

## 📞 Support

For support, email knpknp599@gmail.com or open an issue on GitHub.

---

⭐ If you found this project helpful, please give it a star!
