from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="employee")  # admin, employee
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    invoices = relationship("Invoice", back_populates="user")
    clients = relationship("Client", back_populates="owner")
    assigned_tasks = relationship("Task", back_populates="assigned_to", foreign_keys="Task.assigned_to_id")
    created_tasks = relationship("Task", back_populates="created_by", foreign_keys="Task.created_by_id")
    assigned_leads = relationship("Lead", back_populates="assigned_to", foreign_keys="Lead.assigned_to_id")
    created_leads = relationship("Lead", back_populates="created_by", foreign_keys="Lead.created_by_id")


class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    company = Column(String)
    status = Column(String, default="pending")  # pending, active, completed, inactive, portal_submitted
    onboarding_stage = Column(String, default="initial")  # initial, requirements_submitted, proposal_sent, contract_signed, project_started, completed
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="clients")
    invoices = relationship("Invoice", back_populates="client")
    reports = relationship("Report", back_populates="client")
    portal_submissions = relationship("PortalSubmission", back_populates="client")


class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="draft")  # draft, sent, paid, overdue
    due_date = Column(DateTime)
    paid_date = Column(DateTime)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="invoices")
    user = relationship("User", back_populates="invoices")


class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    company = Column(String)
    source = Column(String)  # website, referral, social, cold_outreach, etc.
    status = Column(String, default="new")  # new, contacted, qualified, proposal_sent, converted, lost
    priority = Column(String, default="medium")  # low, medium, high, urgent
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    estimated_value = Column(Numeric(10, 2))  # Estimated deal value
    notes = Column(Text)
    last_contact_date = Column(DateTime)
    next_follow_up_date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assigned_to = relationship("User", back_populates="assigned_leads", foreign_keys=[assigned_to_id])
    created_by = relationship("User", back_populates="created_leads", foreign_keys=[created_by_id])


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String)  # invoice, follow_up, content_creation, lead_generation, client_onboarding, etc.
    status = Column(String, default="todo")  # todo, in_progress, review, completed, blocked
    priority = Column(String, default="medium")  # low, medium, high, urgent
    due_date = Column(DateTime)
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)  # Optional client association
    estimated_hours = Column(Numeric(5, 2))  # Estimated time in hours
    actual_hours = Column(Numeric(5, 2))  # Actual time spent
    task_metadata = Column(JSON)  # Additional task-specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assigned_to = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to_id])
    created_by = relationship("User", back_populates="created_tasks", foreign_keys=[created_by_id])
    client = relationship("Client")


class ContentPost(Base):
    __tablename__ = "content_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    platform = Column(String)  # twitter, youtube, reddit, etc.
    status = Column(String, default="draft")  # draft, scheduled, published, failed
    scheduled_for = Column(DateTime)
    published_at = Column(DateTime)
    engagement_data = Column(JSON)
    ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type = Column(String)  # client_report, performance, financial, etc.
    client_id = Column(Integer, ForeignKey("clients.id"))
    data = Column(JSON)
    file_path = Column(String)  # Path to generated PDF
    status = Column(String, default="generating")  # generating, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="reports")


class AIScript(Base):
    __tablename__ = "ai_scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    script_content = Column(Text)
    video_style = Column(String)
    target_duration = Column(Integer)  # in seconds
    status = Column(String, default="draft")  # draft, generated, video_created
    script_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Pipeline(Base):
    __tablename__ = "pipelines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    config = Column(JSON)
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PortalSubmission(Base):
    __tablename__ = "portal_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    project_requirements = Column(Text, nullable=False)
    budget_range = Column(String, nullable=False)
    timeline = Column(String, nullable=False)
    additional_info = Column(Text)
    preferred_contact_method = Column(String, default="email")
    urgency_level = Column(String, default="medium")
    status = Column(String, default="new")  # new, reviewed, proposal_sent, follow_up_needed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="portal_submissions")


class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    meeting_type = Column(String, default="general")  # general, client_call, team_meeting, follow_up
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String)  # physical location or meeting link
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled, rescheduled
    calendar_event_id = Column(String)  # For integration with Google Calendar, Outlook, etc.
    attendees = Column(JSON)  # List of email addresses
    meeting_notes = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    client = relationship("Client")
    lead = relationship("Lead")


class EmployeePerformance(Base):
    __tablename__ = "employee_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"))
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Task Performance Metrics
    total_tasks_assigned = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    tasks_overdue = Column(Integer, default=0)
    avg_task_completion_time = Column(Numeric(8, 2))  # in hours
    total_estimated_hours = Column(Numeric(10, 2), default=0)
    total_actual_hours = Column(Numeric(10, 2), default=0)
    
    # Lead Performance Metrics
    leads_assigned = Column(Integer, default=0)
    leads_contacted = Column(Integer, default=0)
    leads_qualified = Column(Integer, default=0)
    leads_converted = Column(Integer, default=0)
    total_estimated_deal_value = Column(Numeric(12, 2), default=0)
    total_actual_deal_value = Column(Numeric(12, 2), default=0)
    
    # Meeting Performance Metrics
    meetings_scheduled = Column(Integer, default=0)
    meetings_completed = Column(Integer, default=0)
    meetings_no_show = Column(Integer, default=0)
    
    # Client Management Metrics
    clients_managed = Column(Integer, default=0)
    client_satisfaction_score = Column(Numeric(3, 2))  # 0.00 to 5.00
    
    # Overall Performance Score (calculated)
    performance_score = Column(Numeric(5, 2))  # 0.00 to 100.00
    rating = Column(String)  # excellent, good, satisfactory, needs_improvement, poor
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employee = relationship("User")
