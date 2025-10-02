from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.db.database import get_db
from app.models import Task, User, Client
from app.core.security import get_current_active_user

router = APIRouter()


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: str = "general"  # invoice, follow_up, content_creation, lead_generation, client_onboarding
    priority: str = "medium"  # low, medium, high, urgent
    due_date: Optional[datetime] = None
    assigned_to_id: int
    client_id: Optional[int] = None
    estimated_hours: Optional[Decimal] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None  # todo, in_progress, review, completed, blocked
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None
    client_id: Optional[int] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    type: str
    status: str
    priority: str
    due_date: Optional[datetime]
    assigned_to_id: int
    assigned_to_name: Optional[str]
    created_by_id: int
    created_by_name: Optional[str]
    client_id: Optional[int]
    client_name: Optional[str]
    estimated_hours: Optional[Decimal]
    actual_hours: Optional[Decimal]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TaskStats(BaseModel):
    total_tasks: int
    todo_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    overdue_tasks: int


class PaginatedTaskResponse(BaseModel):
    items: List[TaskResponse]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


def check_admin_role(current_user: User):
    """Check if current user is admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can perform this action"
        )


@router.get("/stats", response_model=TaskStats)
async def get_task_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get task statistics - Admin sees all, Employee sees only assigned tasks"""
    if current_user.role == "admin":
        # Admin sees all tasks
        base_query = db.query(Task)
    else:
        # Employee sees only assigned tasks
        base_query = db.query(Task).filter(Task.assigned_to_id == current_user.id)
    
    total_tasks = base_query.count()
    todo_tasks = base_query.filter(Task.status == "todo").count()
    in_progress_tasks = base_query.filter(Task.status == "in_progress").count()
    completed_tasks = base_query.filter(Task.status == "completed").count()
    
    # Overdue tasks (past due date and not completed)
    overdue_tasks = base_query.filter(
        Task.due_date < datetime.now(),
        Task.status.in_(["todo", "in_progress", "review", "blocked"])
    ).count()
    
    return TaskStats(
        total_tasks=total_tasks,
        todo_tasks=todo_tasks,
        in_progress_tasks=in_progress_tasks,
        completed_tasks=completed_tasks,
        overdue_tasks=overdue_tasks
    )


@router.get("/", response_model=PaginatedTaskResponse)
async def get_tasks(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_to_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get tasks with filtering and pagination"""
    if current_user.role == "admin":
        # Admin can see all tasks
        query = db.query(Task)
    else:
        # Employee can only see assigned tasks
        query = db.query(Task).filter(Task.assigned_to_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if type:
        query = query.filter(Task.type == type)
    if assigned_to_id and current_user.role == "admin":  # Only admin can filter by assignee
        query = query.filter(Task.assigned_to_id == assigned_to_id)
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    skip = (page - 1) * per_page
    pages = (total + per_page - 1) // per_page
    has_next = page < pages
    has_prev = page > 1
    
    # Get paginated results with relationships
    tasks = query.offset(skip).limit(per_page).all()
    
    # Format response with user and client names
    task_responses = []
    for task in tasks:
        assigned_to = db.query(User).filter(User.id == task.assigned_to_id).first()
        created_by = db.query(User).filter(User.id == task.created_by_id).first()
        client = db.query(Client).filter(Client.id == task.client_id).first() if task.client_id else None
        
        task_responses.append(TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            type=task.type,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            assigned_to_id=task.assigned_to_id,
            assigned_to_name=assigned_to.full_name if assigned_to else None,
            created_by_id=task.created_by_id,
            created_by_name=created_by.full_name if created_by else None,
            client_id=task.client_id,
            client_name=client.name if client else None,
            estimated_hours=task.estimated_hours,
            actual_hours=task.actual_hours,
            created_at=task.created_at,
            updated_at=task.updated_at
        ))
    
    return PaginatedTaskResponse(
        items=task_responses,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new task - Only admin can create tasks"""
    check_admin_role(current_user)
    
    # Verify assigned user exists
    assigned_user = db.query(User).filter(User.id == task_data.assigned_to_id).first()
    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )
    
    # Verify client exists if provided
    if task_data.client_id:
        client = db.query(Client).filter(Client.id == task_data.client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
    
    task = Task(
        title=task_data.title,
        description=task_data.description,
        type=task_data.type,
        priority=task_data.priority,
        due_date=task_data.due_date,
        assigned_to_id=task_data.assigned_to_id,
        created_by_id=current_user.id,
        client_id=task_data.client_id,
        estimated_hours=task_data.estimated_hours,
        status="todo"
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Return formatted response
    assigned_to = db.query(User).filter(User.id == task.assigned_to_id).first()
    client = db.query(Client).filter(Client.id == task.client_id).first() if task.client_id else None
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        type=task.type,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        assigned_to_id=task.assigned_to_id,
        assigned_to_name=assigned_to.full_name if assigned_to else None,
        created_by_id=task.created_by_id,
        created_by_name=current_user.full_name,
        client_id=task.client_id,
        client_name=client.name if client else None,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and task.assigned_to_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view tasks assigned to you"
        )
    
    # Format response
    assigned_to = db.query(User).filter(User.id == task.assigned_to_id).first()
    created_by = db.query(User).filter(User.id == task.created_by_id).first()
    client = db.query(Client).filter(Client.id == task.client_id).first() if task.client_id else None
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        type=task.type,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        assigned_to_id=task.assigned_to_id,
        assigned_to_name=assigned_to.full_name if assigned_to else None,
        created_by_id=task.created_by_id,
        created_by_name=created_by.full_name if created_by else None,
        client_id=task.client_id,
        client_name=client.name if client else None,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update task - Admin can update everything, Employee can only update status and actual_hours"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and task.assigned_to_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update tasks assigned to you"
        )
    
    # Update fields based on role
    update_data = task_data.dict(exclude_unset=True)
    
    if current_user.role == "employee":
        # Employees can only update status and actual_hours
        allowed_fields = {"status", "actual_hours"}
        update_data = {k: v for k, v in update_data.items() if k in allowed_fields}
    
    # Apply updates
    for field, value in update_data.items():
        if hasattr(task, field):
            setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    # Format response
    assigned_to = db.query(User).filter(User.id == task.assigned_to_id).first()
    created_by = db.query(User).filter(User.id == task.created_by_id).first()
    client = db.query(Client).filter(Client.id == task.client_id).first() if task.client_id else None
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        type=task.type,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        assigned_to_id=task.assigned_to_id,
        assigned_to_name=assigned_to.full_name if assigned_to else None,
        created_by_id=task.created_by_id,
        created_by_name=created_by.full_name if created_by else None,
        client_id=task.client_id,
        client_name=client.name if client else None,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete task - Only admin can delete tasks"""
    check_admin_role(current_user)
    
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}


@router.get("/employees/list")
async def get_employees(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of employees for task assignment - Only admin can access"""
    check_admin_role(current_user)
    
    employees = db.query(User).filter(User.role == "employee", User.is_active == True).all()
    
    return [
        {
            "id": emp.id,
            "full_name": emp.full_name,
            "email": emp.email
        }
        for emp in employees
    ]
