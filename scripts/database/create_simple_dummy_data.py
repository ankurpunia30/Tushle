#!/usr/bin/env python3
"""
Script to add dummy employees and sample data for testing the performance dashboard
"""

import sys
import os
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Add the backend directory to the Python path
sys.path.append('/Users/ankur/cses/lehar/backend')

from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal
from app.models import User, Task, Lead, Client, Meeting, EmployeePerformance
from app.core.security import get_password_hash

def create_dummy_data():
    print("🚀 Starting dummy data creation...")
    db = SessionLocal()
    
    try:
        # Check if dummy employees already exist
        existing_employees = db.query(User).filter(User.email.like('%example.com')).all()
        if existing_employees:
            print(f"Found {len(existing_employees)} existing dummy employees. Clearing them first...")
            for emp in existing_employees:
                db.delete(emp)
            db.commit()
        
        print("Creating dummy employees...")
        # Create dummy employees
        employees_data = [
            {
                "email": "sarah.johnson@example.com",
                "full_name": "Sarah Johnson",
                "role": "employee"
            },
            {
                "email": "mike.chen@example.com", 
                "full_name": "Mike Chen",
                "role": "employee"
            },
            {
                "email": "emily.davis@example.com",
                "full_name": "Emily Davis", 
                "role": "employee"
            }
        ]
        
        employees = []
        for emp_data in employees_data:
            employee = User(
                email=emp_data["email"],
                hashed_password=get_password_hash("password123"),
                full_name=emp_data["full_name"],
                role=emp_data["role"],
                is_active=True,
                created_at=datetime.now() - timedelta(days=90)
            )
            db.add(employee)
            employees.append(employee)
        
        db.commit()
        
        # Refresh to get IDs
        for employee in employees:
            db.refresh(employee)
        
        print(f"✅ Created {len(employees)} dummy employees")
        
        # Create dummy clients
        print("Creating dummy clients...")
        clients_data = [
            {"name": "John Smith", "email": "john@techstartup.com", "company": "Tech Startup Inc", "phone": "555-0101"},
            {"name": "Lisa Wang", "email": "lisa@marketingpro.com", "company": "Marketing Pro LLC", "phone": "555-0102"},
            {"name": "Robert Brown", "email": "robert@retailchain.com", "company": "Retail Chain Corp", "phone": "555-0103"},
            {"name": "Maria Garcia", "email": "maria@consulting.com", "company": "Garcia Consulting", "phone": "555-0104"},
            {"name": "David Wilson", "email": "david@healthtech.com", "company": "HealthTech Solutions", "phone": "555-0105"},
        ]
        
        clients = []
        for client_data in clients_data:
            client = Client(
                name=client_data["name"],
                email=client_data["email"],
                company=client_data["company"],
                phone=client_data["phone"],
                status=random.choice(["active", "pending", "completed"]),
                owner_id=random.choice(employees).id,
                created_at=datetime.now() - timedelta(days=random.randint(30, 90))
            )
            db.add(client)
            clients.append(client)
        
        db.commit()
        print(f"✅ Created {len(clients)} dummy clients")
        
        print("✅ Successfully created dummy data:")
        print(f"   - 3 Employees: {', '.join([emp.full_name for emp in employees])}")
        print(f"   - {len(clients)} Clients")
        
    except Exception as e:
        print(f"❌ Error creating dummy data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_dummy_data()
    print("🎉 Done! You can now view the performance dashboard with sample data.")
