from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.db.database import get_db
from app.models import EmployeePerformance, User, Task, Lead, Meeting, Client
from app.core.security import get_current_active_user

router = APIRouter()


class EmployeePerformanceResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    period_start: datetime
    period_end: datetime
    
    # Task Performance
    total_tasks_assigned: int
    tasks_completed: int
    tasks_overdue: int
    task_completion_rate: float
    avg_task_completion_time: Optional[float]
    time_efficiency: Optional[float]  # actual_hours / estimated_hours
    
    # Lead Performance
    leads_assigned: int
    leads_contacted: int
    leads_qualified: int
    leads_converted: int
    lead_conversion_rate: float
    total_estimated_deal_value: Optional[float]
    total_actual_deal_value: Optional[float]
    
    # Meeting Performance
    meetings_scheduled: int
    meetings_completed: int
    meetings_no_show: int
    meeting_completion_rate: float
    
    # Client Management
    clients_managed: int
    client_satisfaction_score: Optional[float]
    
    # Overall Performance
    performance_score: Optional[float]
    rating: Optional[str]
    
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EmployeeStatsResponse(BaseModel):
    employee_id: int
    employee_name: str
    current_period_performance: Optional[EmployeePerformanceResponse]
    
    # Real-time stats
    active_tasks: int
    pending_meetings: int
    recent_activity_score: float
    
    # Trends
    performance_trend: str  # improving, declining, stable
    last_30_days_score: Optional[float]
    
    class Config:
        from_attributes = True


class TeamPerformanceOverview(BaseModel):
    total_employees: int
    avg_performance_score: float
    top_performer: Optional[str]
    employees_needing_attention: List[str]
    team_task_completion_rate: float
    team_lead_conversion_rate: float
    total_revenue_generated: float


