from celery import current_task
from app.celery_app import celery_app
from app.db.database import SessionLocal
from app.models import Lead, Task
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


@celery_app.task
def follow_up_leads():
    """Follow up with leads that haven't been contacted recently"""
    
    db = SessionLocal()
    try:
        # Get leads that need follow-up (simplified logic)
        leads_to_follow_up = db.query(Lead).filter(
            Lead.status == "new"
        ).limit(10).all()
        
        for lead in leads_to_follow_up:
            # Send follow-up email
            send_follow_up_email.delay(lead.id)
            
            # Update lead status
            lead.status = "contacted"
            
        db.commit()
        return f"Initiated follow-up for {len(leads_to_follow_up)} leads"
        
    finally:
        db.close()


@celery_app.task
def send_follow_up_email(lead_id: int):
    """Send follow-up email to a specific lead"""
    
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return f"Lead {lead_id} not found"
        
        # Create email content
        subject = f"Follow-up: Let's discuss your needs, {lead.name}"
        body = f"""
        Hi {lead.name},

        I hope this email finds you well. I wanted to follow up on your inquiry and see how I can help you with your business needs.

        I'd love to schedule a brief call to discuss:
        - Your current challenges
        - How our automation solutions can help
        - Next steps for getting started

        Would you be available for a 15-minute call this week?

        Best regards,
        Your Automation Team
        """
        
        # In a real implementation, you would use proper email service
        # For now, we'll just log the action
        print(f"Would send email to {lead.email}: {subject}")
        
        return f"Follow-up email sent to {lead.email}"
        
    finally:
        db.close()


@celery_app.task
def send_invoice_email(invoice_id: int):
    """Send invoice via email"""
    
    # This would integrate with your email service
    # and generate/attach PDF invoices
    
    return f"Invoice {invoice_id} sent via email"


@celery_app.task
def send_payment_reminder(invoice_id: int):
    """Send payment reminder for overdue invoices"""
    
    # This would check invoice due dates and send reminders
    
    return f"Payment reminder sent for invoice {invoice_id}"
