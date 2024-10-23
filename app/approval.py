import requests
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

# SMTP4Dev server settings
SMTP_SERVER = "192.168.0.185"
SMTP_PORT = 25
BILLING_EMAIL = "billaccount1@company.com"
SHIPPING_EMAIL = "shipaccount1@company.com"

# API endpoint settings
SMTP4DEV_API_URL = "http://192.168.0.185:5000/api"

def get_unread_messages(mailbox_name):
    """Fetch unread messages from the specified mailbox."""
    url = f"{SMTP4DEV_API_URL}/Messages?mailboxName={mailbox_name}&sortColumn=receivedDate&sortIsDescending=true&page=1&pageSize=50"
    response = requests.get(url, headers={'accept': 'application/json'})
    if response.status_code == 200:
        messages = response.json().get("results", [])
        unread_messages = [msg for msg in messages if msg["isUnread"]]
        return unread_messages
    return []

def get_message_content(message_id):
    """Fetch the plaintext content of the email."""
    url = f"{SMTP4DEV_API_URL}/Messages/{message_id}/plaintext"
    response = requests.get(url, headers={'accept': 'application/json'})
    if response.status_code == 200:
        return response.text
    return ""

def mark_message_as_read(message_id):
    """Mark the message as read after processing."""
    url = f"{SMTP4DEV_API_URL}/Messages/{message_id}/markRead"
    response = requests.post(url)
    return response.status_code == 200

def send_response(to_email, from_email, subject, body):
    """Send an email response after approval."""
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Add the email body
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.send_message(msg)
            print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def process_mailbox(mailbox_name, from_email):
    """Process unread messages from a mailbox."""
    unread_messages = get_unread_messages(mailbox_name)

    for message in unread_messages:
        message_id = message["id"]
        from_customer = message["from"]
        subject = message["subject"]

        print(f"\nNew message from {from_customer}: {subject}")

        # Get message content
        content = get_message_content(message_id)
        print(f"Message content:\n{content}\n")

        # Ask for user approval
        approval = input(f"Do you approve responding to this email? (y/n): ").strip().lower()
        if approval == 'y':
            response_body = content
            send_response(from_customer, from_email, f"Re: {subject}", response_body)
            mark_message_as_read(message_id)
            print(f"Message processed and marked as read.")
        else:
            print("Message skipped.")

def main():
    while True:
        print("\nChecking for unread messages in Billing mailbox...")
        process_mailbox("billaccount1", BILLING_EMAIL)

        print("\nChecking for unread messages in Shipping mailbox...")
        process_mailbox("shipaccount1", SHIPPING_EMAIL)

        # Wait before next iteration
        time.sleep(10)

if __name__ == "__main__":
    main()