def check_admin_role(current_user: User):
    """Check if current user is admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can access performance data"
        )


def calculate_performance_metrics(employee_id: int, start_date: datetime, end_date: datetime, db: Session):
    """Calculate performance metrics for an employee"""
    
    # Task Performance
    tasks_assigned = db.query(Task).filter(
        Task.assigned_to_id == employee_id,
        Task.created_at >= start_date,
        Task.created_at <= end_date
    ).count()
    
    tasks_completed = db.query(Task).filter(
        Task.assigned_to_id == employee_id,
        Task.status == "completed",
        Task.created_at >= start_date,
        Task.created_at <= end_date
    ).count()
    
    tasks_overdue = db.query(Task).filter(
        Task.assigned_to_id == employee_id,
        Task.due_date < datetime.now(),
        Task.status.in_(["todo", "in_progress", "review", "blocked"]),
        Task.created_at >= start_date,
        Task.created_at <= end_date
    ).count()
    
    # Average completion time
    completed_tasks = db.query(Task).filter(
        Task.assigned_to_id == employee_id,
        Task.status == "completed",
        Task.actual_hours.isnot(None),
        Task.created_at >= start_date,
        Task.created_at <= end_date
    ).all()
    
    avg_completion_time = None
    time_efficiency = None
    
    if completed_tasks:
        total_actual_hours = sum([task.actual_hours for task in completed_tasks if task.actual_hours])
        avg_completion_time = total_actual_hours / len(completed_tasks) if completed_tasks else 0
        
        # Time efficiency (actual vs estimated)
        estimated_hours = sum([task.estimated_hours for task in completed_tasks if task.estimated_hours])
        if estimated_hours > 0:
            time_efficiency = float(total_actual_hours / estimated_hours)
    
    # Lead Performance
    leads_assigned = db.query(Lead).filter(
        Lead.assigned_to_id == employee_id,
        Lead.created_at >= start_date,
        Lead.created_at <= end_date
    ).count()
    
    leads_contacted = db.query(Lead).filter(
        Lead.assigned_to_id == employee_id,
        Lead.status.in_(["contacted", "qualified", "proposal", "closed_won", "closed_lost"]),
        Lead.created_at >= start_date,
        Lead.created_at <= end_date
    ).count()
    
    leads_qualified = db.query(Lead).filter(
        Lead.assigned_to_id == employee_id,
        Lead.status.in_(["qualified", "proposal", "closed_won"]),
        Lead.created_at >= start_date,
        Lead.created_at <= end_date
    ).count()
    
    leads_converted = db.query(Lead).filter(
        Lead.assigned_to_id == employee_id,
        Lead.status == "closed_won",
        Lead.created_at >= start_date,
        Lead.created_at <= end_date
    ).count()
    
    # Deal values
    lead_values = db.query(Lead).filter(
        Lead.assigned_to_id == employee_id,
        Lead.estimated_value.isnot(None),
        Lead.created_at >= start_date,
        Lead.created_at <= end_date
    ).all()
    
    total_estimated_value = sum([lead.estimated_value for lead in lead_values if lead.estimated_value])
    
    converted_leads = db.query(Lead).filter(
        Lead.assigned_to_id == employee_id,
        Lead.status == "closed_won",
        Lead.estimated_value.isnot(None),
        Lead.created_at >= start_date,
        Lead.created_at <= end_date
    ).all()
    
    total_actual_value = sum([lead.estimated_value for lead in converted_leads if lead.estimated_value])
    
    # Meeting Performance
    meetings_scheduled = db.query(Meeting).filter(
        Meeting.assigned_to_id == employee_id,
        Meeting.created_at >= start_date,
        Meeting.created_at <= end_date
    ).count()
    
    meetings_completed = db.query(Meeting).filter(
        Meeting.assigned_to_id == employee_id,
        Meeting.status == "completed",
        Meeting.created_at >= start_date,
        Meeting.created_at <= end_date
    ).count()
    
    meetings_no_show = db.query(Meeting).filter(
        Meeting.assigned_to_id == employee_id,
        Meeting.status == "cancelled",
        Meeting.created_at >= start_date,
        Meeting.created_at <= end_date
    ).count()
    
    # Client Management
    clients_managed = db.query(Client).filter(
        Client.owner_id == employee_id,
        Client.created_at >= start_date,
        Client.created_at <= end_date
    ).count()
    
    # Calculate performance score (0-100)
    performance_score = 0.0
    
    # Task completion rate (30% weight)
    task_completion_rate = (tasks_completed / tasks_assigned * 100) if tasks_assigned > 0 else 0
    performance_score += task_completion_rate * 0.3
    
    # Lead conversion rate (25% weight)
    lead_conversion_rate = (leads_converted / leads_assigned * 100) if leads_assigned > 0 else 0
    performance_score += lead_conversion_rate * 0.25
    
    # Meeting completion rate (20% weight)
    meeting_completion_rate = (meetings_completed / meetings_scheduled * 100) if meetings_scheduled > 0 else 0
    performance_score += meeting_completion_rate * 0.2
    
    # Time efficiency (15% weight) - inverted (lower is better)
    if time_efficiency:
        efficiency_score = max(0, 100 - (time_efficiency - 1) * 50)  # 1.0 = 100%, >1.0 decreases score
        performance_score += efficiency_score * 0.15
    
    # Overdue penalty (10% weight)
    overdue_penalty = (tasks_overdue / max(tasks_assigned, 1)) * 100
    performance_score -= overdue_penalty * 0.1
    
    performance_score = max(0, min(100, performance_score))
    
    # Rating based on score
    if performance_score >= 90:
        rating = "excellent"
    elif performance_score >= 80:
        rating = "good"
    elif performance_score >= 70:
        rating = "satisfactory"
    elif performance_score >= 60:
        rating = "needs_improvement"
    else:
        rating = "poor"
    
    return {
        "total_tasks_assigned": tasks_assigned,
        "tasks_completed": tasks_completed,
        "tasks_overdue": tasks_overdue,
        "avg_task_completion_time": avg_completion_time,
        "total_estimated_hours": sum([task.estimated_hours for task in completed_tasks if task.estimated_hours]) if completed_tasks else 0,
        "total_actual_hours": sum([task.actual_hours for task in completed_tasks if task.actual_hours]) if completed_tasks else 0,
        "leads_assigned": leads_assigned,
        "leads_contacted": leads_contacted,
        "leads_qualified": leads_qualified,
        "leads_converted": leads_converted,
        "total_estimated_deal_value": total_estimated_value,
        "total_actual_deal_value": total_actual_value,
        "meetings_scheduled": meetings_scheduled,
        "meetings_completed": meetings_completed,
        "meetings_no_show": meetings_no_show,
        "clients_managed": clients_managed,
        "performance_score": performance_score,
        "rating": rating
    }


@router.get("/team-overview", response_model=TeamPerformanceOverview)
async def get_team_performance_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get overall team performance overview - Admin only"""
    check_admin_role(current_user)
    
    # Get all employees
    employees = db.query(User).filter(User.role == "employee", User.is_active == True).all()
    total_employees = len(employees)
    
    if total_employees == 0:
        return TeamPerformanceOverview(
            total_employees=0,
            avg_performance_score=0,
            top_performer=None,
            employees_needing_attention=[],
            team_task_completion_rate=0,
            team_lead_conversion_rate=0,
            total_revenue_generated=0
        )
    
    # Calculate current month metrics
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = datetime.now()
    
    employee_scores = []
    total_tasks_assigned = 0
    total_tasks_completed = 0
    total_leads_assigned = 0
    total_leads_converted = 0
    total_revenue = 0
    
    for employee in employees:
        metrics = calculate_performance_metrics(employee.id, start_of_month, end_of_month, db)
        employee_scores.append({
            "name": employee.full_name,
            "score": metrics["performance_score"],
            "employee": employee
        })
        
        total_tasks_assigned += metrics["total_tasks_assigned"]
        total_tasks_completed += metrics["tasks_completed"]
        total_leads_assigned += metrics["leads_assigned"]
        total_leads_converted += metrics["leads_converted"]
        total_revenue += metrics["total_actual_deal_value"] or 0
    
    # Calculate averages
    avg_performance_score = sum([emp["score"] for emp in employee_scores]) / total_employees
    team_task_completion_rate = (total_tasks_completed / total_tasks_assigned * 100) if total_tasks_assigned > 0 else 0
    team_lead_conversion_rate = (total_leads_converted / total_leads_assigned * 100) if total_leads_assigned > 0 else 0
    
    # Find top performer
    top_performer = max(employee_scores, key=lambda x: x["score"])["name"] if employee_scores else None
    
    # Find employees needing attention (score < 70)
    employees_needing_attention = [emp["name"] for emp in employee_scores if emp["score"] < 70]
    
    return TeamPerformanceOverview(
        total_employees=total_employees,
        avg_performance_score=avg_performance_score,
        top_performer=top_performer,
        employees_needing_attention=employees_needing_attention,
        team_task_completion_rate=team_task_completion_rate,
        team_lead_conversion_rate=team_lead_conversion_rate,
        total_revenue_generated=total_revenue
    )


