# 🏗️ Tushle AI Automation Dashboard - Project Structure

## 📁 Root Directory Structure

```
lehar/
├── 📁 .github/                    # GitHub workflows and templates
│   └── copilot-instructions.md   # Copilot workspace instructions
├── 📁 .vscode/                    # VS Code workspace settings
├── 📁 backend/                    # FastAPI backend application
├── 📁 frontend/                   # React TypeScript frontend
├── 📁 scripts/                    # Utility and maintenance scripts
├── 📁 docs/                       # Project documentation
├── 📁 configs/                    # Configuration files
├── 📁 deployment/                 # Deployment configurations
└── 📄 README.md                   # Main project documentation
```

## 🔧 Backend Structure (`/backend/`)

```
backend/
├── 📁 app/                        # Main application code
│   ├── 📁 api/                    # API routes and endpoints
│   │   └── v1/routes/             # Version 1 API routes
│   ├── 📁 core/                   # Core application logic
│   │   ├── config.py              # Configuration settings
│   │   └── security.py            # Authentication & security
│   ├── 📁 db/                     # Database configuration
│   │   └── database.py            # Database connection setup
│   ├── 📁 models/                 # SQLAlchemy database models
│   ├── 📁 services/               # Business logic services
│   │   ├── trending_service.py    # 15-source content intelligence
│   │   ├── pdf_report_service.py  # Tushle AI PDF generation
│   │   └── llm_service.py         # Groq AI integration
│   └── 📁 tasks/                  # Celery background tasks
├── 📁 alembic/                    # Database migrations
├── 📁 data/                       # Database files
│   └── automation_dashboard.db    # SQLite database
├── 📁 reports/                    # Generated reports storage
│   └── pdf/                       # PDF reports folder
├── 📁 examples/                   # Example scripts and demos
├── 📄 requirements.txt            # Python dependencies
├── 📄 Dockerfile                  # Docker container config
├── 📄 Procfile                    # Deployment process file
├── 📄 .env.example               # Environment variables template
└── 📄 alembic.ini                # Database migration config
```

## 🎨 Frontend Structure (`/frontend/`)

```
frontend/
├── 📁 src/                        # Source code
│   ├── 📁 components/             # Reusable UI components
│   │   └── ui/                    # shadcn/ui components
│   ├── 📁 pages/                  # Application pages/routes
│   │   ├── ContentEngine.tsx      # Main content intelligence page
│   │   ├── Dashboard.tsx          # Analytics dashboard
│   │   ├── Clients.tsx            # Client management
│   │   └── ...                    # Other pages
│   ├── 📁 contexts/               # React contexts
│   ├── 📁 lib/                    # Utility libraries
│   │   ├── api.ts                 # API client configuration
│   │   └── utils.ts               # Utility functions
│   └── 📁 types/                  # TypeScript type definitions
├── 📄 package.json               # Node.js dependencies
├── 📄 vite.config.ts             # Vite bundler configuration
├── 📄 tailwind.config.js         # TailwindCSS configuration
├── 📄 tsconfig.json              # TypeScript configuration
├── 📄 Dockerfile                 # Docker container config
└── 📄 nginx.conf                 # Nginx configuration for production
```

## 🔧 Scripts Directory (`/scripts/`)

```
scripts/
├── 📁 database/                   # Database management scripts
│   ├── create_dummy_clients.py    # Create test client data
│   ├── create_dummy_data.py       # Create comprehensive test data
│   ├── create_simple_dummy_data.py # Create basic test data
│   ├── create_dummy_employees.py  # Create employee test data
│   ├── create_test_tasks.py       # Create task test data
│   ├── create_test_user_ankurP.py # Create specific test user
│   ├── add_more_clients.py        # Add additional client data
│   ├── update_ankur_email.py      # Update user email
│   └── update_ankur_name.py       # Update user name
├── 📁 setup/                      # Installation and setup scripts
│   └── setup_groq.sh             # Groq API setup script
└── 📁 testing/                    # Testing and validation scripts
    ├── simple_test.py             # Basic functionality test
    ├── test_groq_setup.py         # Groq API connection test
    └── test_pdf_llm.py            # PDF generation with LLM test
```

## 📚 Documentation Directory (`/docs/`)

