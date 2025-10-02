from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.db.database import get_db
from app.models import Invoice, User, Client
from app.core.security import get_current_active_user
from app.tasks.email_tasks import send_invoice_email, send_payment_reminder

router = APIRouter()


class InvoiceCreate(BaseModel):
    client_id: int
    amount: Decimal
    due_date: datetime
    description: Optional[str] = None


class InvoiceUpdate(BaseModel):
    amount: Optional[Decimal] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    description: Optional[str] = None
    paid_date: Optional[datetime] = None


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    client_id: int
    client_name: Optional[str] = None
    user_id: int
    amount: Decimal
    status: str
    due_date: Optional[datetime]
    paid_date: Optional[datetime]
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceStats(BaseModel):
    total_invoices: int
    paid_invoices: int
    overdue_invoices: int
    pending_invoices: int
    total_revenue: Decimal
    overdue_amount: Decimal


class PaginatedInvoiceResponse(BaseModel):
    items: List[InvoiceResponse]
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
            detail="Admin access required"
        )


@router.get("/stats", response_model=InvoiceStats)
async def get_invoice_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get invoice statistics"""
    if current_user.role == "admin":
        # Admin can see all invoices
        invoices = db.query(Invoice).all()
    else:
        # User can only see their own invoices
        invoices = db.query(Invoice).filter(Invoice.user_id == current_user.id).all()
    
    total_invoices = len(invoices)
    paid_invoices = len([i for i in invoices if i.status == "paid"])
    overdue_invoices = len([i for i in invoices if i.status == "overdue"])
    pending_invoices = len([i for i in invoices if i.status in ["draft", "sent"]])
    
    total_revenue = sum([i.amount for i in invoices if i.status == "paid"])
    overdue_amount = sum([i.amount for i in invoices if i.status == "overdue"])
    
    return InvoiceStats(
        total_invoices=total_invoices,
        paid_invoices=paid_invoices,
        overdue_invoices=overdue_invoices,
        pending_invoices=pending_invoices,
        total_revenue=total_revenue,
        overdue_amount=overdue_amount
    )


@router.get("/", response_model=PaginatedInvoiceResponse)
async def get_invoices(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    client_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get invoices with filtering and pagination"""
    if current_user.role == "admin":
        # Admin can see all invoices
        query = db.query(Invoice)
    else:
        # User can only see their own invoices
        query = db.query(Invoice).filter(Invoice.user_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(Invoice.status == status)
    if client_id:
        query = query.filter(Invoice.client_id == client_id)
    
    # Count total for pagination
    total = query.count()
    
    # Calculate pagination
    pages = (total + per_page - 1) // per_page
    has_next = page < pages
    has_prev = page > 1
    skip = (page - 1) * per_page
    
    # Get paginated results with client information
    invoices = query.order_by(Invoice.created_at.desc()).offset(skip).limit(per_page).all()
    
    # Format response with client names
    invoice_responses = []
    for invoice in invoices:
        client = db.query(Client).filter(Client.id == invoice.client_id).first()
        invoice_responses.append(InvoiceResponse(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            client_id=invoice.client_id,
            client_name=client.name if client else None,
            user_id=invoice.user_id,
            amount=invoice.amount,
            status=invoice.status,
            due_date=invoice.due_date,
            paid_date=invoice.paid_date,
            description=invoice.description,
            created_at=invoice.created_at
        ))
    
    return PaginatedInvoiceResponse(
        items=invoice_responses,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.post("/", response_model=InvoiceResponse)
async def create_invoice(
    invoice_data: InvoiceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new invoice - Only admin can create invoices"""
    check_admin_role(current_user)
    
    # Verify client exists and belongs to current user
    client = db.query(Client).filter(Client.id == invoice_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Generate invoice number
    invoice_count = db.query(Invoice).count()
    invoice_number = f"INV-{datetime.now().strftime('%Y')}-{str(invoice_count + 1).zfill(4)}"
    
    # Create invoice
    invoice = Invoice(
        invoice_number=invoice_number,
        client_id=invoice_data.client_id,
        user_id=current_user.id,
        amount=invoice_data.amount,
        status="draft",
        due_date=invoice_data.due_date,
        description=invoice_data.description
    )
    
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    # Get client name for response
    client = db.query(Client).filter(Client.id == invoice.client_id).first()
    
    return InvoiceResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        client_id=invoice.client_id,
        client_name=client.name if client else None,
        user_id=invoice.user_id,
        amount=invoice.amount,
        status=invoice.status,
        due_date=invoice.due_date,
        paid_date=invoice.paid_date,
        description=invoice.description,
        created_at=invoice.created_at
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific invoice"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and invoice.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get client name
    client = db.query(Client).filter(Client.id == invoice.client_id).first()
    
    return InvoiceResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        client_id=invoice.client_id,
        client_name=client.name if client else None,
        user_id=invoice.user_id,
        amount=invoice.amount,
        status=invoice.status,
        due_date=invoice.due_date,
        paid_date=invoice.paid_date,
        description=invoice.description,
        created_at=invoice.created_at
    )


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing invoice"""
    check_admin_role(current_user)
    
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Update fields
    if invoice_data.amount is not None:
        invoice.amount = invoice_data.amount
    if invoice_data.status is not None:
        invoice.status = invoice_data.status
    if invoice_data.due_date is not None:
        invoice.due_date = invoice_data.due_date
    if invoice_data.description is not None:
        invoice.description = invoice_data.description
    if invoice_data.paid_date is not None:
        invoice.paid_date = invoice_data.paid_date
    
    db.commit()
    db.refresh(invoice)
    
    # Get client name
    client = db.query(Client).filter(Client.id == invoice.client_id).first()
    
    return InvoiceResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        client_id=invoice.client_id,
        client_name=client.name if client else None,
        user_id=invoice.user_id,
        amount=invoice.amount,
        status=invoice.status,
        due_date=invoice.due_date,
        paid_date=invoice.paid_date,
        description=invoice.description,
        created_at=invoice.created_at
    )


@router.delete("/{invoice_id}")
async def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an invoice"""
    check_admin_role(current_user)
    
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    db.delete(invoice)
    db.commit()
    
    return {"message": "Invoice deleted successfully"}


@router.post("/{invoice_id}/send")
async def send_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send invoice via email"""
    check_admin_role(current_user)
    
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Update status to sent
    invoice.status = "sent"
    db.commit()
    
    # Schedule email sending
    send_invoice_email.delay(invoice_id)
    
    return {"message": "Invoice sent successfully", "invoice_id": invoice_id}


@router.post("/{invoice_id}/mark-paid")
async def mark_invoice_paid(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark invoice as paid"""
    check_admin_role(current_user)
    
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Update status and paid date
    invoice.status = "paid"
    invoice.paid_date = datetime.now()
    db.commit()
    
    return {"message": "Invoice marked as paid", "invoice_id": invoice_id}


@router.post("/overdue/send-reminders")
async def send_overdue_reminders(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send payment reminders for overdue invoices"""
    check_admin_role(current_user)
    
    # Find overdue invoices
    overdue_invoices = db.query(Invoice).filter(
        Invoice.status.in_(["sent"]),
        Invoice.due_date < datetime.now()
    ).all()
    
    # Update status to overdue and send reminders
    reminder_count = 0
    for invoice in overdue_invoices:
        invoice.status = "overdue"
        send_payment_reminder.delay(invoice.id)
        reminder_count += 1
    
    db.commit()
    
    return {
        "message": f"Payment reminders sent for {reminder_count} overdue invoices",
        "count": reminder_count
    }
