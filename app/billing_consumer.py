import json
import time
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from confluent_kafka import Consumer, KafkaError
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
customer_service_prompt = os.getenv('customer_service_prompt')

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:19092'
BILLING_TOPIC = 'billing_topic'

# Configure the consumer
conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': 'billing_consumer_group',
    'auto.offset.reset': 'earliest',
}

# Create the consumer instance
consumer = Consumer(conf)

# Subscribe to the billing topic
consumer.subscribe([BILLING_TOPIC])

# Email configuration
smtp_server = "localhost"
smtp_port = 25  # Updated to 25
billing_email = "billaccount1@company.com"

# Function to get customer details from the database
def get_customer_details(email):
    conn = sqlite3.connect('billing_db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, billing_statement FROM billing_customers WHERE email=?", (email,))
    record = cursor.fetchone()
    conn.close()
    return record

try:
    while True:
        # Poll for new messages
        msg = consumer.poll(1.0)  # Timeout set to 1 second

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Error occurred: {msg.error()}")
                break

        # Process the message
        message_value = msg.value().decode('utf-8')
        print(f"Received message: {message_value}")

        # Extract customer email from message
        json_data = json.loads(message_value)
        customer_email = json_data.get("from", "customer@company.com")

        # Get customer details from the billing database
        customer_details = get_customer_details(customer_email)
        if customer_details:
            customer_name, billing_statement = customer_details
        else:
            customer_name, billing_statement = "Unknown", "No billing statement available"

        # Call the Ollama LLM API for generating the reply
        prompt = f"{customer_service_prompt}. For the following message:\n{message_value}\nOriginal billing statement: {billing_statement}\nCustomer name: {customer_name}. Return the corrected Bill if applicable. [DO NOT USE PLACEHOLDERS]"
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma:2b", "prompt": prompt, "stream": False}
        )

        email_content = response.json().get("response", "") + "\n\nChecked"

        # Set up the email
        msg = MIMEMultipart()
        msg['From'] = customer_email
        msg['To'] = billing_email
        msg['Subject'] = "Billing Inquiry Response"

        # Add the email content to the message
        msg.attach(MIMEText(email_content, 'plain'))

        # Set up the SMTP connection
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                # Send the email
                server.send_message(msg)
                print(f"Email sent successfully to {billing_email}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

        time.sleep(5)  # Wait before processing the next message

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
