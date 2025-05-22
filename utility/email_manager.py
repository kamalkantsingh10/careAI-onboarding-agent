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
    EmailManager with Mailtrap for testing
    """
    
    def __init__(self):
        """Initialize EmailManager with Mailtrap configuration"""
        self.smtp_server = os.getenv("SMTP_SERVER", "sandbox.smtp.mailtrap.io")
        self.smtp_port = int(os.getenv("SMTP_PORT", "2525"))
        self.username = os.getenv("MAILTRAP_USERNAME")  # Your mailtrap username
        self.password = os.getenv("MAILTRAP_PASSWORD")  # Your mailtrap password
        self.sender_name = os.getenv("SENDER_NAME", "TwoCare AI Team")
        self.sender_email = os.getenv("SENDER_EMAIL", "care@2care.ai")
        
        self.agent = Agent('openai:gpt-4', output_type=EmailContent)
        
        # Validate configuration
        if not self.username or not self.password:
            print("❌ Please set MAILTRAP_USERNAME and MAILTRAP_PASSWORD in .env file")
    
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

        5. **information**: Create a clean/clear list with the information collected be comprehensive about it.
           
        6. **Additional Value**: Include 2-3 practical tips for remote caregiving or relevant resources. then include next steps.

        Generate both an email subject line and the complete email body in HTML format.
        """
        
        result = self.agent.run_sync(prompt)
        return result.output
    
    def send_email(self, recipient_email: str, subject: str, html_body: str) -> bool:
        """Send email using Mailtrap SMTP"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = recipient_email
            
            # Add HTML content
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
            
            # Send email via Mailtrap
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(message)
            
            print(f"✅ Email sent successfully to {recipient_email}")
            print("📧 Check your Mailtrap inbox to see the email!")
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
        """Test Mailtrap connection"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                print("✅ Mailtrap connection successful!")
                return True
        except Exception as e:
            print(f"❌ Mailtrap connection failed: {str(e)}")
            return False

