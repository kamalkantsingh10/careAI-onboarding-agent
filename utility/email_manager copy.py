from pydantic import BaseModel, Field
from typing import Optional
from pydantic_ai import Agent
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

load_dotenv()

class EmailContent(BaseModel):
    subject: str = Field(description="Email subject line")
    email_body: str = Field(description="Complete email body in HTML format")

class EmailManager:
    """
    EmailManager with custom SMTP provider
    """
    
    def __init__(self):
        """Initialize EmailManager with custom SMTP configuration"""
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.sender_name = os.getenv("SENDER_NAME", "TwoCare AI Team")
        self.sender_email = os.getenv("SENDER_EMAIL", "care@2care.ai")
        
        self.agent = Agent('openai:gpt-4', output_type=EmailContent)
        
       
    def generate_care_email(self, transcript: str) -> EmailContent:
        """Generate personalized care email content"""
        prompt = f"""
        You are a compassionate healthcare communication specialist for TwoCare AI. Based on the following call transcript, create a warm, empathic, and professional follow-up email for the customer.

        TRANSCRIPT:
        {transcript}

        EMAIL REQUIREMENTS:
        1. **Tone**: Conversational, warm, empathic, and reassuring
        2. **Style**: Personal but professional, like talking to a trusted friend.Visually it should look prefessional
        3. **Structure**: 
           - Warm greeting using their name
           - Acknowledge their care situation with empathy
           - Provide a clean summary table of their loved one's information
           - Include next steps and timeline
           - Add helpful resources or tips
           - Warm, supportive closing

        4. **Content Guidelines**:
           - Use "we understand" language to show empathy
           - Acknowledge the challenges of distance caregiving
           - Make them feel supported and not alone
           - Be specific about what happens next
           - Include a table with their loved one's health information
           - Keep it concise but comprehensive
           - Use HTML formatting for the email

        5. **information**: Create a clean/clear list with the information collected. Be very comprehensive about it.
           
        6. **Additional Value**: Include 2-3 practical tips for remote caregiving or relevant resources. then include next steps.

        Generate both an email subject line and the complete email body in HTML format.
        """
        
        result = self.agent.run_sync(prompt)
        return result.output
    
    def send_email(self, recipient_email: str, subject: str, html_body: str) -> bool:
        """Send email using custom SMTP provider"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = recipient_email
            
            # Add HTML content
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
            
            # Send email via custom SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(message)
            
            print(f"✅ Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
            return False
    
    def send_care_email(self, transcript: str, recipient_email: str) -> bool:
        """Generate and send care coordination email"""
        try:
            email_content = self.generate_care_email(transcript)
            return self.send_email(recipient_email, email_content.subject, email_content.email_body)
        except Exception as e:
            print(f"❌ Error in send_care_email: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Test SMTP connection"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                print("✅ SMTP connection successful!")
                return True
        except Exception as e:
            print(f"❌ SMTP connection failed: {str(e)}")
            return False