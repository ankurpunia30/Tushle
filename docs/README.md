# 🚀 Tushle AI Automation Dashboard

A comprehensive full-stack automation dashboard featuring advanced content intelligence, AI-powered insights, and business process automation.

## 🎯 Project Overview

This project provides a complete business automation platform with:
- **15-Source Content Intelligence Engine**: Real-time trending topics from major platforms
- **Tushle AI PDF Reports**: Professional market intelligence reports with LLM-generated recommendations
- **Business Process Automation**: Client management, invoicing, task automation
- **Modern Full-Stack Architecture**: FastAPI backend + React TypeScript frontend

## 🏗️ Project Structure

```
lehar/
├── 📁 backend/          # FastAPI application with 15-source content engine
├── 📁 frontend/         # React TypeScript UI with PDF generation
├── 📁 scripts/          # Database, setup, and testing scripts
├── 📁 docs/             # Documentation and deployment guides
├── 📁 configs/          # Configuration files (Docker, Railway, etc.)
├── 📁 deployment/       # Platform-specific deployment configs
└── 📄 PROJECT_STRUCTURE.md  # Detailed structure documentation
```

For detailed structure information, see [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md)

## ✨ Key Features

### 🧠 Content Intelligence Engine
- **15 Real Data Sources**: Reddit, HackerNews, Twitter, Instagram, TikTok, GitHub, ProductHunt, Medium, DEV.to, YouTube, LinkedIn, StackOverflow, Quora, Pinterest, News
- **Field-Specific Content**: Technology, Fashion, Marketing, Finance, Health, and more
- **Business Intelligence**: Revenue opportunity analysis, monetization strategies
- **Daily Variation**: Fresh content with cryptographic seeds for uniqueness

### 📊 Tushle AI Reports
- **Professional PDF Generation**: Branded reports with comprehensive analytics
- **LLM-Enhanced Recommendations**: Authentic insights based on real trending data
- **Download Functionality**: Complete PDF download system
- **Business Metrics**: Popularity scores, revenue estimates, competitive analysis

### 🏗️ Backend (FastAPI)
- **Modular Architecture**: Organized by business domains (finance, clients, content, etc.)
- **Task Scheduling**: Celery + Redis for background job processing
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based auth with role-based access control
- **AI Integration**: Local LLMs via Ollama for script generation
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

### 🎨 Frontend (React + TypeScript)
- **Modern UI**: TailwindCSS + shadcn/ui components
- **Responsive Design**: Mobile-first approach
- **State Management**: TanStack Query for server state
- **Animations**: Framer Motion for smooth transitions
- **Type Safety**: Full TypeScript coverage

### 🤖 Automation Pipelines

1. **Automatic Invoicing & Payments**
   - Generate and send invoices automatically
   - Payment tracking and reminders
   - Integration with payment processors

2. **Client Onboarding Workflow**
   - Automated onboarding sequences
   - Status tracking and progress monitoring
   - Welcome emails and document collection

3. **Follow-Up & Lead Nurture**
   - Automated lead scoring and follow-up
   - Email sequences based on lead behavior
   - CRM integration and pipeline management

4. **Daily Deliverables & Task Automation**
   - Recurring task automation
   - Progress tracking and reporting
   - Team collaboration features

5. **AI Topic Research Agent**
   - Trending topic discovery
   - Content idea generation
   - Market research automation

6. **AI Script Generator**
   - Video script generation using LLMs
   - Multiple style and tone options
   - Hook generation and optimization

7. **AI Avatar Video Creation**
   - Text-to-speech conversion
   - Lip-sync video generation
   - Multiple avatar options

8. **Auto Posting & Optimization Agent**
   - Multi-platform content posting
   - Optimal timing analysis
   - Engagement tracking and optimization

9. **AI Client Report Generator**
   - Automated report generation
   - Data visualization
   - PDF export and email delivery

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL
- Redis
- Ollama (for AI features)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Task Workers

```bash
# In backend directory
celery -A app.celery_app worker --loglevel=info

# For periodic tasks
celery -A app.celery_app beat --loglevel=info
```

## Project Structure

```
/
├── backend/
│   ├── app/
│   │   ├── api/v1/routes/      # API endpoints
│   │   ├── core/               # Security, config
│   │   ├── db/                 # Database setup
│   │   ├── models/             # SQLAlchemy models
│   │   ├── tasks/              # Celery tasks
│   │   └── main.py             # FastAPI app
│   ├── alembic/                # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Route components
│   │   ├── contexts/           # React contexts
│   │   ├── lib/                # Utilities and API
│   │   └── types/              # TypeScript types
│   ├── public/
│   └── package.json
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### AI Services
- `POST /api/v1/ai/generate-script` - Generate AI script
- `GET /api/v1/ai/scripts` - List generated scripts
- `DELETE /api/v1/ai/scripts/{id}` - Delete script

### Dashboard
- `GET /api/v1/dashboard/stats` - Get dashboard statistics

### Clients
- `GET /api/v1/clients` - List clients
- `POST /api/v1/clients` - Create client
- `GET /api/v1/clients/{id}` - Get client details

## Key Technologies

### Backend
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Celery**: Distributed task queue
- **Redis**: In-memory data store for caching and queues
- **Pydantic**: Data validation using Python type annotations
- **Jose**: JSON Web Signature implementation
- **Passlib**: Password hashing library

### Frontend
- **React 18**: UI library with hooks and concurrent features
- **TypeScript**: Static type checking
- **Vite**: Fast build tool and development server
- **TailwindCSS**: Utility-first CSS framework
- **shadcn/ui**: Beautiful, accessible component library
- **TanStack Query**: Data fetching and state management
- **React Router**: Client-side routing
- **Framer Motion**: Animation library
- **Axios**: HTTP client for API calls

## Deployment

### Backend Deployment
```bash
# Production requirements
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Serve static files with nginx or CDN
```

### Docker Support
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Environment Variables

See `.env.example` for all required environment variables including:
- Database connection
- Redis configuration
- API keys for external services
- Email settings
- Security keys

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API docs at `/docs` when running the backend

## Roadmap

- [ ] Payment processor integration (Stripe, PayPal)
- [ ] Advanced AI features (GPT-4, Claude integration)
- [ ] Mobile app (React Native)
- [ ] Advanced analytics and reporting
- [ ] Team collaboration features
- [ ] Webhook system for external integrations
- [ ] Multi-tenant support
- [ ] Advanced role-based permissions
