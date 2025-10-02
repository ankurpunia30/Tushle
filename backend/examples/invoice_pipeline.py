"""
Sample Invoice Automation Pipeline

This demonstrates how to create a complete automation pipeline
that generates invoices, sends them via email, and tracks payments.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from app.db.database import SessionLocal
from app.models import Client, Invoice, Task, User
from app.tasks.email_tasks import send_invoice_email, send_payment_reminder
import uuid


class InvoiceAutomationPipeline:
    """
    Complete invoice automation pipeline
    """
    
    def __init__(self):
        self.db = SessionLocal()
    
    def create_monthly_invoices(self, user_id: int):
        """
        Create monthly recurring invoices for all active clients
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            active_clients = self.db.query(Client).filter(
                Client.owner_id == user_id,
                Client.status == "active"
            ).all()
            
            created_invoices = []
            
            for client in active_clients:
                # Generate invoice number
                invoice_number = f"INV-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"
                
                # Create invoice (example: $500 monthly service)
                invoice = Invoice(
                    invoice_number=invoice_number,
                    client_id=client.id,
                    user_id=user_id,
                    amount=Decimal("500.00"),
                    status="draft",
                    due_date=datetime.now() + timedelta(days=30),
                    description=f"Monthly automation services for {datetime.now().strftime('%B %Y')}"
                )
                
                self.db.add(invoice)
                self.db.flush()  # Get the ID
                
                # Create task to send invoice
                task = Task(
                    title=f"Send invoice {invoice_number} to {client.name}",
                    description=f"Send monthly invoice to {client.email}",
                    type="invoice_send",
                    status="pending",
                    assigned_to_id=user_id,
                    metadata={
                        "invoice_id": invoice.id,
                        "client_id": client.id,
                        "automation_pipeline": "monthly_invoicing"
                    }
                )
                
                self.db.add(task)
                created_invoices.append({
                    "invoice_id": invoice.id,
                    "invoice_number": invoice_number,
                    "client_name": client.name,
                    "amount": float(invoice.amount)
                })
            
            self.db.commit()
            
            # Schedule email sending
            for invoice_info in created_invoices:
                send_invoice_email.delay(invoice_info["invoice_id"])
            
            return {
                "success": True,
                "created_invoices": len(created_invoices),
                "invoices": created_invoices
            }
            
        except Exception as e:
            self.db.rollback()
            return {"error": str(e)}
        
        finally:
            self.db.close()
    
    def process_overdue_invoices(self):
        """
        Find overdue invoices and send payment reminders
        """
        try:
            overdue_invoices = self.db.query(Invoice).filter(
                Invoice.status.in_(["sent", "overdue"]),
                Invoice.due_date < datetime.now()
            ).all()
            
            reminders_sent = 0
            
            for invoice in overdue_invoices:
                # Update status to overdue
                if invoice.status != "overdue":
                    invoice.status = "overdue"
                
                # Send payment reminder
                send_payment_reminder.delay(invoice.id)
                reminders_sent += 1
                
                # Create follow-up task
                task = Task(
                    title=f"Follow up on overdue invoice {invoice.invoice_number}",
                    description=f"Invoice is {(datetime.now() - invoice.due_date).days} days overdue",
                    type="payment_follow_up",
                    status="pending",
                    priority="high",
                    assigned_to_id=invoice.user_id,
                    metadata={
                        "invoice_id": invoice.id,
                        "days_overdue": (datetime.now() - invoice.due_date).days
                    }
                )
                
                self.db.add(task)
            
            self.db.commit()
            
            return {
                "success": True,
                "overdue_invoices": len(overdue_invoices),
                "reminders_sent": reminders_sent
            }
            
        except Exception as e:
            self.db.rollback()
            return {"error": str(e)}
        
        finally:
            self.db.close()


# Example usage and pipeline execution
def run_invoice_automation():
    """
    Main pipeline execution function
    """
    pipeline = InvoiceAutomationPipeline()
    
    # Example: Create monthly invoices for user ID 1
    monthly_result = pipeline.create_monthly_invoices(user_id=1)
    print("Monthly invoices created:", monthly_result)
    
    # Process overdue invoices
    overdue_result = pipeline.process_overdue_invoices()
    print("Overdue invoices processed:", overdue_result)


if __name__ == "__main__":
    run_invoice_automation()
