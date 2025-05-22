from pydantic import BaseModel, Field
from typing import Optional
from tinydb import TinyDB, Query
from uuid import uuid4
from datetime import datetime
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
import os

from data.structure import BasicInfo, Conversation, Customer, DetailedInfo
from run_server import db_customer, db_conversation




class CustomerDB:
    def __init__(self):
        self.db = db_customer
        self.customers = self.db.table('customers')
        print(f"Database initialized")
    
    def add_customer(self, customer: Customer):
        """Add a new customer or update existing one"""
        # Generate ID if not provided
        if not customer.id:
            customer.id = f"CUST-{uuid4().hex[:8].upper()}"
        
        # Add timestamps
        now = datetime.now().isoformat()
        if not customer.created_at:
            customer.created_at = now
        customer.updated_at = now
        
        # Convert to dict using appropriate method for Pydantic version
        try:
            # Try Pydantic v2 method first
            data = customer.model_dump()
        except AttributeError:
            # Fall back to Pydantic v1 method
            data = customer.dict()
        
        # Save to database
        self.customers.upsert(data, Query().id == customer.id)
        print(f"Customer saved with ID: {customer.id}")
        return customer.id
    
    def get_customer(self, customer_id):
        """Get a customer by ID"""
        customer = self.customers.get(Query().id == customer_id)
        if customer:
            print(f"Found customer: {customer.get('customer_name', 'Unknown')}")
        else:
            print(f"Customer with ID {customer_id} not found")
        return customer
    
    def update_basic_info(self, customer_id, basic_info: BasicInfo):
        """Update a customer with basic info data"""
        # Check if customer exists
        customer = self.get_customer(customer_id)
        if not customer:
            print(f"Customer with ID {customer_id} not found. Creating a new record.")
            # Create a new customer record
            new_customer = Customer(
                id=customer_id,
                status="pending",
                email="unknown@example.com",
                phone="unknown",
                date_of_birth="unknown"
            )
            self.add_customer(new_customer)
        
        # Convert basic_info to dict
        try:
            # Try Pydantic v2 method first
            data = basic_info.model_dump(exclude_unset=True)
        except AttributeError:
            # Fall back to Pydantic v1 method
            data = basic_info.dict(exclude_unset=True)
        
        # Add updated timestamp
        data["updated_at"] = datetime.now().isoformat()
        
        # Update the customer record
        self.customers.update(data, Query().id == customer_id)
        print(f"Updated basic info for customer {customer_id}")
        
        return customer_id
    
    def update_detailed_info(self, customer_id, detailed_info: DetailedInfo):
        """Update a customer with detailed info data"""
        # Check if customer exists
        customer = self.get_customer(customer_id)
        if not customer:
            print(f"Customer with ID {customer_id} not found. Creating a new record.")
            # Create a new customer record
            new_customer = Customer(
                id=customer_id,
                status="pending",
                email="unknown@example.com",
                phone="unknown",
                date_of_birth="unknown"
            )
            self.add_customer(new_customer)
        
        # Convert detailed_info to dict
        try:
            # Try Pydantic v2 method first
            data = detailed_info.model_dump(exclude_unset=True)
        except AttributeError:
            # Fall back to Pydantic v1 method
            data = detailed_info.dict(exclude_unset=True)
        
        # Add updated timestamp
        data["updated_at"] = datetime.now().isoformat()
        
        # Update the customer record
        self.customers.update(data, Query().id == customer_id)
        print(f"Updated detailed info for customer {customer_id}")
        
        return customer_id
    
    def find_by_email(self, email):
        """Find customer by email address"""
        User = Query()
        customer = self.customers.get(User.email == email)
        if customer:
            print(f"Found customer by email: {customer.get('customer_name', 'Unknown')}")
        else:
            print(f"No customer found with email: {email}")
        return customer

    def find_by_name_dob(self, name, dob):
        """Find customers by name and date of birth"""
        User = Query()
        customers = self.customers.search(
            (User.customer_name == name) & (User.date_of_birth == dob)
        )
        print(f"Found {len(customers)} customers matching name:{name}, DOB:{dob}")
        return customers
    
    def find_by_email_and_dob(self, email, dob):
        """Find customer by email and date of birth"""
        User = Query()
        customer = self.customers.get(
            (User.email == email) & (User.date_of_birth == dob)
        )
        if customer:
            print(f"Found customer by email and DOB: {customer.get('customer_name', 'Unknown')}")
        else:
            print(f"No customer found with email: {email} and DOB: {dob}")
        return customer
        


class ConversationDB:
    def __init__(self):
      
        self.db = db_conversation
        self.conversations = self.db.table('conversations')
        print(f"Conversation database initialized")
    
    def add_conversation(self, conversation: Conversation):
        """Add a new conversation with auto-incrementing ID"""
        # If ID is not provided, generate the next available ID
        if conversation.id is None:
            # Get all existing IDs
            all_ids = [item.get('id', 0) for item in self.conversations.all()]
            # Find the maximum ID and add 1, or start at 1 if no records exist
            next_id = max(all_ids, default=0) + 1
            conversation.id = next_id
        
        # Convert to dict
        try:
            # Try Pydantic v2 method first
            data = conversation.model_dump()
        except AttributeError:
            # Fall back to Pydantic v1 method
            data = conversation.dict()
        
        # Save to database
        self.conversations.upsert(data, Query().id == conversation.id)
        print(f"Conversation saved with ID: {conversation.id}")
        return conversation.id
    
    def get_conversation(self, conversation_id):
        """Get a conversation by ID"""
        return self.conversations.get(Query().id == conversation_id)
    
    def get_customer_conversations(self, customer_name):
        """Get all conversations for a customer by name"""
        return self.conversations.search(Query().name == customer_name)

