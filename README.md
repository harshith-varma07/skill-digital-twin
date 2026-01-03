# 🎯 Skill Digital Twin

An AI-powered skill profiling, gap analysis, and personalized learning roadmap system that creates a dynamic visual representation of a learner's skills, identifies gaps, and generates personalized learning paths.

## 🌟 Features

### Core Features
- **Skill Digital Twin Visualization**: Interactive force-directed graph showing skills, mastery levels, and relationships
- **AI-Powered Skill Extraction**: Extract skills from resumes, academic backgrounds, and self-descriptions using NLP
- **Comprehensive Gap Analysis**: Compare skills against career role requirements
- **Personalized Learning Roadmaps**: AI-generated learning paths with YouTube video recommendations
- **Career Alignment Engine**: Match skills against real-world job roles with readiness percentages
- **Adaptive Assessments**: AI-generated diagnostic questions to validate understanding

### Technical Highlights
- Real-time skill mastery tracking
- Structured skill ontology with categories and relationships
- YouTube API integration for curated video content
- OpenAI GPT-4 for intelligent content generation
- Async PostgreSQL database with SQLAlchemy
- Modern React frontend with D3.js visualizations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │Dashboard │  │ Digital  │  │ Learning │  │  Career  │    │
│  │          │  │   Twin   │  │ Roadmap  │  │ Alignment│    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI + Python)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │   Auth   │  │  Skills  │  │ Learning │  │  Career  │    │
│  │   API    │  │   API    │  │    API   │  │    API   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│                              │                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   Service Layer                       │   │
│  │  ┌────────────┐  ┌─────────────┐  ┌────────────┐    │   │
│  │  │ AI Service │  │ Skill Ext.  │  │ YouTube    │    │   │
│  │  │  (GPT-4)   │  │   Service   │  │  Service   │    │   │
│  │  └────────────┘  └─────────────┘  └────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │   OpenAI    │      │
│  │   Database   │  │    Cache     │  │     API     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional, for caching)

**OR**

- Docker & Docker Compose (recommended for quick setup)

### 🐳 Docker Deployment (Recommended)

The easiest way to run the entire application is using Docker Compose.

#### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd skill-digital-twin
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (OPENAI_API_KEY, YOUTUBE_API_KEY)
   ```

3. **Build and start all services**
   ```bash
   docker compose up -d
   ```

   This will start:
   - PostgreSQL database (port 5432)
   - Redis cache (port 6379)
   - Backend API (port 8000)
   - Frontend application (port 80)

4. **Access the application**
   - Frontend: `http://localhost`
   - Backend API: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`

5. **View logs**
   ```bash
   docker compose logs -f
   ```

6. **Stop all services**
   ```bash
   docker compose down
   ```

7. **Stop and remove volumes (clean slate)**
   ```bash
   docker compose down -v
   ```

#### Development Mode with Hot Reload

For development with hot-reloading:

```bash
docker compose -f docker-compose.dev.yml up
```

This runs:
- Backend with auto-reload on code changes (port 8000)
- Frontend with Vite dev server (port 3000)
- PostgreSQL and Redis

Access at `http://localhost:3000` (frontend) and `http://localhost:8000` (backend)

#### Docker Commands Reference

```bash
# Rebuild services after code changes
docker compose build

# Rebuild specific service
docker compose build backend

# Start specific service
docker compose up backend

# View service logs
docker compose logs backend -f

# Execute commands in running container
docker compose exec backend python -m app.seed_data

# Access database
docker compose exec postgres psql -U postgres -d skill_digital_twin
```

### Manual Setup (Without Docker)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   # Create PostgreSQL database
   createdb skill_digital_twin
   
   # Run migrations (tables created on startup)
   ```

6. **Seed initial data**
   ```bash
   python -m app.seed_data
   ```

7. **Start the server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open in browser**
   Navigate to `http://localhost:3000`

## 📚 API Documentation

Once the backend is running, access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register new user |
| `/api/v1/auth/login` | POST | User login |
| `/api/v1/digital-twin/profile` | GET | Get skill digital twin |
| `/api/v1/digital-twin/gap-analysis` | GET | Perform gap analysis |
| `/api/v1/skills/extract` | POST | Extract skills from text |
| `/api/v1/learning/roadmaps/generate` | POST | Generate learning roadmap |
| `/api/v1/careers/alignment/{role_id}` | GET | Get career alignment |
| `/api/v1/assessments/diagnostic` | POST | Create diagnostic assessment |

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/skill_digital_twin

# OpenAI API
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# YouTube API
YOUTUBE_API_KEY=your-youtube-api-key

# JWT Authentication
JWT_SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## 📂 Project Structure

```
skill-digital-twin/
├── backend/
│   ├── app/
│   │   ├── api/           # API route handlers
│   │   ├── core/          # Config, database, security
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic services
│   │   └── main.py        # FastAPI application
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API service layer
│   │   ├── store/         # State management (Zustand)
│   │   └── App.tsx        # Main application
│   ├── package.json
│   └── .env.example
└── README.md
```

## 🎨 Features Walkthrough

### 1. Skill Digital Twin
- Visual force-directed graph of all skills
- Color-coded by category and mastery level
- Interactive node exploration
- Skill relationships and prerequisites

### 2. Gap Analysis
- Compare skills against career requirements
- Priority-based skill gap identification
- Actionable recommendations

### 3. Learning Roadmaps
- AI-generated learning paths
- Curated YouTube video recommendations
- Progress tracking
- Practice questions for validation

### 4. Career Alignment
- Match against multiple career roles
- Readiness percentage calculation
- Upskilling recommendations
- Time-to-ready estimates

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Async ORM
- **PostgreSQL** - Primary database
- **OpenAI GPT-4** - AI content generation
- **spaCy** - NLP processing

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Query** - Data fetching
- **Zustand** - State management
- **D3.js / react-force-graph-2d** - Visualizations
- **Recharts** - Charts

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For support, please open an issue in the GitHub repository.
