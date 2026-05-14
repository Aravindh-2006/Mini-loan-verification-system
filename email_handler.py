import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_loan_status_email(receiver_email, loan_id, status, message):
    """
    Sends an automated email to the user regarding their loan status.
    """
    sender_email = os.getenv('MAIL_USERNAME')
    sender_password = os.getenv('MAIL_PASSWORD')
    smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('MAIL_PORT', 587))
    
    if not sender_email or not sender_password:
        print("⚠️ Email credentials not found in environment variables. Skipping email.")
        return False

    # Create the email content
    subject = f"Update on Your Loan Application #{loan_id}"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Loan Application Update</h2>
            <p>Dear Applicant,</p>
            <p>There has been an update to your loan application <strong>#{loan_id}</strong>.</p>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-left: 5px solid #3498db; margin: 20px 0;">
                <p style="margin: 0;"><strong>New Status:</strong> <span style="text-transform: uppercase; color: {'#27ae60' if status == 'approved' else '#e74c3c' if status == 'rejected' else '#f39c12'}; font-weight: bold;">{status}</span></p>
            </div>
            
            <p><strong>Admin Message:</strong></p>
            <div style="padding: 15px; background-color: #fff; border: 1px dashed #ccc; border-radius: 5px;">
                <p style="margin: 0; white-space: pre-wrap;">{message}</p>
            </div>
            
            <p style="margin-top: 20px;">You can log in to your dashboard to view full details.</p>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 0.9em; color: #7f8c8d;">
                <p>This is an automated notification from the Mini Loan Verification System.</p>
                <p>Admin: {sender_email}</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = f"Mini Loan System <{sender_email}>"
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent successfully to {receiver_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP Authentication Failed (Error 535).")
        print("⚠️  If using Gmail, ensure you use an 'App Password' instead of your regular account password.")
        print("⚠️  Continuing without sending email.")
        return False
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        print("⚠️  Continuing without sending email.")
        return False
