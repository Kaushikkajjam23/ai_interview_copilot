# backend/app/email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "your-email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-app-password")
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "AI Interview Co-Pilot <noreply@example.com>")

def send_email(recipient_email: str, subject: str, html_content: str):
    """Send an email with HTML content"""
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = EMAIL_SENDER
    message["To"] = recipient_email
    
    # Turn the HTML content into MIMEText objects
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    
    try:
        # Create secure connection with server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, recipient_email, message.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def format_datetime(dt):
    """Format datetime object to a human-readable string"""
    return dt.strftime("%A, %B %d, %Y at %I:%M %p")

def send_candidate_email(recipient_email: str, recipient_name: str, interview_details: dict):
    """Send interview notification email to candidate"""
    subject = f"Interview Scheduled: {interview_details['topic']}"
    
    # Format the scheduled time
    scheduled_time = interview_details['scheduled_time']
    if isinstance(scheduled_time, str):
        scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
    formatted_time = format_datetime(scheduled_time)
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4a6fa5; color: white; padding: 10px 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Interview Scheduled</h2>
            </div>
            <div class="content">
                <p>Hello {recipient_name},</p>
                
                <p>Your interview has been scheduled for <strong>{interview_details['topic']}</strong>.</p>
                
                <p><strong>Details:</strong></p>
                <ul>
                    <li><strong>Date & Time:</strong> {formatted_time}</li>
                    <li><strong>Interviewer:</strong> {interview_details['interviewer_name']}</li>
                    <li><strong>Topic:</strong> {interview_details['topic']}</li>
                </ul>
                
                <p>Please make sure to be ready 5 minutes before the scheduled time. You'll receive a link to join the interview closer to the date.</p>
                
                <p>If you need to reschedule or have any questions, please reply to this email.</p>
                
                <p>Best regards,<br>AI Interview Co-Pilot Team</p>
            </div>
            <div class="footer">
                <p>© {datetime.now().year} AI Interview Co-Pilot. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(recipient_email, subject, html_content)

def send_interviewer_email(recipient_email: str, recipient_name: str, interview_details: dict):
    """Send interview notification email to interviewer"""
    subject = f"Interview Scheduled: {interview_details['topic']} with {interview_details['candidate_name']}"
    
    # Format the scheduled time
    scheduled_time = interview_details['scheduled_time']
    if isinstance(scheduled_time, str):
        scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
    formatted_time = format_datetime(scheduled_time)
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4a6fa5; color: white; padding: 10px 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
            .details {{ background-color: #eef2f7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Interview Scheduled</h2>
            </div>
            <div class="content">
                <p>Hello {recipient_name},</p>
                
                <p>You have an upcoming interview scheduled with <strong>{interview_details['candidate_name']}</strong>.</p>
                
                <div class="details">
                    <p><strong>Interview Details:</strong></p>
                    <ul>
                        <li><strong>Date & Time:</strong> {formatted_time}</li>
                        <li><strong>Candidate:</strong> {interview_details['candidate_name']}</li>
                        <li><strong>Topic:</strong> {interview_details['topic']}</li>
                        <li><strong>Level:</strong> {interview_details['candidate_level']}</li>
                        <li><strong>Required Skills:</strong> {interview_details['required_skills']}</li>
                        <li><strong>Focus Areas:</strong> {interview_details['focus_areas']}</li>
                    </ul>
                </div>
                
                <p>Please prepare your questions based on the candidate's level and the focus areas mentioned above.</p>
                
                <p>You'll receive a link to host the interview closer to the scheduled date.</p>
                
                <p>Best regards,<br>AI Interview Co-Pilot Team</p>
            </div>
            <div class="footer">
                <p>© {datetime.now().year} AI Interview Co-Pilot. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(recipient_email, subject, html_content)