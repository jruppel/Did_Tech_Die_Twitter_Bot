# Text alerts
import constants
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_provider, recipient, email, password = constants.smtp_provider, constants.recipient, constants.email, constants.password

def send_text(message):
    server = smtplib.SMTP(smtp_provider, 587)
    server.starttls()
    server.login(email, password)
    msg = MIMEMultipart()
    msg['From'], msg['To'], msg['Subject'] = email, recipient, "New tweet\n"
    msg.attach(MIMEText(message, 'plain'))
    sms = msg.as_string()
    server.sendmail(email,recipient,sms)