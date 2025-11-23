import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sender_email = os.environ.get("GMAIL_EMAIL")
sender_password = os.environ.get("GMAIL_APP_PASSWORD")
receiver_email = sender_email  # Send test email to yourself

msg = MIMEText("This is a test email from SecureWebAudit setup.")
msg['Subject'] = "Test Email"
msg['From'] = sender_email
msg['To'] = receiver_email

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
    print("✅ Test email sent successfully!")
except smtplib.SMTPAuthenticationError as e:
    print("❌ Authentication failed!")
    print(e)
except Exception as e:
    print("❌ Some other error occurred:")
    print(e)
