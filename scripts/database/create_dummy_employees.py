#!/usr/bin/env python3
"""
Script to create dummy employees and sample tasks for testing the task management system
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the backend directory to the Python path
sys.path.append('/Users/ankur/cses/lehar/backend')

from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal
from app.models import User, Task, Client
from app.core.security import get_password_hash

def create_dummy_employees_and_tasks():
    print("🚀 Creating dummy employees and tasks...")
    db = SessionLocal()
    
    try:
        # Check if dummy employees already exist
        existing_employees = db.query(User).filter(User.email.like('%company.com')).all()
        if existing_employees:
            print(f"Found {len(existing_employees)} existing dummy employees. Clearing them first...")
            # Delete existing tasks assigned to dummy employees
            for emp in existing_employees:
                existing_tasks = db.query(Task).filter(Task.assigned_to_id == emp.id).all()
                for task in existing_tasks:
                    db.delete(task)
                db.delete(emp)
            db.commit()
        
        print("Creating dummy employees...")
        
        # Create admin user if doesn't exist
        admin_user = db.query(User).filter(User.email == "admin@company.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@company.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin Manager",
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.flush()
            print("✅ Created admin user: admin@company.com (password: admin123)")
        
        # Create dummy employees
        employees_data = [
            {
                "email": "sarah.johnson@company.com",
                "full_name": "Sarah Johnson",
                "role": "employee",
                "password": "employee123"
            },
            {
                "email": "mike.chen@company.com", 
                "full_name": "Mike Chen",
                "role": "employee",
                "password": "employee123"
            },
            {
                "email": "emily.davis@company.com",
                "full_name": "Emily Davis", 
                "role": "employee",
                "password": "employee123"
            },
            {
                "email": "james.wilson@company.com",
                "full_name": "James Wilson",
                "role": "employee", 
                "password": "employee123"
            },
            {
                "email": "lisa.brown@company.com",
                "full_name": "Lisa Brown",
                "role": "employee",
                "password": "employee123"
            }
        ]
        
        employees = []
        for emp_data in employees_data:
            employee = User(
                email=emp_data["email"],
                hashed_password=get_password_hash(emp_data["password"]),
                full_name=emp_data["full_name"],
                role=emp_data["role"],
                is_active=True
            )
            db.add(employee)
            db.flush()  # Get the ID
            employees.append(employee)
            print(f"✅ Created employee: {emp_data['full_name']} ({emp_data['email']})")
        
        # Create some dummy clients for task assignment
        print("Creating dummy clients...")
        clients_data = [
            {"name": "TechCorp Solutions", "email": "contact@techcorp.com", "company": "TechCorp Solutions"},
            {"name": "Marketing Pro Agency", "email": "hello@marketingpro.com", "company": "Marketing Pro Agency"},
            {"name": "StartupXYZ", "email": "founder@startupxyz.com", "company": "StartupXYZ"},
        ]
        
        clients = []
        for client_data in clients_data:
            # Check if client already exists
            existing_client = db.query(Client).filter(Client.email == client_data["email"]).first()
            if not existing_client:
                client = Client(
                    name=client_data["name"],
                    email=client_data["email"],
                    company=client_data["company"],
                    status="active",
                    owner_id=admin_user.id
                )
                db.add(client)
                db.flush()
                clients.append(client)
                print(f"✅ Created client: {client_data['name']}")
            else:
                clients.append(existing_client)
        
        # Create sample tasks
        print("Creating sample tasks...")
        task_templates = [
            {
                "title": "Design new homepage mockup",
                "description": "Create wireframes and high-fidelity mockups for the new company homepage. Include mobile and desktop versions.",
                "type": "design",
                "priority": "high",
                "estimated_hours": 8.0,
                "days_from_now": 7
            },
            {
                "title": "Implement user authentication system", 
                "description": "Develop secure login/logout functionality with JWT tokens and password reset capabilities.",
                "type": "development",
                "priority": "high",
                "estimated_hours": 12.0,
                "days_from_now": 14
            },
            {
                "title": "Create social media content calendar",
                "description": "Plan and schedule social media posts for the next month across LinkedIn, Twitter, and Instagram.",
                "type": "marketing",
                "priority": "medium",
                "estimated_hours": 4.0,
                "days_from_now": 5
            },
            {
                "title": "Conduct client onboarding call",
                "description": "Schedule and conduct onboarding call with new client to understand requirements and project scope.",
                "type": "client_onboarding",
                "priority": "high",
                "estimated_hours": 2.0,
                "days_from_now": 3
            },
            {
                "title": "Write technical documentation",
                "description": "Document the new API endpoints and create developer guide for the authentication system.",
                "type": "documentation",
                "priority": "medium",
                "estimated_hours": 6.0,
                "days_from_now": 10
            },
            {
                "title": "Perform website security audit",
                "description": "Review codebase for security vulnerabilities and implement necessary fixes.",
                "type": "security",
                "priority": "urgent",
                "estimated_hours": 8.0,
                "days_from_now": 2
            },
            {
                "title": "Set up automated backup system",
                "description": "Configure daily database backups and test restore procedures.",
                "type": "infrastructure",
                "priority": "medium",
                "estimated_hours": 4.0,
                "days_from_now": 12
            },
            {
                "title": "Create email marketing campaign",
                "description": "Design and implement email marketing campaign for product launch announcement.",
                "type": "marketing",
                "priority": "high",
                "estimated_hours": 6.0,
                "days_from_now": 8
            },
            {
                "title": "Optimize database queries",
                "description": "Review and optimize slow database queries to improve application performance.",
                "type": "optimization",
                "priority": "medium",
                "estimated_hours": 5.0,
                "days_from_now": 15
            },
            {
                "title": "Prepare monthly client report",
                "description": "Compile performance metrics and create detailed report for client presentation.",
                "type": "reporting",
                "priority": "medium",
                "estimated_hours": 3.0,
                "days_from_now": 6
            }
        ]
        
        # Create tasks with random assignments
        statuses = ["todo", "in_progress", "review", "completed"]
        
        for i, task_template in enumerate(task_templates):
            # Assign to random employee
            assigned_employee = random.choice(employees)
            
            # Assign to random client (50% chance)
            assigned_client = random.choice(clients) if random.random() > 0.5 else None
            
            # Random status (favor non-completed for demo)
            status_weights = [0.4, 0.3, 0.2, 0.1]  # todo, in_progress, review, completed
            status = random.choices(statuses, weights=status_weights)[0]
            
            # Calculate due date
            due_date = datetime.now() + timedelta(days=task_template["days_from_now"])
            
            # Add some actual hours if task is in progress or completed
            actual_hours = None
            if status in ["in_progress", "review", "completed"]:
                actual_hours = round(random.uniform(0.5, task_template["estimated_hours"] * 1.2), 1)
            
            task = Task(
                title=task_template["title"],
                description=task_template["description"],
                type=task_template["type"],
                status=status,
                priority=task_template["priority"],
                due_date=due_date,
                assigned_to_id=assigned_employee.id,
                created_by_id=admin_user.id,
                client_id=assigned_client.id if assigned_client else None,
                estimated_hours=task_template["estimated_hours"],
                actual_hours=actual_hours
            )
            
            db.add(task)
            print(f"✅ Created task: {task_template['title']} → {assigned_employee.full_name} ({status})")
        
        db.commit()
        
        print("\n🎉 Successfully created dummy data!")
        print("\n📊 Summary:")
        print(f"   • 1 Admin user (admin@company.com / admin123)")
        print(f"   • {len(employees)} Employee users (password: employee123)")
        print(f"   • {len(clients)} Clients")
        print(f"   • {len(task_templates)} Tasks")
        
        print("\n👥 Employee Login Credentials:")
        for emp in employees:
            print(f"   • {emp.full_name}: {emp.email} / employee123")
        
        print("\n🚀 You can now:")
        print("   1. Login as admin to create and assign tasks")
        print("   2. Login as any employee to view and update assigned tasks")
        print("   3. Test the task management system!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = create_dummy_employees_and_tasks()
    if success:
        print("\n✅ Dummy data creation completed successfully!")
    else:
        print("\n❌ Dummy data creation failed!")
        sys.exit(1)
