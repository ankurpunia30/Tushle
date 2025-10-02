from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.db.database import get_db
from app.models import Meeting, User, Client, Lead
from app.core.security import get_current_active_user

router = APIRouter()


class MeetingCreate(BaseModel):
    title: str
    description: Optional[str] = None
    meeting_type: str = "general"
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    assigned_to_id: int
    client_id: Optional[int] = None
    lead_id: Optional[int] = None
    attendees: Optional[List[str]] = None  # List of email addresses


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    meeting_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    assigned_to_id: Optional[int] = None
    client_id: Optional[int] = None
    lead_id: Optional[int] = None
    status: Optional[str] = None
    attendees: Optional[List[str]] = None
    meeting_notes: Optional[str] = None
    follow_up_required: Optional[bool] = None


class MeetingResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    meeting_type: str
    start_time: datetime
    end_time: datetime
    location: Optional[str]
    assigned_to_id: int
    assigned_to_name: Optional[str]
    created_by_id: int
    created_by_name: Optional[str]
    client_id: Optional[int]
    client_name: Optional[str]
    lead_id: Optional[int]
    lead_name: Optional[str]
    status: str
    attendees: Optional[List[str]]
    meeting_notes: Optional[str]
    follow_up_required: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MeetingStats(BaseModel):
    total_meetings: int
    scheduled_meetings: int
    completed_meetings: int
    cancelled_meetings: int
    today_meetings: int
    upcoming_meetings: int


class PaginatedMeetingResponse(BaseModel):
    items: List[MeetingResponse]
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


