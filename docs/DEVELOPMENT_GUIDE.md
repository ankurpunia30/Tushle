# 🛠️ Development Guide - Tushle AI Automation Dashboard

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Clone and setup the project
git clone <repository-url>
cd lehar
./setup.sh
```

### 2. Development Workflow
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 3. Access Points
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:5173/dashboard

## 📁 Working with the New Structure

### Backend Development (`/backend/`)

#### Adding New Services
```python
# Create new service in /backend/app/services/
# Example: /backend/app/services/new_service.py

class NewService:
    def __init__(self):
        pass
    
    async def new_method(self):
        return "Hello from new service"

# Export instance
new_service = NewService()
```

#### Adding New API Routes
```python
# Create new route in /backend/app/api/v1/routes/
# Example: /backend/app/api/v1/routes/new_route.py

from fastapi import APIRouter
router = APIRouter()

@router.get("/new-endpoint")
async def new_endpoint():
    return {"message": "New endpoint"}
```

#### Database Scripts
```bash
# Use scripts in /scripts/database/
python scripts/database/create_dummy_clients.py    # Add test clients
python scripts/database/create_test_tasks.py       # Add test tasks
python scripts/database/update_ankur_email.py      # Update user data
```

### Frontend Development (`/frontend/`)

#### Adding New Pages
```typescript
// Create new page in /frontend/src/pages/
// Example: /frontend/src/pages/NewPage.tsx

import React from 'react';

const NewPage: React.FC = () => {
  return (
    <div>
      <h1>New Page</h1>
    </div>
  );
};

export default NewPage;
```

#### Adding New Components
```typescript
// Create reusable components in /frontend/src/components/
// Example: /frontend/src/components/NewComponent.tsx

interface NewComponentProps {
  title: string;
}

export const NewComponent: React.FC<NewComponentProps> = ({ title }) => {
  return <div className="new-component">{title}</div>;
};
```

## 🧪 Testing Workflow

### Backend Testing
```bash
# Test individual services
python scripts/testing/test_groq_setup.py          # Test Groq AI integration
python scripts/testing/test_pdf_llm.py             # Test PDF + LLM generation
python scripts/testing/simple_test.py              # Basic functionality test

# Test specific endpoints
curl http://localhost:8000/api/v1/content/discover-topics \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"field": "fashion", "content_type": "social_media"}'
```

### Frontend Testing
```bash
cd frontend
npm run build      # Test build process
npm run preview    # Test production build
npm run lint       # Check code quality
```

## 📊 Content Engine Development

### Adding New Content Sources
```python
# In /backend/app/services/trending_service.py

async def get_new_source_trending(self, field: str) -> List[Dict[str, Any]]:
    """Add new content source integration"""
    try:
        # Your source-specific logic here
        return []
    except Exception as e:
        logger.error(f"Error fetching from new source: {e}")
        return []

# Add to aggregate_trending_topics method
if 'new_source' in daily_sources:
    new_trends = await self.get_new_source_trending(field)
    # Process and add to all_topics
```

### Customizing PDF Reports
```python
# In /backend/app/services/pdf_report_service.py

# Modify generate_comprehensive_report method
# Add new sections, change styling, customize content

# Example: Add new section
story.append(Paragraph("NEW SECTION", self.styles['CustomTitle']))
# Add your custom content here
```

### Enhancing LLM Integration
```python
# In /backend/app/services/llm_service.py

async def new_llm_method(self, data: Dict) -> str:
    """Add new LLM-powered functionality"""
    try:
        # Your LLM integration logic
        return "LLM response"
    except Exception as e:
        return "Fallback response"
```

## 🔧 Configuration Management

### Environment Variables
```bash
# Backend configuration (/backend/.env)
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=sqlite:///./data/automation_dashboard.db
SECRET_KEY=your_secret_key

# Frontend configuration (/frontend/.env.local)
VITE_API_URL=http://localhost:8000
```

### Docker Development
```bash
# Build and run with Docker Compose
docker-compose -f configs/docker-compose.yml up --build

# Individual containers
docker build -t lehar-backend ./backend
docker build -t lehar-frontend ./frontend
```

## 📚 Documentation Workflow

### Adding New Documentation
```bash
# API documentation - automatically generated
# Update docstrings in your route functions

# User guides
echo "# New Guide" > docs/guides/new-guide.md

# Update PROJECT_STRUCTURE.md when adding new directories
```

### API Documentation
- Automatic generation via FastAPI
- Access at http://localhost:8000/docs
- Update docstrings in route functions for better docs

## 🚀 Deployment Workflow

### Platform Configurations
```bash
# Railway deployment
deployment/railway/

# Other platforms
configs/railway.json
configs/docker-compose.yml
```

### Environment Setup for Production
```bash
# Use production environment files
backend/.env.production
frontend/.env.production
```

## 🔍 Debugging and Troubleshooting

### Common Issues

1. **Backend won't start**
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Frontend build fails**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Database issues**
   ```bash
   python scripts/database/create_simple_dummy_data.py
   ```

4. **Groq API issues**
   ```bash
   python scripts/testing/test_groq_setup.py
   ```

### Logging
- Backend logs: Console output from uvicorn
- Frontend logs: Browser console
- Script logs: Terminal output

## 📈 Performance Optimization

### Backend
- Use async/await for I/O operations
- Implement proper caching for trending data
- Optimize database queries

### Frontend
- Lazy load components
- Optimize bundle size
- Use React Query for efficient data fetching

## 🤝 Contributing Guidelines

1. **Follow the folder structure**
2. **Add tests for new features**
3. **Update documentation**
4. **Use TypeScript for frontend**
5. **Follow Python PEP 8 for backend**
6. **Test thoroughly before committing**

---

*This guide helps you efficiently work with the organized Tushle AI project structure.*
