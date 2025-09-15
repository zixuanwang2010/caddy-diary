import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import current_app

class EmailService:
    def __init__(self):
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@caddydiary.com')
        self.app_name = 'Caddy Diary'
        
    def send_verification_email(self, to_email, username, verification_code):
        """Send verification email using SendGrid"""
        try:
            if self.sendgrid_api_key:
                return self._send_with_sendgrid(to_email, username, verification_code)
            else:
                return self._send_with_smtp(to_email, username, verification_code)
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def _send_with_sendgrid(self, to_email, username, verification_code):
        """Send email using SendGrid API"""
        try:
            sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
            
            # Create email content
            subject = f"Verify your {self.app_name} account"
            
            html_content = self._create_verification_html(username, verification_code)
            text_content = self._create_verification_text(username, verification_code)
            
            # Create Mail object
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=text_content
            )
            
            # Send email
            response = sg.send(message)
            print(f"SendGrid email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"SendGrid error: {str(e)}")
            return False
    
    def _send_with_smtp(self, to_email, username, verification_code):
        """Send email using SMTP (fallback)"""
        try:
            # SMTP settings (you can configure these in .env)
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            if not smtp_username or not smtp_password:
                print("SMTP credentials not configured")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Verify your {self.app_name} account"
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Create content
            html_content = self._create_verification_html(username, verification_code)
            text_content = self._create_verification_text(username, verification_code)
            
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            print(f"SMTP email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"SMTP error: {str(e)}")
            return False
    
    def _create_verification_html(self, username, verification_code):
        """Create HTML version of verification email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Account</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .verification-code {{ background: #fff; border: 2px solid #667eea; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }}
                .code {{ font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 5px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to {self.app_name}!</h1>
                    <p>Your personal AI-powered diary companion</p>
                </div>
                
                <div class="content">
                    <h2>Hi {username},</h2>
                    <p>Thank you for signing up! To complete your registration, please verify your email address using the verification code below:</p>
                    
                    <div class="verification-code">
                        <div class="code">{verification_code}</div>
                        <p><strong>This code expires in 15 minutes</strong></p>
                    </div>
                    
                    <p>Enter this code in the verification page to activate your account and start your diary journey.</p>
                    
                    <p>If you didn't create an account with {self.app_name}, you can safely ignore this email.</p>
                    
                    <p>Best regards,<br>The {self.app_name} Team</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message, please do not reply to this email.</p>
                    <p>&copy; 2024 {self.app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_verification_text(self, username, verification_code):
        """Create text version of verification email"""
        return f"""
Welcome to {self.app_name}!

Hi {username},

Thank you for signing up! To complete your registration, please verify your email address using the verification code below:

VERIFICATION CODE: {verification_code}

This code expires in 15 minutes.

Enter this code in the verification page to activate your account and start your diary journey.

If you didn't create an account with {self.app_name}, you can safely ignore this email.

Best regards,
The {self.app_name} Team

---
This is an automated message, please do not reply to this email.
© 2024 {self.app_name}. All rights reserved.
        """