@router.get("/stats", response_model=MeetingStats)
async def get_meeting_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get meeting statistics"""
    if current_user.role == "admin":
        # Admin sees all meetings
        base_query = db.query(Meeting)
    else:
        # Employee sees only assigned meetings
        base_query = db.query(Meeting).filter(Meeting.assigned_to_id == current_user.id)
    
    total_meetings = base_query.count()
    scheduled_meetings = base_query.filter(Meeting.status == "scheduled").count()
    completed_meetings = base_query.filter(Meeting.status == "completed").count()
    cancelled_meetings = base_query.filter(Meeting.status == "cancelled").count()
    
    # Today's meetings
    today = datetime.now().date()
    today_meetings = base_query.filter(
        Meeting.start_time >= datetime.combine(today, datetime.min.time()),
        Meeting.start_time < datetime.combine(today, datetime.max.time())
    ).count()
    
    # Upcoming meetings (next 7 days)
    from datetime import timedelta
    next_week = datetime.now() + timedelta(days=7)
    upcoming_meetings = base_query.filter(
        Meeting.start_time >= datetime.now(),
        Meeting.start_time <= next_week,
        Meeting.status == "scheduled"
    ).count()
    
    return MeetingStats(
        total_meetings=total_meetings,
        scheduled_meetings=scheduled_meetings,
        completed_meetings=completed_meetings,
        cancelled_meetings=cancelled_meetings,
        today_meetings=today_meetings,
        upcoming_meetings=upcoming_meetings
    )


@router.get("/", response_model=PaginatedMeetingResponse)
async def get_meetings(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    meeting_type: Optional[str] = Query(None),
    assigned_to_id: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get meetings with filtering and pagination"""
    if current_user.role == "admin":
        # Admin can see all meetings
        query = db.query(Meeting)
    else:
        # Employee can only see assigned meetings
        query = db.query(Meeting).filter(Meeting.assigned_to_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(Meeting.status == status)
    if meeting_type:
        query = query.filter(Meeting.meeting_type == meeting_type)
    if assigned_to_id and current_user.role == "admin":
        query = query.filter(Meeting.assigned_to_id == assigned_to_id)
    if date_from:
        query = query.filter(Meeting.start_time >= date_from)
    if date_to:
        query = query.filter(Meeting.start_time <= date_to)
    
    # Order by start time
    query = query.order_by(Meeting.start_time.asc())
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    skip = (page - 1) * per_page
    pages = (total + per_page - 1) // per_page
    has_next = page < pages
    has_prev = page > 1
    
    # Get paginated results
    meetings = query.offset(skip).limit(per_page).all()
    
    # Format response
    meeting_responses = []
    for meeting in meetings:
        assigned_to = db.query(User).filter(User.id == meeting.assigned_to_id).first()
        created_by = db.query(User).filter(User.id == meeting.created_by_id).first()
        client = db.query(Client).filter(Client.id == meeting.client_id).first() if meeting.client_id else None
        lead = db.query(Lead).filter(Lead.id == meeting.lead_id).first() if meeting.lead_id else None
        
        meeting_responses.append(MeetingResponse(
            id=meeting.id,
            title=meeting.title,
            description=meeting.description,
            meeting_type=meeting.meeting_type,
            start_time=meeting.start_time,
            end_time=meeting.end_time,
            location=meeting.location,
            assigned_to_id=meeting.assigned_to_id,
            assigned_to_name=assigned_to.full_name if assigned_to else None,
            created_by_id=meeting.created_by_id,
            created_by_name=created_by.full_name if created_by else None,
            client_id=meeting.client_id,
            client_name=client.name if client else None,
            lead_id=meeting.lead_id,
            lead_name=lead.name if lead else None,
            status=meeting.status,
            attendees=meeting.attendees,
            meeting_notes=meeting.meeting_notes,
            follow_up_required=meeting.follow_up_required,
            created_at=meeting.created_at,
            updated_at=meeting.updated_at
        ))
    
    return PaginatedMeetingResponse(
        items=meeting_responses,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.post("/", response_model=MeetingResponse)
async def create_meeting(
    meeting_data: MeetingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new meeting - Only admin can create meetings"""
    check_admin_role(current_user)
    
    # Verify assigned user exists
    assigned_user = db.query(User).filter(User.id == meeting_data.assigned_to_id).first()
    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )
    
    # Verify client exists if provided
    if meeting_data.client_id:
        client = db.query(Client).filter(Client.id == meeting_data.client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
    
    # Verify lead exists if provided
    if meeting_data.lead_id:
        lead = db.query(Lead).filter(Lead.id == meeting_data.lead_id).first()
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
    
    # Check for scheduling conflicts
    conflicts = db.query(Meeting).filter(
        Meeting.assigned_to_id == meeting_data.assigned_to_id,
        Meeting.status == "scheduled",
        Meeting.start_time < meeting_data.end_time,
        Meeting.end_time > meeting_data.start_time
    ).all()
    
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meeting conflicts with existing scheduled meeting"
        )
    
    meeting = Meeting(
        title=meeting_data.title,
        description=meeting_data.description,
        meeting_type=meeting_data.meeting_type,
        start_time=meeting_data.start_time,
        end_time=meeting_data.end_time,
        location=meeting_data.location,
        assigned_to_id=meeting_data.assigned_to_id,
        created_by_id=current_user.id,
        client_id=meeting_data.client_id,
        lead_id=meeting_data.lead_id,
        attendees=meeting_data.attendees,
        status="scheduled"
    )
    
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    
    # TODO: Integrate with calendar APIs (Google Calendar, Outlook, etc.)
    
    # Return formatted response
    assigned_to = db.query(User).filter(User.id == meeting.assigned_to_id).first()
    client = db.query(Client).filter(Client.id == meeting.client_id).first() if meeting.client_id else None
    lead = db.query(Lead).filter(Lead.id == meeting.lead_id).first() if meeting.lead_id else None
    
    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        description=meeting.description,
        meeting_type=meeting.meeting_type,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        location=meeting.location,
        assigned_to_id=meeting.assigned_to_id,
        assigned_to_name=assigned_to.full_name if assigned_to else None,
        created_by_id=meeting.created_by_id,
        created_by_name=current_user.full_name,
        client_id=meeting.client_id,
        client_name=client.name if client else None,
        lead_id=meeting.lead_id,
        lead_name=lead.name if lead else None,
        status=meeting.status,
        attendees=meeting.attendees,
        meeting_notes=meeting.meeting_notes,
        follow_up_required=meeting.follow_up_required,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at
    )


@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: int,
    meeting_data: MeetingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update meeting"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and meeting.assigned_to_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update meetings assigned to you"
        )
    
    # Update fields based on role
    update_data = meeting_data.dict(exclude_unset=True)
    
    if current_user.role == "employee":
        # Employees can only update certain fields
        allowed_fields = {"status", "meeting_notes", "follow_up_required"}
        update_data = {k: v for k, v in update_data.items() if k in allowed_fields}
    
    # Apply updates
    for field, value in update_data.items():
        if hasattr(meeting, field):
            setattr(meeting, field, value)
    
    db.commit()
    db.refresh(meeting)
    
    # Format response
    assigned_to = db.query(User).filter(User.id == meeting.assigned_to_id).first()
    created_by = db.query(User).filter(User.id == meeting.created_by_id).first()
    client = db.query(Client).filter(Client.id == meeting.client_id).first() if meeting.client_id else None
    lead = db.query(Lead).filter(Lead.id == meeting.lead_id).first() if meeting.lead_id else None
    
    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        description=meeting.description,
        meeting_type=meeting.meeting_type,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        location=meeting.location,
        assigned_to_id=meeting.assigned_to_id,
        assigned_to_name=assigned_to.full_name if assigned_to else None,
        created_by_id=meeting.created_by_id,
        created_by_name=created_by.full_name if created_by else None,
        client_id=meeting.client_id,
        client_name=client.name if client else None,
        lead_id=meeting.lead_id,
        lead_name=lead.name if lead else None,
        status=meeting.status,
        attendees=meeting.attendees,
        meeting_notes=meeting.meeting_notes,
        follow_up_required=meeting.follow_up_required,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at
    )


@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete meeting - Only admin can delete meetings"""
    check_admin_role(current_user)
    
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    db.delete(meeting)
    db.commit()
    
    return {"message": "Meeting deleted successfully"}


@router.get("/calendar/upcoming")
async def get_upcoming_meetings(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get upcoming meetings for calendar view"""
    from datetime import timedelta
    
    end_date = datetime.now() + timedelta(days=days)
    
    if current_user.role == "admin":
        meetings = db.query(Meeting).filter(
            Meeting.start_time >= datetime.now(),
            Meeting.start_time <= end_date,
            Meeting.status.in_(["scheduled", "rescheduled"])
        ).order_by(Meeting.start_time.asc()).all()
    else:
        meetings = db.query(Meeting).filter(
            Meeting.assigned_to_id == current_user.id,
            Meeting.start_time >= datetime.now(),
            Meeting.start_time <= end_date,
            Meeting.status.in_(["scheduled", "rescheduled"])
        ).order_by(Meeting.start_time.asc()).all()
    
    # Format for calendar display
    calendar_events = []
    for meeting in meetings:
        assigned_to = db.query(User).filter(User.id == meeting.assigned_to_id).first()
        client = db.query(Client).filter(Client.id == meeting.client_id).first() if meeting.client_id else None
        
        calendar_events.append({
            "id": meeting.id,
            "title": meeting.title,
            "start": meeting.start_time.isoformat(),
            "end": meeting.end_time.isoformat(),
            "location": meeting.location,
            "assignee": assigned_to.full_name if assigned_to else None,
            "client": client.name if client else None,
            "type": meeting.meeting_type,
            "status": meeting.status
        })
    
    return calendar_events
