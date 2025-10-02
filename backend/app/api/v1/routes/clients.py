from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from app.db.database import get_db
from app.models import Client, User, PortalSubmission
from app.core.security import get_current_active_user

router = APIRouter()


class ClientCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    status: str = "pending"
    onboarding_stage: str = "initial"


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    onboarding_stage: Optional[str] = None


class ClientResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    status: str
    onboarding_stage: str
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ClientStats(BaseModel):
    total_clients: int
    active_clients: int
    pending_clients: int
    completed_clients: int


class PaginatedClientResponse(BaseModel):
    items: List[ClientResponse]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


class ClientPortalSubmission(BaseModel):
    project_requirements: str
    budget_range: str
    timeline: str
    additional_info: Optional[str] = None
    preferred_contact_method: str = "email"
    urgency_level: str = "medium"


class PortalSubmissionResponse(BaseModel):
    id: int
    client_id: int
    project_requirements: str
    budget_range: str
    timeline: str
    additional_info: Optional[str]
    preferred_contact_method: str
    urgency_level: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/stats", response_model=ClientStats)
async def get_client_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get client statistics for the dashboard"""
    total_clients = db.query(Client).filter(Client.owner_id == current_user.id).count()
    active_clients = db.query(Client).filter(
        Client.owner_id == current_user.id,
        Client.status == "active"
    ).count()
    pending_clients = db.query(Client).filter(
        Client.owner_id == current_user.id,
        Client.status == "pending"
    ).count()
    completed_clients = db.query(Client).filter(
        Client.owner_id == current_user.id,
        Client.status == "completed"
    ).count()
    
    return ClientStats(
        total_clients=total_clients,
        active_clients=active_clients,
        pending_clients=pending_clients,
        completed_clients=completed_clients
    )


@router.post("/", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new client"""
    # Check if client email already exists for this user
    existing_client = db.query(Client).filter(
        Client.email == client_data.email,
        Client.owner_id == current_user.id
    ).first()
    
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client with this email already exists"
        )
    
    client = Client(
        name=client_data.name,
        email=client_data.email,
        phone=client_data.phone,
        company=client_data.company,
        status=client_data.status,
        onboarding_stage=client_data.onboarding_stage,
        owner_id=current_user.id
    )
    
    db.add(client)
    db.commit()
    db.refresh(client)
    
    return client


@router.get("/", response_model=PaginatedClientResponse)
async def get_clients(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all clients for current user with filtering and pagination"""
    query = db.query(Client).filter(Client.owner_id == current_user.id)
    
    # Apply search filter
    if search:
        query = query.filter(
            (Client.name.contains(search)) |
            (Client.email.contains(search)) |
            (Client.company.contains(search))
        )
    
    # Apply status filter
    if status:
        query = query.filter(Client.status == status)
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    skip = (page - 1) * per_page
    pages = (total + per_page - 1) // per_page  # Ceiling division
    has_next = page < pages
    has_prev = page > 1
    
    # Get paginated results
    clients = query.offset(skip).limit(per_page).all()
    
    return PaginatedClientResponse(
        items=clients,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific client"""
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.owner_id == current_user.id
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing client"""
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.owner_id == current_user.id
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Update client fields
    update_data = client_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    
    return client


@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a client"""
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.owner_id == current_user.id
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    db.delete(client)
    db.commit()
    
    return {"message": "Client deleted successfully"}


@router.post("/portal/{client_id}/submit", response_model=PortalSubmissionResponse)
async def submit_client_portal_form(
    client_id: int,
    submission: ClientPortalSubmission,
    db: Session = Depends(get_db)
):
    """Submit client portal form (public endpoint)"""
    # Check if client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Create portal submission record
    portal_submission = PortalSubmission(
        client_id=client_id,
        project_requirements=submission.project_requirements,
        budget_range=submission.budget_range,
        timeline=submission.timeline,
        additional_info=submission.additional_info,
        preferred_contact_method=submission.preferred_contact_method,
        urgency_level=submission.urgency_level,
        status="new"
    )
    
    db.add(portal_submission)
    
    # Update client status to indicate new submission
    client.status = "portal_submitted"
    client.onboarding_stage = "requirements_submitted"
    
    db.commit()
    db.refresh(portal_submission)
    
    return portal_submission


@router.get("/portal/{client_id}/info", response_model=dict)
async def get_client_portal_info(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Get basic client info for portal display (public endpoint)"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client portal not found"
        )
    
    return {
        "client_name": client.name,
        "company": client.company,
        "portal_active": True
    }


@router.get("/{client_id}/portal-submissions", response_model=List[PortalSubmissionResponse])
async def get_client_portal_submissions(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all portal submissions for a client"""
    # Check if client exists and belongs to current user
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.owner_id == current_user.id
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    submissions = db.query(PortalSubmission).filter(
        PortalSubmission.client_id == client_id
    ).order_by(PortalSubmission.created_at.desc()).all()
    
    return submissions


@router.patch("/portal-submissions/{submission_id}/status")
async def update_portal_submission_status(
    submission_id: int,
    status: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update portal submission status"""
    submission = db.query(PortalSubmission).join(Client).filter(
        PortalSubmission.id == submission_id,
        Client.owner_id == current_user.id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portal submission not found"
        )
    
    submission.status = status
    db.commit()
    
    return {"message": "Portal submission status updated", "status": status}
