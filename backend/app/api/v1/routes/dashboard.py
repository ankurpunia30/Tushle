from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import User, Client, Invoice, Task, Lead
from app.core.security import get_current_active_user

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    
    # Count various entities
    total_clients = db.query(Client).filter(Client.owner_id == current_user.id).count()
    active_clients = db.query(Client).filter(
        Client.owner_id == current_user.id,
        Client.status == "active"
    ).count()
    
    pending_tasks = db.query(Task).filter(
        Task.assigned_to_id == current_user.id,
        Task.status.in_(["todo", "in_progress"])  # Use valid statuses
    ).count()
    
    new_leads = db.query(Lead).filter(
        Lead.assigned_to_id == current_user.id,
        Lead.status == "new"
    ).count()
    
    return {
        "total_clients": total_clients,
        "active_clients": active_clients,
        "pending_tasks": pending_tasks,
        "new_leads": new_leads,
        "revenue_this_month": 0,  # Calculate based on invoices
        "content_posts_scheduled": 0  # Calculate based on content posts
    }
