from flask import Flask, request, jsonify
import requests
import os
import json
from pydantic_ai import Agent, RunContext
from data.structure import BasicInfo, DetailedInfo
from data.db_manager import ConversationDB, CustomerDB
from framework.handlers import save_conversation, send_customer_email
from utility.email_manager import EmailManager


transcript= """
AI: Hi. This is Rohan from 2 care dot ai. Who do I have the pleasure of speaking with today?
User: This is StarCape.
AI: Thank you, Star Cape. To ensure we're setting up your account correctly, could you please provide your date of birth in day, month, year format?
User: 3 1 0 5 1 9 9 0.
AI: Just a sec. It seems I couldn't find your details in our system.
AI: Let me double check the information. Could you confirm your full name and date of birth again? Just to ensure accuracy?
User: Yes. So 3 1 0 5 1 9 9 0.
AI: Just a sec. It seems I couldn't locate your details in our system.
AI: It's possible you may not yet be registered. Would you like me
User: Okay. My name is Saket. Saket.
AI: Thank you, Saket. To ensure we're setting up your account correctly, could you please confirm your date of birth in day, month, year format?
User: 3 1 0 5 1 9 9 0.
AI: This will just take a sec. Perfect, Saket. I have your information here. Let me confirm.
AI: Name, Saket. Date of birth, 31 May 19 90. Main goal, coordinating care for your mother with chronic conditions. Chronic conditions, diabetes and hypertension. Allergies, unknown at this time. Consent, yes. Is that correct? Now before we dive into your specific needs, let me briefly share why 2 care day ai exists. When our founder's father was diagnosed with cancer in 2020, they struggled to coordinate his care from Germany and Ireland. They faced misdiagnoses from complex reports. Difficulty tracking vitals, and fragmented health records. Losing him left them wondering if better monitoring could have made a difference. That's why we created twocare dot ai. To make health care accessible and efficient, empowering you to manage your loved one's health from anywhere Now let's focus on your mother. What is her name?
User: Veena?
AI: Thank you, Saket. Vina is a beautiful name. What is your relationship to Vina? Are you her son? Or do you hold another role in her care?
User: No sign. Mother, it has to be son.
AI: Thank you for clarifying, Saket. Could you tell me Vina's age, and the general area where she lives? I don't need the exact address just the city or region.
User: 73 alpha.
AI: Got it, Saket. Vina is 73 years old. Could you tell me the city or region where she resides?
User: Yeah. How where's my call?
AI: Thank you for sharing For emergency situations, who would be the primary emergency contact for Vina? Please include their name, relationship to the patient, and phone number.
User: It'll be my uncle His name is Sipi. And his age is 63. Phone number is 8 4289 3.
AI: Thank you, Saket. So Sippy, your uncle, will be the primary emergency contact, and his phone number is 8 4 2 8 9 3. Now could you tell me about Vina's current health condition? What are the main health challenges she's facing?
User: It was already said that she has monitoring and all her issues of diabetes and hypertension in the last call.
AI: Thank you for clarifying, Saket. You're right. Vina's main health challenges are diabetes and hypertension. How well does she manage her medications? Does she take them consistently, or are there challenges with compliance?
User: Did mention that she forgets things, so she forgets medicine.
AI: Thank you for sharing that, Saket. Forgetting medications can be a common challenge, with conditions like diabetes and hypertension. Does Vina currently use any monitoring devices such as a blood pressure monitor, glucose meter, or other health tracking devices?
User: Sometimes.
AI: I understand it can be challenging to maintain consistent monitoring. How often do you feel Vina needs health monitoring or check ins? Would it be daily, weekly, or based on specific symptoms?
User: We
AI: It sounds like weekly monitoring might be the current approach. What kind of a does Vina need with daily activities? This could include things like meal preparation, medication reminders, mobility support, or other daily tasks.
User: Just medication reminders would be fine.
AI: Thank you, Saket. Medication reminders are an area we can assist with. Are there any lifestyle factors factors that affect Venus health? For example, diet restrictions, exercise limitations, or social isolation.
User: So she's she can't eat sugar stuff, so there's diet restriction.
AI: Got it, suck it. Vina has a diet restriction and avoids sugar due to her diabetes. Thank you for sharing these details. Based on everything you've shared Vina, I can see how to care dot a I would be incredibly valuable for your situation. Our comprehensive care package at 89 dollars per month provides 4 7 health monitoring and coordination, simplified medical report analysis and interpretation, centralized health records management, vital signs tracking with smart alerts, care coordination from anywhere in the world, direct communication with health care professionals when needed, With our annual subscription, that's just 1068 dollars for the entire year. Less than 3 dollars per day to ensure Veena receives the coordinated comprehensive care she deserves given what you've told me about her condition and needs. Would you be interested in getting started with our comprehensive package?
User: Yes. Can you send me the emails in the papers? Right?
AI: That's wonderful, Saket. I'm 2Care dot ai will make a significant difference in managing Venus care. I'll send you a detailed summary of our conversation along with all the information about getting started via email. Let me summarize what we've covered today. We've verified your identity and collected comprehensive information about Venus care needs. You've expressed interest in our comprehensive care package at 89 dollars a month. Vina's main challenges include diabetes, hypertension, and medication reminders. She has diet restrictions and occasional use of monitoring devices. Your uncle Sippy is the primary emergency contact. We'll send you the email shortly with the next steps. Thank you for trusting 2 care dot a I. We Venus Care Coordination. Is there anything else I can help clarify for you today?
User: No. That's it. Thanks.
AI: You're very welcome, Saket. Thank you for trusting 2 Character AI with Vina's care coordination. We'll make sure everything is set up smoothly. You'll receive the email shortly with all the details if you have any questions or need assistance in the future, feel free to reach out. Take care and have a wonderful day.
"""



def call_ended():
 # Step 1: collect info
    payload = {}
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
    
    
    
    
    
    
    
call_ended()