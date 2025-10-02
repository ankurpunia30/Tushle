from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.db.database import get_db
from app.models import Lead, User, Client
from app.core.security import get_current_active_user

router = APIRouter()


class LeadCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    status: str = "new"  # new, contacted, interested, qualified, proposal, closed_won, closed_lost
    priority: str = "medium"  # low, medium, high, urgent
    estimated_value: Optional[Decimal] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    assigned_to_id: int


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    estimated_value: Optional[Decimal] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None


class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    status: str
    priority: str
    estimated_value: Optional[Decimal]
    notes: Optional[str]
    follow_up_date: Optional[datetime]
    assigned_to_id: int
    assigned_to_name: Optional[str]
    created_by_id: int
    created_by_name: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LeadStats(BaseModel):
    total_leads: int
    new_leads: int
    qualified_leads: int
    proposal_leads: int
    closed_won: int
    closed_lost: int
    total_estimated_value: Optional[Decimal]


class PaginatedLeadResponse(BaseModel):
    items: List[LeadResponse]
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


@router.get("/stats", response_model=LeadStats)
async def get_lead_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get lead statistics - Admin sees all, Employee sees only assigned leads"""
    if current_user.role == "admin":
        # Admin sees all leads
        base_query = db.query(Lead)
    else:
        # Employee sees only assigned leads
        base_query = db.query(Lead).filter(Lead.assigned_to_id == current_user.id)
    
    total_leads = base_query.count()
    new_leads = base_query.filter(Lead.status == "new").count()
    qualified_leads = base_query.filter(Lead.status == "qualified").count()
    proposal_leads = base_query.filter(Lead.status == "proposal").count()
    closed_won = base_query.filter(Lead.status == "closed_won").count()
    closed_lost = base_query.filter(Lead.status == "closed_lost").count()
    
    # Calculate total estimated value
    estimated_value_query = base_query.filter(Lead.estimated_value.isnot(None))
    total_estimated_value = sum([lead.estimated_value for lead in estimated_value_query.all()]) if estimated_value_query.count() > 0 else None
    
    return LeadStats(
        total_leads=total_leads,
        new_leads=new_leads,
        qualified_leads=qualified_leads,
        proposal_leads=proposal_leads,
        closed_won=closed_won,
        closed_lost=closed_lost,
        total_estimated_value=total_estimated_value
    )


@router.get("/", response_model=PaginatedLeadResponse)
async def get_leads(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_to_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get leads with filtering and pagination"""
    if current_user.role == "admin":
        # Admin can see all leads
        query = db.query(Lead)
    else:
        # Employee can only see assigned leads
        query = db.query(Lead).filter(Lead.assigned_to_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(Lead.status == status)
    if priority:
        query = query.filter(Lead.priority == priority)
    if assigned_to_id and current_user.role == "admin":  # Only admin can filter by assignee
        query = query.filter(Lead.assigned_to_id == assigned_to_id)
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    skip = (page - 1) * per_page
    pages = (total + per_page - 1) // per_page
    has_next = page < pages
    has_prev = page > 1
    
    # Get paginated results with relationships
    leads = query.offset(skip).limit(per_page).all()
    
    # Format response with user names
    lead_responses = []
    for lead in leads:
        assigned_to = db.query(User).filter(User.id == lead.assigned_to_id).first()
        created_by = db.query(User).filter(User.id == lead.created_by_id).first()
        
        lead_responses.append(LeadResponse(
            id=lead.id,
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            company=lead.company,
            status=lead.status,
            priority=lead.priority,
            estimated_value=lead.estimated_value,
            notes=lead.notes,
            follow_up_date=lead.follow_up_date,
            assigned_to_id=lead.assigned_to_id,
            assigned_to_name=assigned_to.full_name if assigned_to else None,
            created_by_id=lead.created_by_id,
            created_by_name=created_by.full_name if created_by else None,
            created_at=lead.created_at,
            updated_at=lead.updated_at
        ))
    
    return PaginatedLeadResponse(
        items=lead_responses,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead_data: LeadCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new lead - Only admin can create leads"""
    check_admin_role(current_user)
    
    # Verify assigned user exists
    assigned_user = db.query(User).filter(User.id == lead_data.assigned_to_id).first()
    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )
    
    lead = Lead(
        name=lead_data.name,
        email=lead_data.email,
        phone=lead_data.phone,
        company=lead_data.company,
        status=lead_data.status,
        priority=lead_data.priority,
        estimated_value=lead_data.estimated_value,
        notes=lead_data.notes,
        follow_up_date=lead_data.follow_up_date,
        assigned_to_id=lead_data.assigned_to_id,
        created_by_id=current_user.id
    )
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    # Return formatted response
    assigned_to = db.query(User).filter(User.id == lead.assigned_to_id).first()
    
    return LeadResponse(
        id=lead.id,
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        company=lead.company,
        status=lead.status,
        priority=lead.priority,
        estimated_value=lead.estimated_value,
        notes=lead.notes,
        follow_up_date=lead.follow_up_date,
        assigned_to_id=lead.assigned_to_id,
        assigned_to_name=assigned_to.full_name if assigned_to else None,
        created_by_id=lead.created_by_id,
        created_by_name=current_user.full_name,
        created_at=lead.created_at,
        updated_at=lead.updated_at
    )


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and lead.assigned_to_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view leads assigned to you"
        )
    
    # Format response
    assigned_to = db.query(User).filter(User.id == lead.assigned_to_id).first()
    created_by = db.query(User).filter(User.id == lead.created_by_id).first()
    
    return LeadResponse(
        id=lead.id,
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        company=lead.company,
        status=lead.status,
        priority=lead.priority,
        estimated_value=lead.estimated_value,
        notes=lead.notes,
        follow_up_date=lead.follow_up_date,
        assigned_to_id=lead.assigned_to_id,
        assigned_to_name=assigned_to.full_name if assigned_to else None,
        created_by_id=lead.created_by_id,
        created_by_name=created_by.full_name if created_by else None,
        created_at=lead.created_at,
        updated_at=lead.updated_at
    )


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update lead - Admin can update everything, Employee can only update status and notes"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and lead.assigned_to_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update leads assigned to you"
        )
    
    # Update fields based on role
    update_data = lead_data.dict(exclude_unset=True)
    
    if current_user.role == "employee":
        # Employees can only update status, notes, and follow_up_date
        allowed_fields = {"status", "notes", "follow_up_date"}
        update_data = {k: v for k, v in update_data.items() if k in allowed_fields}
    
    # Apply updates
    for field, value in update_data.items():
        if hasattr(lead, field):
            setattr(lead, field, value)
    
    db.commit()
    db.refresh(lead)
    
    # Format response
    assigned_to = db.query(User).filter(User.id == lead.assigned_to_id).first()
    created_by = db.query(User).filter(User.id == lead.created_by_id).first()
    
    return LeadResponse(
        id=lead.id,
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        company=lead.company,
        status=lead.status,
        priority=lead.priority,
        estimated_value=lead.estimated_value,
        notes=lead.notes,
        follow_up_date=lead.follow_up_date,
        assigned_to_id=lead.assigned_to_id,
        assigned_to_name=assigned_to.full_name if assigned_to else None,
        created_by_id=lead.created_by_id,
        created_by_name=created_by.full_name if created_by else None,
        created_at=lead.created_at,
        updated_at=lead.updated_at
    )


@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete lead - Only admin can delete leads"""
    check_admin_role(current_user)
    
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    db.delete(lead)
    db.commit()
    
    return {"message": "Lead deleted successfully"}


@router.post("/{lead_id}/convert-to-client")
async def convert_lead_to_client(
    lead_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Convert a lead to a client - Only admin can convert leads"""
    check_admin_role(current_user)
    
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    if lead.status != "closed_won":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only convert won leads to clients"
        )
    
    # Create new client from lead
    client = Client(
        name=lead.company or lead.name,
        email=lead.email,
        phone=lead.phone,
        status="active",
        created_by_id=current_user.id
    )
    
    db.add(client)
    db.commit()
    db.refresh(client)
    
    # Update lead status to converted
    lead.status = "converted"
    db.commit()
    
    return {
        "message": "Lead converted to client successfully",
        "client_id": client.id,
        "lead_id": lead.id
    }
