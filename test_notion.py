from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from notion_client import Client
from data.db_manager import ConversationDB, CustomerDB
from data.notion_connecter import NotionConnection
from data.save_conversations import NotionConversationSync
from data.structure import Conversation,Customer,DetailedInfo,BasicInfo
from data.customer_manager import CustomerManager


def example_usage():
    # Create a manager
    print("\n=== Customer Database Example ===\n")
    
    # Initialize database
    db = CustomerDB()
    
    # Create a new customer
    customer = Customer(
        status="active",
        email="maria.silva@example.com",
        phone="+352-661-123-456",
        customer_name="Maria Silva",
        date_of_birth="1980-03-25"
    )
    
    # Save the customer
    customer_id = db.add_customer(customer)
    print(f"Created customer with ID: {customer_id}")
    
    # Add basic info
    basic_info = BasicInfo(
        main_goal="Manage arthritis pain",
        chronic_conditions="Rheumatoid Arthritis",
        allergies="Sulfa drugs",
        current_medications="Methotrexate 10mg weekly, Prednisone 5mg daily",
        consent="Yes"
    )
    
    # Update with basic info
    db.update_basic_info(customer_id, basic_info)
    
    # Add detailed info
    detailed_info = DetailedInfo(
        patient_name="Luis Silva",
        relationship_to_customer="Husband", 
        age=72,
        address="Esch-sur-Alzette",
        emergency_contact="Maria Silva (Wife) / +352-661-123-456",
        condition_details="Parkinson's Disease diagnosed 3 years ago",
        interested_in_2care="Yes, Standard Package"
    )
    
    # Update with detailed info
    db.update_detailed_info(customer_id, detailed_info)
    
    # Find by name and DOB
    customers = db.find_by_name_dob("Maria Silva", "1980-03-25")
    
    # Get complete customer record
    complete_record = db.get_customer(customer_id)
    if complete_record:
        print("\nComplete customer record:")
        print(f"ID: {complete_record['id']}")
        print(f"Name: {complete_record['customer_name']}")
        print(f"Patient name: {complete_record.get('patient_name', 'N/A')}")
        print(f"Main goal: {complete_record.get('main_goal', 'N/A')}")
        print(f"Interested in 2care: {complete_record.get('interested_in_2care', 'N/A')}")
    
    print("\n=== Conversation Database Example ===\n")
    
    # Initialize conversation database
    conv_db = ConversationDB()
    
    # Create a new conversation
    conversation = Conversation(
        name=customer_id,  # Associate with the customer ID
        result="success",
        purpose="follow-up on order",
        agent="Sarah",
        summary="Customer inquired about healthcare options. Provided details on 2care packages.",
        transcript="Full conversation text...",
        recording="https://recordings.example.com/call123.mp3"
    )
    
    # Save the conversation
    conv_id = conv_db.add_conversation(conversation)
    print(f"Created conversation with ID: {conv_id}")
    
    # Get the conversation
    conv = conv_db.get_conversation(conv_id)
    if conv:
        print(f"Conversation purpose: {conv['purpose']}")
        print(f"Conversation summary: {conv['summary']}")



if __name__ == "__main__":
    example_usage()

