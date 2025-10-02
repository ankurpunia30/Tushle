<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Automation Dashboard Project

This is a full-stack automation dashboard built with FastAPI (backend) and React (frontend).

## Project Structure
- `backend/`: FastAPI application with SQLAlchemy, Celery, and Redis
- `frontend/`: React + TypeScript application with TailwindCSS and shadcn/ui

## Key Architectural Patterns
- **Backend**: Modular architecture with separate routes for each business domain
- **Database**: SQLAlchemy models with proper relationships
- **Authentication**: JWT-based auth with role-based access control
- **Tasks**: Celery for background job processing
- **Frontend**: Component-based architecture with TypeScript

## Code Style Guidelines
- Use TypeScript for all frontend code
- Follow REST API conventions for backend endpoints
- Use Pydantic models for request/response validation
- Implement proper error handling and logging
- Use async/await patterns for asynchronous operations

## Key Features
- AI-powered script generation using Ollama
- Automated task scheduling and execution
- Multi-platform content posting automation
- Client relationship management
- Invoicing and payment tracking
- Lead nurturing workflows
- Dashboard analytics and reporting

## Development Workflow
- Use proper type annotations in Python
- Implement proper error boundaries in React
- Follow component composition patterns
- Use React Query for server state management
- Implement proper loading and error states
- Use Framer Motion for animations

## API Integration
- All API calls should use the centralized axios instance
- Implement proper authentication headers
- Handle token refresh and expiration
- Use proper error handling for API failures

## Database Patterns
- Use SQLAlchemy relationships properly
- Implement proper migrations with Alembic
- Use database sessions correctly with proper cleanup
- Follow naming conventions for tables and columns

## UI/UX Guidelines
- Use shadcn/ui components consistently
- Follow TailwindCSS utility patterns
- Implement responsive design principles
- Use proper color schemes and spacing
- Implement smooth animations and transitions
