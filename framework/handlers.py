from flask import Flask, request, jsonify
import requests
import os
import json
from pydantic_ai import Agent, RunContext
from data.structure import BasicInfo, DetailedInfo
from data.db_manager import ConversationDB, CustomerDB
from utility.email_manager import EmailManager


def send_customer_email(transcript, customer_email, email_consent, call_type="basic"):
    """
    Reusable method to send emails to customers
    
    Args:
        transcript (str): Call transcript
        customer_email (str): Customer's email address
        email_consent (bool): Whether customer consented to receive emails
        call_type (str): Type of call ("basic", "onboarding", etc.)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not customer_email:
        print("📧 No email address available for customer")
        return False
        
    if not email_consent:
        print("📧 Customer did not consent to receive emails")
        return False
    
    try:
        # Initialize EmailManager 
        email_manager = EmailManager()
        success = email_manager.send_care_email(transcript, customer_email)
        
        # For now, print what would be sent
        print(f"Would send {call_type} email to: {customer_email}")
        print(f"Email content would include transcript: {transcript[:100]}...")
        
        if success:
            print(f"✅ {call_type.capitalize()} email sent successfully to {customer_email}")
            return True
        else:
            print(f"❌ Failed to send {call_type} email to {customer_email}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending {call_type} email: {str(e)}")
        return False


def save_conversation(customer_record, customer_info, summary, transcript, recording, purpose, agent_name="Neha"):
    """
    Reusable method to save conversations to database
    
    Args:
        customer_record (dict): Existing customer record from database
        customer_info (object): Customer info object (BasicInfo or DetailedInfo)
        summary (str): Call summary
        transcript (str): Call transcript
        recording (str): Recording URL
        purpose (str): Purpose of the call
        agent_name (str): Name of the agent handling the call
    
    Returns:
        int: Conversation ID if successful, None otherwise
    """
    try:
        from data.structure import Conversation
        conversation_db = ConversationDB()
        
        # Get customer name for the conversation record
        customer_name = None
        if customer_record:
            customer_name = customer_record.get('customer_name') or customer_record.get('id')
        elif hasattr(customer_info, 'name') and customer_info.name:
            customer_name = customer_info.name
        else:
            customer_name = "Unknown Customer"
        
        # Create new conversation record (always new, never existing)
        conversation = Conversation(
            id=None,  # Will be auto-generated as new conversation
            name=customer_name,
            result="successful",
            purpose=purpose,
            agent=agent_name,
            summary=summary,
            transcript=transcript,
            recording=recording
        )
        
        conversation_id = conversation_db.add_conversation(conversation)
        print(f"✅ New {purpose} conversation saved with ID: {conversation_id}")
        return conversation_id
        
    except Exception as e:
        print(f"❌ Error saving new {purpose} conversation: {str(e)}")
        return None


def call_ended(event):
    """Handle basic info collection call ended event"""
    # Step 1: collect info
    event = request.json
    payload = event.get("message", {})
    transcript = payload.get("transcript")
    summary = payload.get("summary", "")
    recording = payload.get("recordingUrl", "")
    duration = payload.get("durationMinutes", "")
    
    print(transcript)
    print("-------------------------------------")
    print(summary)
    print("-------------------------------------")
    print(recording)
    print("-------------------------------------")
    print(duration)
    
    # Extract customer info from transcript
    agent = Agent('openai:gpt-4.1', output_type=BasicInfo)
    customer_info = agent.run_sync('read the transcript and get me information \n' + transcript)
    print(customer_info.output)
    
    # Step 2: Search for existing customer and update basic info
    customer_record = None
    try:
        basic_info = customer_info.output
        customer_db = CustomerDB()
        
        # Search for customer by name and DOB
        if hasattr(basic_info, 'name') and basic_info.name and basic_info.date_of_birth:
            # First try to find by name and DOB
            customers = customer_db.find_by_name_dob(basic_info.name, basic_info.date_of_birth)
            if customers:
                customer_record = customers[0]  # Get the first match
                print(f"Found existing customer: {customer_record.get('id')}")
        
        # If no customer found by name/DOB, try to search by email if available
        if not customer_record and hasattr(basic_info, 'email') and basic_info.email:
            customer_record = customer_db.find_by_email(basic_info.email)
        
        # Update or create customer record
        if customer_record:
            customer_id = customer_record.get('id')
            customer_db.update_basic_info(customer_id, basic_info)
            
            # Update status to "pending onboarding"
            from tinydb import Query
            customer_db.customers.update({'status': 'pending onboarding'}, Query().id == customer_id)
        else:
            print("No existing customer found, this might be a new customer")
        
        # Step 3: Send email using reusable method
        customer_email = customer_record.get('email') if customer_record else getattr(basic_info, 'email', None)
        email_consent = getattr(basic_info, 'send_him_email', False)
        send_customer_email(transcript, customer_email, email_consent, "basic info")
    
    except Exception as e:
        print(f"❌ Error processing customer info: {str(e)}")
    
    # Step 4: Save conversation using reusable method
    save_conversation(
        customer_record=customer_record,
        customer_info=customer_info.output,
        summary=summary,
        transcript=transcript,
        recording=recording,
        purpose="basic info collection",
        agent_name="Neha"
    )
    
    print(f"📞 Call ended")
    print(f"📴 Call ended. Summary: {payload.get('summary')}")
    print("📜 Full transcript:", payload.get("transcript"))


def onboarding_call_ended(event):
    """Handle detailed info collection (onboarding) call ended event"""
    # Step 1: collect info
    event = request.json
    payload = event.get("message", {})
    transcript = payload.get("transcript")
    summary = payload.get("summary", "")
    recording = payload.get("recordingUrl", "")
    duration = payload.get("durationMinutes", "")
    
    print(transcript)
    print("-------------------------------------")
    print(summary)
    print("-------------------------------------")
    print(recording)
    print("-------------------------------------")
    print(duration)
    
    # Extract detailed customer info from transcript
    agent = Agent('openai:gpt-4.1', output_type=DetailedInfo)
    detailed_customer_info = agent.run_sync('read the transcript and get me detailed information \n' + transcript)
    print(detailed_customer_info.output)
    
    # Step 2: Search for existing customer and update detailed info
    customer_record = None
    try:
        detailed_info = detailed_customer_info.output
        customer_db = CustomerDB()
        
        # Search for customer by name and DOB
        if hasattr(detailed_info, 'name') and detailed_info.name and detailed_info.date_of_birth:
            # First try to find by name and DOB
            customers = customer_db.find_by_name_dob(detailed_info.name, detailed_info.date_of_birth)
            if customers:
                customer_record = customers[0]  # Get the first match
                print(f"Found existing customer: {customer_record.get('id')}")
        
        # If no customer found by name/DOB, try to search by email if available
        if not customer_record and hasattr(detailed_info, 'email') and getattr(detailed_info, 'email', None):
            customer_record = customer_db.find_by_email(detailed_info.email)
        
        # Update customer record with detailed info
        if customer_record:
            customer_id = customer_record.get('id')
            customer_db.update_detailed_info(customer_id, detailed_info)
            
            # Update status to "onboarding complete"
            from tinydb import Query
            customer_db.customers.update({'status': 'onboarding complete'}, Query().id == customer_id)
        else:
            print("No existing customer found for onboarding call")
        
        # Step 3: Send email using reusable method
        customer_email = customer_record.get('email') if customer_record else getattr(detailed_info, 'email', None)
        email_consent = getattr(detailed_info, 'send_him_email', False)
        send_customer_email(transcript, customer_email, email_consent, "onboarding")
    
    except Exception as e:
        print(f"❌ Error processing detailed customer info: {str(e)}")
    
    # Step 4: Save conversation using reusable method
    save_conversation(
        customer_record=customer_record,
        customer_info=detailed_customer_info.output,
        summary=summary,
        transcript=transcript,
        recording=recording,
        purpose="detailed info collection / onboarding",
        agent_name="Rohan"
    )
    
    print(f"📞 Onboarding call ended")
    print(f"📴 Onboarding call ended. Summary: {payload.get('summary')}")
    print("📜 Full transcript:", payload.get("transcript"))


def tool_call(event):
    """Handle tool call events"""
    print("in tool call")
    # executed when a tool is called
    with open('test.json', 'w') as f: 
        json.dump(event, f, indent=2)
    
    event = request.json
    payload = event.get("message", {})
    event_type = payload.get("type")
    tool_name = payload.get("name")
    call_id = payload.get("call").get("id")
    tool_call_id = payload.get("toolCalls").get("id")
    args = payload.get("arguments", {})
    
    tool_response = {
        "results": [
            {
                "toolCallId": tool_name,
                "result": "Verified"
            }
        ]
    }
    return tool_response


def function_call(event):
    """Handle function call events"""
    # executed when a function is called
    print("in function call")