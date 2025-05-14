import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from fastapi import BackgroundTasks
import logging

logger = logging.getLogger(__name__)

# Email configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "ai.interview.copilot@example.com")

def send_email_background(
    to_email: str,
    subject: str,
    html_content: str
):
    """Send email in the background"""
    try:
        # Skip sending if credentials are not configured
        if not EMAIL_USERNAME or not EMAIL_PASSWORD:
            logger.warning("Email credentials not configured. Skipping email send.")
            return False
            
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = EMAIL_FROM
        message["To"] = to_email
        
        # Add HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Send email
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, message.as_string())
            
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def send_interview_invitation(
    background_tasks: BackgroundTasks,
    to_email: str,
    candidate_name: str,
    interviewer_name: str,
    interview_topic: str,
    scheduled_time: str,
    interview_link: str
):
    """Send interview invitation email to candidate"""
    subject = f"Interview Invitation: {interview_topic}"
    
    html_content = f"""
    <html>
    <body>
        <h2>Interview Invitation</h2>
        <p>Hello {candidate_name},</p>
        <p>You have been invited to an interview with {interviewer_name} for {interview_topic}.</p>
        <p><strong>Scheduled Time:</strong> {scheduled_time}</p>
        <p>Please click the link below to join the interview:</p>
        <p><a href="{interview_link}">Join Interview</a></p>
        <p>Best regards,<br>AI Interview Co-Pilot Team</p>
    </body>
    </html>
    """
    
    background_tasks.add_task(
        send_email_background,
        to_email=to_email,
        subject=subject,
        html_content=html_content
    )