@router.get("/employees", response_model=List[EmployeeStatsResponse])
async def get_all_employee_performance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get performance stats for all employees - Admin only"""
    check_admin_role(current_user)
    
    employees = db.query(User).filter(User.role == "employee", User.is_active == True).all()
    
    result = []
    for employee in employees:
        # Get current month performance
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = datetime.now()
        
        current_performance = db.query(EmployeePerformance).filter(
            EmployeePerformance.employee_id == employee.id,
            EmployeePerformance.period_start >= start_of_month,
            EmployeePerformance.period_end <= end_of_month
        ).first()
        
        # Real-time stats
        active_tasks = db.query(Task).filter(
            Task.assigned_to_id == employee.id,
            Task.status.in_(["todo", "in_progress", "review"])
        ).count()
        
        pending_meetings = db.query(Meeting).filter(
            Meeting.assigned_to_id == employee.id,
            Meeting.status == "scheduled",
            Meeting.start_time >= datetime.now()
        ).count()
        
        # Calculate recent activity score (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_metrics = calculate_performance_metrics(employee.id, week_ago, datetime.now(), db)
        recent_activity_score = recent_metrics["performance_score"]
        
        # Performance trend (compare last 30 days with previous 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        sixty_days_ago = datetime.now() - timedelta(days=60)
        
        last_30_metrics = calculate_performance_metrics(employee.id, thirty_days_ago, datetime.now(), db)
        previous_30_metrics = calculate_performance_metrics(employee.id, sixty_days_ago, thirty_days_ago, db)
        
        last_30_score = last_30_metrics["performance_score"]
        previous_30_score = previous_30_metrics["performance_score"]
        
        if last_30_score > previous_30_score + 5:
            trend = "improving"
        elif last_30_score < previous_30_score - 5:
            trend = "declining"
        else:
            trend = "stable"
        
        # Format current performance if exists
        current_perf_response = None
        if current_performance:
            current_perf_response = EmployeePerformanceResponse(
                id=current_performance.id,
                employee_id=current_performance.employee_id,
                employee_name=employee.full_name,
                period_start=current_performance.period_start,
                period_end=current_performance.period_end,
                total_tasks_assigned=current_performance.total_tasks_assigned,
                tasks_completed=current_performance.tasks_completed,
                tasks_overdue=current_performance.tasks_overdue,
                task_completion_rate=(current_performance.tasks_completed / max(current_performance.total_tasks_assigned, 1)) * 100,
                avg_task_completion_time=float(current_performance.avg_task_completion_time) if current_performance.avg_task_completion_time else None,
                time_efficiency=float(current_performance.total_actual_hours / max(current_performance.total_estimated_hours, 1)) if current_performance.total_estimated_hours else None,
                leads_assigned=current_performance.leads_assigned,
                leads_contacted=current_performance.leads_contacted,
                leads_qualified=current_performance.leads_qualified,
                leads_converted=current_performance.leads_converted,
                lead_conversion_rate=(current_performance.leads_converted / max(current_performance.leads_assigned, 1)) * 100,
                total_estimated_deal_value=float(current_performance.total_estimated_deal_value) if current_performance.total_estimated_deal_value else None,
                total_actual_deal_value=float(current_performance.total_actual_deal_value) if current_performance.total_actual_deal_value else None,
                meetings_scheduled=current_performance.meetings_scheduled,
                meetings_completed=current_performance.meetings_completed,
                meetings_no_show=current_performance.meetings_no_show,
                meeting_completion_rate=(current_performance.meetings_completed / max(current_performance.meetings_scheduled, 1)) * 100,
                clients_managed=current_performance.clients_managed,
                client_satisfaction_score=float(current_performance.client_satisfaction_score) if current_performance.client_satisfaction_score else None,
                performance_score=float(current_performance.performance_score) if current_performance.performance_score else None,
                rating=current_performance.rating,
                created_at=current_performance.created_at,
                updated_at=current_performance.updated_at
            )
        
        result.append(EmployeeStatsResponse(
            employee_id=employee.id,
            employee_name=employee.full_name,
            current_period_performance=current_perf_response,
            active_tasks=active_tasks,
            pending_meetings=pending_meetings,
            recent_activity_score=recent_activity_score,
            performance_trend=trend,
            last_30_days_score=last_30_score
        ))
    
    return result


@router.get("/employee/{employee_id}/performance", response_model=List[EmployeePerformanceResponse])
async def get_employee_performance_history(
    employee_id: int,
    months: int = Query(6, ge=1, le=24),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get performance history for a specific employee"""
    check_admin_role(current_user)
    
    # Verify employee exists
    employee = db.query(User).filter(User.id == employee_id, User.role == "employee").first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Get historical performance records
    performance_records = db.query(EmployeePerformance).filter(
        EmployeePerformance.employee_id == employee_id
    ).order_by(EmployeePerformance.period_start.desc()).limit(months).all()
    
    result = []
    for record in performance_records:
        result.append(EmployeePerformanceResponse(
            id=record.id,
            employee_id=record.employee_id,
            employee_name=employee.full_name,
            period_start=record.period_start,
            period_end=record.period_end,
            total_tasks_assigned=record.total_tasks_assigned,
            tasks_completed=record.tasks_completed,
            tasks_overdue=record.tasks_overdue,
            task_completion_rate=(record.tasks_completed / max(record.total_tasks_assigned, 1)) * 100,
            avg_task_completion_time=float(record.avg_task_completion_time) if record.avg_task_completion_time else None,
            time_efficiency=float(record.total_actual_hours / max(record.total_estimated_hours, 1)) if record.total_estimated_hours else None,
            leads_assigned=record.leads_assigned,
            leads_contacted=record.leads_contacted,
            leads_qualified=record.leads_qualified,
            leads_converted=record.leads_converted,
            lead_conversion_rate=(record.leads_converted / max(record.leads_assigned, 1)) * 100,
            total_estimated_deal_value=float(record.total_estimated_deal_value) if record.total_estimated_deal_value else None,
            total_actual_deal_value=float(record.total_actual_deal_value) if record.total_actual_deal_value else None,
            meetings_scheduled=record.meetings_scheduled,
            meetings_completed=record.meetings_completed,
            meetings_no_show=record.meetings_no_show,
            meeting_completion_rate=(record.meetings_completed / max(record.meetings_scheduled, 1)) * 100,
            clients_managed=record.clients_managed,
            client_satisfaction_score=float(record.client_satisfaction_score) if record.client_satisfaction_score else None,
            performance_score=float(record.performance_score) if record.performance_score else None,
            rating=record.rating,
            created_at=record.created_at,
            updated_at=record.updated_at
        ))
    
    return result