```
docs/
├── 📁 guides/                     # Setup and deployment guides
│   ├── DEPLOYMENT_GUIDE.md        # General deployment guide
│   ├── LAUNCH_GUIDE.md           # Quick launch guide
│   ├── railway-deploy.md          # Railway deployment
│   ├── render-deploy.md           # Render deployment
│   └── vercel-deploy.md           # Vercel deployment
├── 📁 api/                        # API documentation
├── COMPREHENSIVE_CONTENT_ENGINE.md # Content engine documentation
├── CONTENT_ENGINE_SETUP.md       # Content engine setup
├── GROQ_SETUP.md                 # Groq AI setup guide
└── PRE_DEPLOYMENT_CHECKLIST.md   # Deployment checklist
```

## ⚙️ Configuration Directory (`/configs/`)

```
configs/
├── docker-compose.yml            # Docker Compose configuration
├── railway.json                  # Railway deployment config
└── [other config files]          # Additional configuration files
```

## 🚀 Deployment Directory (`/deployment/`)

```
deployment/
├── 📁 railway/                    # Railway platform deployment
│   ├── frontend/
│   └── backend/
└── 📁 [other platforms]/         # Other deployment configurations
```

## 🔑 Key Features by Directory

### Backend Services (`/backend/app/services/`)
- **`trending_service.py`**: 15-source content intelligence engine
  - Reddit, HackerNews, Twitter, Instagram, TikTok, GitHub, ProductHunt
  - Medium, DEV.to, YouTube, LinkedIn, StackOverflow, Quora, Pinterest, News
- **`pdf_report_service.py`**: Tushle AI branded PDF report generation
- **`llm_service.py`**: Groq LLM integration for authentic recommendations

### Frontend Pages (`/frontend/src/pages/`)
- **`ContentEngine.tsx`**: Main content discovery and PDF generation
- **`Dashboard.tsx`**: Analytics and performance dashboard
- **`Clients.tsx`**: Client relationship management
- **`Tasks.tsx`**: Task and automation management
- **`Finance.tsx`**: Invoicing and payment tracking

### API Routes (`/backend/app/api/v1/routes/`)
- **`content.py`**: Content intelligence and PDF generation endpoints
- **`clients.py`**: Client management APIs
- **`tasks.py`**: Task automation APIs
- **`auth.py`**: Authentication and authorization
- **`dashboard.py`**: Analytics and reporting APIs

## 🛠️ Development Workflow

1. **Backend Development**: Work in `/backend/app/`
2. **Frontend Development**: Work in `/frontend/src/`
3. **Database Scripts**: Use scripts in `/scripts/database/`
4. **Testing**: Run scripts from `/scripts/testing/`
5. **Documentation**: Update files in `/docs/`
6. **Deployment**: Use configurations in `/configs/` and `/deployment/`

## 📋 Quick Start Commands

```bash
# Backend setup
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Frontend setup
cd frontend && npm run dev

# Database setup
python scripts/database/create_simple_dummy_data.py

# Run tests
python scripts/testing/test_pdf_llm.py
```

## 🎯 Project Highlights

- **15 Content Sources**: Comprehensive market intelligence
- **Tushle AI Branding**: Professional PDF reports with LLM recommendations
- **Full-Stack Architecture**: FastAPI + React + TypeScript
- **Real-Time Data**: Daily-refreshed trending topics
- **Download Functionality**: Actual PDF file downloads
- **Authentication**: JWT-based with role management
- **Scalable Structure**: Modular, maintainable codebase

## 🚀 Deployment Ready

### Vercel Deployment Configuration ✅
- `vercel.json` - Complete Vercel configuration
- `api/index.py` - Serverless backend handler
- `requirements.txt` - Optimized Python dependencies
- `frontend/.env.production` - Production environment setup
- `scripts/setup/deploy-vercel.sh` - Automated deployment script

### Quick Deploy Commands
```bash
# Prepare for deployment
./scripts/setup/deploy-vercel.sh

# Deploy to Vercel (after pushing to GitHub)
# 1. Connect repository to Vercel
# 2. Set environment variables
# 3. Deploy automatically
```

### Environment Variables Required
- `GROQ_API_KEY` - Your Groq AI API key
- `SECRET_KEY` - JWT secret key (32+ characters)
- `DATABASE_URL` - Database connection string

---

*This structure provides clear separation of concerns, easy maintenance, and scalable development for the Tushle AI Automation Dashboard.*
