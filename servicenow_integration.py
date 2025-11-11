import os
import requests
import base64
from slack_sdk import WebClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def create_servicenow_ticket(title, description, urgency='2', impact='2'):
    """
    Create a ServiceNow incident ticket.
    Falls back to mock print if credentials are missing or request fails.
    """
    instance = os.getenv('SERVICENOW_INSTANCE')
    user = os.getenv('SERVICENOW_USER')
    password = os.getenv('SERVICENOW_PASSWORD')

    if not all([instance, user, password]):
        print(f"[Mock ServiceNow Ticket] {title} - {description}")
        return

    try:
        auth = base64.b64encode(f"{user}:{password}".encode()).decode()
        headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        url = f"https://{instance}.service-now.com/api/now/table/incident"
        body = {
            'short_description': title,
            'description': description,
            'urgency': urgency,
            'impact': impact
        }
        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        ticket_num = response.json().get('result', {}).get('number', 'UNKNOWN')
        print(f"[ServiceNow Ticket Created] {ticket_num}")
        return ticket_num
    except Exception as e:
        print(f"[ServiceNow Error] {e}")
        print(f"[Mock ServiceNow Ticket] {title} - {description}")

def send_alert(msg, channel='#alerts', to_email=None):
    """
    Send alert message via Slack or Email (simple text).
    Falls back to print if both fail.
    """
    sent = False
    token = os.getenv('SLACK_TOKEN')
    if token:
        try:
            client = WebClient(token=token)
            client.chat_postMessage(channel=channel, text=msg)
            print("[Slack Alert Sent]")
            sent = True
        except Exception as e:
            print(f"[Slack Error] {e}")

    if not sent and to_email:
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_user = os.getenv('SMTP_USER')
        smtp_pass = os.getenv('SMTP_PASS')
        if smtp_user and smtp_pass and smtp_server:
            try:
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
                server.starttls()
                server.login(smtp_user, smtp_pass)
                email_msg = MIMEText(msg)
                email_msg['Subject'] = 'FlashNarrative Alert'
                email_msg['From'] = smtp_user
                email_msg['To'] = to_email
                server.send_message(email_msg)
                server.quit()
                print(f"[Email Alert Sent] to {to_email}")
                sent = True
            except Exception as e:
                print(f"[Email Alert Error] {e}")
    if not sent:
        print(f"[Alert Fallback - Print] {msg}")

def send_report_email_with_attachments(to_email, subject, body, attachments):
    """
    Sends an email with one or more attachments. Returns True/False.
    """
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS') # Use App Password for Gmail

    if not all([smtp_server, smtp_user, smtp_pass, to_email]):
        print("[Email Error] Missing SMTP credentials or recipient email.")
        return False # Indicate failure

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        for filename, content_bytes, mime_type in attachments:
            maintype, subtype = mime_type.split('/', 1)
            part = MIMEBase(maintype, subtype)
            part.set_payload(content_bytes)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {filename}")
            msg.attach(part)

        server = smtplib.SMTP(smtp_server, smtp_port, timeout=20)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"[Email Sent] Report with {len(attachments)} attachment(s) sent to {to_email}")
        return True # Indicate success
    except smtplib.SMTPAuthenticationError:
         print("[Email Error] SMTP Authentication Failed. Check email/password (use App Password).")
         return False
    except Exception as e:
        print(f"[Email Error] Failed to send report: {e}")
        return False