@router.post("/calculate-monthly-performance")
async def calculate_monthly_performance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calculate and store monthly performance for all employees - Admin only"""
    check_admin_role(current_user)
    
    # Get all active employees
    employees = db.query(User).filter(User.role == "employee", User.is_active == True).all()
    
    # Calculate for last month
    today = datetime.now()
    if today.month == 1:
        start_of_last_month = datetime(today.year - 1, 12, 1)
        end_of_last_month = datetime(today.year, 1, 1) - timedelta(days=1)
    else:
        start_of_last_month = datetime(today.year, today.month - 1, 1)
        end_of_last_month = datetime(today.year, today.month, 1) - timedelta(days=1)
    
    created_count = 0
    
    for employee in employees:
        # Check if record already exists
        existing = db.query(EmployeePerformance).filter(
            EmployeePerformance.employee_id == employee.id,
            EmployeePerformance.period_start == start_of_last_month,
            EmployeePerformance.period_end == end_of_last_month
        ).first()
        
        if existing:
            continue  # Skip if already calculated
        
        # Calculate metrics
        metrics = calculate_performance_metrics(employee.id, start_of_last_month, end_of_last_month, db)
        
        # Create performance record
        performance = EmployeePerformance(
            employee_id=employee.id,
            period_start=start_of_last_month,
            period_end=end_of_last_month,
            **metrics
        )
        
        db.add(performance)
        created_count += 1
    
    db.commit()
    
    return {
        "message": f"Monthly performance calculated for {created_count} employees",
        "period": f"{start_of_last_month.strftime('%Y-%m')} to {end_of_last_month.strftime('%Y-%m-%d')}"
    }
