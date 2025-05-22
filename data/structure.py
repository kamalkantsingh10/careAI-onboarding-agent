from pydantic import BaseModel, Field
from typing import Optional
from tinydb import TinyDB, Query
from uuid import uuid4
from datetime import datetime
import os



# 1. Define models with all fields and descriptions
class BasicInfo(BaseModel):
    name:Optional[str] = Field(None, description="Name of the Customer that was verified")
    date_of_birth: str = Field(..., description="Date of Birth of customer (DOB) in ddmmyyyy format")
    main_goal: Optional[str] = Field(None, description="What is the main goal of the customer")
    chronic_conditions: Optional[str] = Field(None, description="Patient details: Chronic Conditions of that the customer wants to care for")
    recent_hospitalizations: Optional[str] = Field(None, description="Patient details: Recent Hospitalizations or Doctor Visits")
    allergies: Optional[str] = Field(None, description="Patient details: Allergies")
    current_medications: Optional[str] = Field(None, description="Notes about Current Medications (Name/Dose/Frequency)")
    medical_devices: Optional[str] = Field(None, description="Medical Devices in use for managing condition of the patients")
    mental_health_status: Optional[str] = Field(None, description="Notes on Mental Health Status of patient")
    consent: Optional[str] = Field(None, description="Did customer provided his consent for Monitoring and data handling: Yes/No")
    send_him_email:Optional[bool] = Field(None, description="Did we agree to send him email?")

class DetailedInfo(BaseModel):
    name:Optional[str] = Field(None, description="Name of the Customer that was verified")
    date_of_birth: str = Field(..., description="Date of Birth of customer (DOB) in ddmmyyyy format")
    patient_name: Optional[str] = Field(None, description="Patient Name")
    relationship_to_customer: Optional[str] = Field(None, description="What is customer's relationship to the patient. E.g., Father, Mother, Wife, Husband etc.")
    age: Optional[int] = Field(None, description="Age of Patient in years")
    address: Optional[str] = Field(None, description="Address where the patient lives. Not exact.. on high level")
    emergency_contact: Optional[str] = Field(None, description="Emergency Contact (Name/Relation/Phone) for the patient")
    condition_details: Optional[str] = Field(None, description="What is the Condition of patient")
    medication_compliance: Optional[str] = Field(None, description="How compliant is patient with medication")
    monitoring_devices: Optional[str] = Field(None, description="Monitoring Devices that the patient uses")
    monitoring_frequency: Optional[str] = Field(None, description="Monitoring Frequency needed for the patient")
    daily_assistance: Optional[str] = Field(None, description="Assistance needed by patient with Daily Activities")
    lifestyle_factors: Optional[str] = Field(None, description="Lifestyle Factors of the patient")
    interested_in_2care: Optional[str] = Field(None, description="Did customer show interest in 2care paid packages")
    notes: Optional[str] = Field(None, description="Additional details like Notes/Urgent Flags/Info")
    send_him_email:Optional[bool] = Field(None, description="Did we agree to send him email?")

class Customer(BaseModel):
    # Auto-generated ID field
    id: Optional[str] = Field(None, description="Unique customer identifier")
    
    # Fields from customer_identification
    status: str = Field(..., description="Status of onboarding")
    email: str = Field(..., description="Email of customer")
    phone: str = Field(..., description="Phone number of customer")
    customer_name: Optional[str] = Field(None, description="Customer name")
    date_of_birth: str = Field(..., description="Date of Birth of customer (DOB)")
    
    # Fields from BasicInfo
    main_goal: Optional[str] = Field(None, description="What is the main goal of the customer")
    chronic_conditions: Optional[str] = Field(None, description="Patient details: Chronic Conditions of that the customer wants to care for")
    recent_hospitalizations: Optional[str] = Field(None, description="Patient details: Recent Hospitalizations or Doctor Visits")
    allergies: Optional[str] = Field(None, description="Patient details: Allergies")
    current_medications: Optional[str] = Field(None, description="Notes about Current Medications (Name/Dose/Frequency)")
    medical_devices: Optional[str] = Field(None, description="Medical Devices in use for managing condition of the patients")
    mental_health_status: Optional[str] = Field(None, description="Notes on Mental Health Status of patient")
    consent: Optional[str] = Field(None, description="Did customer provided his consent for Monitoring and data handling: Yes/No")
    
    # Fields from DetailedInfo
    patient_name: Optional[str] = Field(None, description="Patient Name")
    relationship_to_customer: Optional[str] = Field(None, description="What is customer's relationship to the patient. E.g., Father, Mother, Wife, Husband etc.")
    age: Optional[int] = Field(None, description="Age of Patient in years")
    address: Optional[str] = Field(None, description="Address where the patient lives. Not exact.. on high level")
    emergency_contact: Optional[str] = Field(None, description="Emergency Contact (Name/Relation/Phone) for the patient")
    condition_details: Optional[str] = Field(None, description="What is the Condition of patient")
    medication_compliance: Optional[str] = Field(None, description="How compliant is patient with medication")
    monitoring_devices: Optional[str] = Field(None, description="Monitoring Devices that the patient uses")
    monitoring_frequency: Optional[str] = Field(None, description="Monitoring Frequency needed for the patient")
    daily_assistance: Optional[str] = Field(None, description="Assistance needed by patient with Daily Activities")
    lifestyle_factors: Optional[str] = Field(None, description="Lifestyle Factors of the patient")
    interested_in_2care: Optional[str] = Field(None, description="Did customer show interest in 2care paid packages")
    notes: Optional[str] = Field(None, description="Additional details like Notes/Urgent Flags/Info")
    
    # Additional metadata fields
    created_at: Optional[str] = Field(None, description="When this record was created")
    updated_at: Optional[str] = Field(None, description="When this record was last updated")

class Conversation(BaseModel):
    id: Optional[int] = Field(None, description="Unique conversation ID")
    name: Optional[str] = Field(None, description="customer id")
    result: Optional[str] = Field(None, description="was this successful or did it fail")
    purpose: Optional[str] = Field(None, description="why was this call made")
    agent: Optional[str] = Field(None, description="name of the agent")
    summary: Optional[str] = Field(None, description="summary of what was discussed")
    transcript: Optional[str] = Field(None, description="full transcripts")
    recording: Optional[str] = Field(None, description="recording url")
