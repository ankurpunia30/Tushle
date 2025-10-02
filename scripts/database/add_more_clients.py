#!/usr/bin/env python3

import sqlite3
from datetime import datetime, timedelta
import random

# Sample client data for testing pagination
clients_data = [
    ("Acme Corporation", "contact@acme.com", "+1-555-0101", "Acme Corporation", "active", "onboarding"),
    ("Tech Solutions Ltd", "info@techsolutions.com", "+1-555-0102", "Tech Solutions Ltd", "pending", "initial"),
    ("Global Marketing Inc", "hello@globalmarketing.com", "+1-555-0103", "Global Marketing Inc", "active", "content_creation"),
    ("Digital Agency Pro", "team@digitalagency.com", "+1-555-0104", "Digital Agency Pro", "completed", "completed"),
    ("StartupBoost Co", "founders@startupboost.com", "+1-555-0105", "StartupBoost Co", "active", "strategy"),
    ("Enterprise Solutions", "business@enterprise.com", "+1-555-0106", "Enterprise Solutions", "active", "execution"),
    ("Creative Studios", "creative@studios.com", "+1-555-0107", "Creative Studios", "pending", "proposal"),
    ("E-commerce Plus", "shop@ecommerceplus.com", "+1-555-0108", "E-commerce Plus", "active", "onboarding"),
    ("FinTech Innovations", "contact@fintech.com", "+1-555-0109", "FinTech Innovations", "active", "content_creation"),
    ("HealthCare Systems", "info@healthcare.com", "+1-555-0110", "HealthCare Systems", "pending", "initial"),
    ("Education First", "admin@educationfirst.com", "+1-555-0111", "Education First", "completed", "completed"),
    ("Real Estate Group", "sales@realestate.com", "+1-555-0112", "Real Estate Group", "active", "strategy"),
    ("Food & Beverage Co", "orders@foodbev.com", "+1-555-0113", "Food & Beverage Co", "active", "execution"),
    ("Fashion Forward", "style@fashionforward.com", "+1-555-0114", "Fashion Forward", "pending", "proposal"),
    ("Auto Dealers United", "cars@autodealers.com", "+1-555-0115", "Auto Dealers United", "active", "onboarding"),
    ("Travel Adventures", "book@traveladventures.com", "+1-555-0116", "Travel Adventures", "active", "content_creation"),
    ("Sports Equipment Pro", "gear@sportspro.com", "+1-555-0117", "Sports Equipment Pro", "completed", "completed"),
    ("Home Improvement", "build@homeimprovement.com", "+1-555-0118", "Home Improvement", "active", "strategy"),
    ("Legal Services LLC", "law@legalservices.com", "+1-555-0119", "Legal Services LLC", "pending", "initial"),
    ("Consulting Group", "consult@consultinggroup.com", "+1-555-0120", "Consulting Group", "active", "execution"),
]

def add_clients():
    # Connect to database
    conn = sqlite3.connect('automation_dashboard.db')
    cursor = conn.cursor()
    
    # Assume user ID 1 is the main user
    user_id = 1
    
    # Add clients
    for name, email, phone, company, status, onboarding_stage in clients_data:
        # Check if client already exists
        cursor.execute("SELECT id FROM clients WHERE email = ?", (email,))
        if cursor.fetchone():
            print(f"Client with email {email} already exists, skipping...")
            continue
            
        # Create random date within last 6 months
        created_date = datetime.now() - timedelta(days=random.randint(1, 180))
        
        cursor.execute("""
            INSERT INTO clients (name, email, phone, company, status, onboarding_stage, owner_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, company, status, onboarding_stage, user_id, created_date, created_date))
        
        print(f"Added client: {name}")
    
    conn.commit()
    conn.close()
    print(f"\nAdded {len(clients_data)} clients for testing pagination!")

if __name__ == "__main__":
    add_clients()
