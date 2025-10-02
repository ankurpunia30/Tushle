from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
from datetime import datetime, timedelta
from typing import Dict, List, Any

from app.db.database import get_db
from app.core.security import get_current_active_user
from app.models import User, Task, Client

router = APIRouter()

@router.get("/employee/{employee_id}/tasks")
async def get_employee_task_analytics(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive task analytics for an employee"""
    
    # Check if user can access this data (admin or self)
    if current_user.role != "admin" and current_user.id != employee_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this data")
    
    # Get employee
    employee = db.query(User).filter(User.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Basic task counts
    total_tasks = db.query(Task).filter(Task.assigned_to_id == employee_id).count()
    completed_tasks = db.query(Task).filter(
        Task.assigned_to_id == employee_id,
        Task.status == "completed"
    ).count()
    in_progress_tasks = db.query(Task).filter(
        Task.assigned_to_id == employee_id,
        Task.status == "in_progress"
    ).count()
    
    # Overdue tasks
    overdue_tasks = db.query(Task).filter(
        Task.assigned_to_id == employee_id,
        Task.due_date < datetime.now(),
        Task.status.in_(["todo", "in_progress"])
    ).count()
    
    # Total hours logged
    total_hours_result = db.query(func.sum(Task.actual_hours)).filter(
        Task.assigned_to_id == employee_id,
        Task.actual_hours.isnot(None)
    ).scalar()
    total_hours_logged = float(total_hours_result) if total_hours_result else 0.0
    
    # Average completion time (for completed tasks)
    avg_completion_result = db.query(func.avg(Task.actual_hours)).filter(
        Task.assigned_to_id == employee_id,
        Task.status == "completed",
        Task.actual_hours.isnot(None)
    ).scalar()
    avg_completion_time = float(avg_completion_result) if avg_completion_result else 0.0
    
    # Productivity score (completed tasks / total tasks * 100)
    productivity_score = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Tasks by month (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    tasks_by_month = []
    for i in range(6):
        month_start = datetime.now() - timedelta(days=30 * i)
        month_end = month_start - timedelta(days=30)
        
        count = db.query(Task).filter(
            Task.assigned_to_id == employee_id,
            Task.created_at >= month_end,
            Task.created_at < month_start
        ).count()
        
        tasks_by_month.append({
            "month": month_start.strftime("%b %Y"),
            "count": count
        })
    
    # Tasks by priority
    tasks_by_priority = db.query(
        Task.priority,
        func.count(Task.id).label('count')
    ).filter(
        Task.assigned_to_id == employee_id
    ).group_by(Task.priority).all()
    
    priority_data = [{"priority": p[0], "count": p[1]} for p in tasks_by_priority]
    
    # Recent tasks (last 10)
    recent_tasks = db.query(Task).filter(
        Task.assigned_to_id == employee_id
    ).order_by(Task.created_at.desc()).limit(10).all()
    
    recent_tasks_data = []
    for task in recent_tasks:
        recent_tasks_data.append({
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "priority": task.priority,
            "type": task.type,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat()
        })
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "overdue_tasks": overdue_tasks,
        "total_hours_logged": round(total_hours_logged, 1),
        "avg_completion_time": round(avg_completion_time, 1),
        "productivity_score": round(productivity_score, 1),
        "tasks_by_month": list(reversed(tasks_by_month)),
        "tasks_by_priority": priority_data,
        "recent_tasks": recent_tasks_data
    }

@router.get("/employee/{employee_id}/finance")
async def get_employee_finance_analytics(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get financial analytics for an employee"""
    
    # Check if user can access this data (admin only for finance)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get employee
    employee = db.query(User).filter(User.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Mock hourly rate (in a real system, this would be in the user profile)
    hourly_rate = 75.0  # Default hourly rate
    
    # Get billable hours (completed tasks actual hours)
    billable_hours_result = db.query(func.sum(Task.actual_hours)).filter(
        Task.assigned_to_id == employee_id,
        Task.status == "completed",
        Task.actual_hours.isnot(None)
    ).scalar()
    billable_hours = float(billable_hours_result) if billable_hours_result else 0.0
    
    # Calculate total revenue
    total_revenue_generated = billable_hours * hourly_rate
    
    # Monthly earnings (last 6 months)
    monthly_earnings = []
    for i in range(6):
        month_start = datetime.now() - timedelta(days=30 * i)
        month_end = month_start - timedelta(days=30)
        
        month_hours_result = db.query(func.sum(Task.actual_hours)).filter(
            Task.assigned_to_id == employee_id,
            Task.status == "completed",
            Task.actual_hours.isnot(None),
            Task.updated_at >= month_end,
            Task.updated_at < month_start
        ).scalar()
        
        month_hours = float(month_hours_result) if month_hours_result else 0.0
        monthly_earnings.append({
            "month": month_start.strftime("%b %Y"),
            "amount": round(month_hours * hourly_rate, 2)
        })
    
    # Project earnings (group by client)
    project_earnings = db.query(
        Client.name,
        func.sum(Task.actual_hours).label('total_hours')
    ).join(
        Task, Task.client_id == Client.id
    ).filter(
        Task.assigned_to_id == employee_id,
        Task.status == "completed",
        Task.actual_hours.isnot(None)
    ).group_by(Client.name).all()
    
    project_earnings_data = []
    for client_name, hours in project_earnings:
        if hours:
            project_earnings_data.append({
                "project": client_name,
                "amount": round(float(hours) * hourly_rate, 2)
            })
    
    # Efficiency rating (based on task completion rate and time management)
    completed_on_time = db.query(Task).filter(
        Task.assigned_to_id == employee_id,
        Task.status == "completed",
        Task.actual_hours <= Task.estimated_hours
    ).count() if db.query(Task).filter(Task.assigned_to_id == employee_id, Task.status == "completed").count() > 0 else 0
    
    total_completed = db.query(Task).filter(
        Task.assigned_to_id == employee_id,
        Task.status == "completed"
    ).count()
    
    efficiency_rating = 5.0
    if total_completed > 0:
        on_time_rate = completed_on_time / total_completed
        efficiency_rating = min(5.0, 3.0 + (on_time_rate * 2.0))  # Scale to 3-5 range
    
    return {
        "total_revenue_generated": round(total_revenue_generated, 2),
        "billable_hours": round(billable_hours, 1),
        "hourly_rate": hourly_rate,
        "monthly_earnings": list(reversed(monthly_earnings)),
        "project_earnings": project_earnings_data,
        "efficiency_rating": round(efficiency_rating, 1)
    }

@router.get("/employee/{employee_id}/projects")
async def get_employee_project_analytics(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get project analytics for an employee"""
    
    # Check if user can access this data (admin or self)
    if current_user.role != "admin" and current_user.id != employee_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this data")
    
    # Get employee
    employee = db.query(User).filter(User.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Group tasks by client to simulate projects
    client_projects = db.query(
        Client.id,
        Client.name,
        func.count(Task.id).label('task_count'),
        func.sum(case((Task.status == 'completed', 1), else_=0)).label('completed_tasks'),
        func.sum(Task.estimated_hours).label('total_estimated_hours'),
        func.sum(Task.actual_hours).label('total_actual_hours')
    ).join(
        Task, Task.client_id == Client.id
    ).filter(
        Task.assigned_to_id == employee_id
    ).group_by(Client.id, Client.name).all()
    
    projects = []
    total_projects = len(client_projects)
    completed_projects = 0
    active_projects = 0
    
    for project in client_projects:
        client_id, client_name, task_count, completed_task_count, est_hours, actual_hours = project
        
        # Calculate progress
        progress = (completed_task_count / task_count * 100) if task_count > 0 else 0
        
        # Determine status
        if progress == 100:
            status = "completed"
            completed_projects += 1
        elif progress > 0:
            status = "in_progress"
            active_projects += 1
        else:
            status = "not_started"
        
        if progress > 0:
            active_projects += 1
        
        # Mock project data
        projects.append({
            "id": client_id,
            "name": f"{client_name} Project",
            "status": status,
            "progress": round(progress, 1),
            "client": client_name,
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat() if status != "completed" else datetime.now().isoformat(),
            "budget": round(float(est_hours or 0) * 75, 2)  # Mock budget calculation
        })
    
    # Project success rate
    project_success_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
    
    return {
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "total_projects": total_projects,
        "project_success_rate": round(project_success_rate, 1),
        "projects": projects
    }

@router.get("/employee/{employee_id}/leads")
async def get_employee_lead_analytics(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get lead generation analytics for an employee"""
    
    # Check if user can access this data (admin or self)
    if current_user.role != "admin" and current_user.id != employee_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this data")
    
    # Get employee
    employee = db.query(User).filter(User.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Mock lead data based on client interactions and tasks
    # In a real system, you'd have a leads table
    
    # Count clients that this employee has worked with (simulate leads generated)
    client_interactions = db.query(Client.id).join(
        Task, Task.client_id == Client.id
    ).filter(
        Task.assigned_to_id == employee_id
    ).distinct().count()
    
    leads_generated = client_interactions * 2  # Mock multiplier
    
    # Count completed client projects (simulate conversions)
    completed_client_projects = db.query(Client.id).join(
        Task, Task.client_id == Client.id
    ).filter(
        Task.assigned_to_id == employee_id,
        Task.status == "completed"
    ).distinct().count()
    
    leads_converted = completed_client_projects
    
    # Conversion rate
    conversion_rate = (leads_converted / leads_generated * 100) if leads_generated > 0 else 0
    
    # Monthly leads (last 6 months)
    monthly_leads = []
    for i in range(6):
        month_start = datetime.now() - timedelta(days=30 * i)
        month_end = month_start - timedelta(days=30)
        
        # Mock monthly data
        month_leads = max(0, leads_generated // 6 + (i % 3))  # Distribute across months
        month_converted = max(0, month_leads // 2)
        
        monthly_leads.append({
            "month": month_start.strftime("%b %Y"),
            "leads": month_leads,
            "converted": month_converted
        })
    
    # Lead sources (mock data)
    lead_sources = [
        {"source": "referral", "count": leads_generated // 3},
        {"source": "website", "count": leads_generated // 4},
        {"source": "social_media", "count": leads_generated // 5},
        {"source": "email", "count": leads_generated - (leads_generated // 3 + leads_generated // 4 + leads_generated // 5)}
    ]
    
    # Average lead value (mock calculation)
    total_revenue = db.query(func.sum(Task.actual_hours)).filter(
        Task.assigned_to_id == employee_id,
        Task.status == "completed",
        Task.actual_hours.isnot(None)
    ).scalar()
    
    avg_lead_value = 0
    if total_revenue and leads_converted > 0:
        avg_lead_value = (float(total_revenue) * 75) / leads_converted  # Mock calculation
    
    return {
        "leads_generated": leads_generated,
        "leads_converted": leads_converted,
        "conversion_rate": round(conversion_rate, 1),
        "monthly_leads": list(reversed(monthly_leads)),
        "lead_sources": lead_sources,
        "avg_lead_value": round(avg_lead_value, 2)
    }
