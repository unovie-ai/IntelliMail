from flask import Flask, request, jsonify
import requests
from faker import Faker
import threading
import time
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

app = Flask(__name__)
fake = Faker()
from dotenv import load_dotenv
import os

# Load the environment variables from .env file
load_dotenv()

# Extract SMTP server and port
smtp_server = "host.docker.internal"
smtp_port = 25

# Extract Redpanda broker port
redpanda_broker_port = os.getenv("REDPANDA_BROKER_PORT")

topics_list = [
    "Customer Billing Issue",
    "Customer Shipment Issue",
    "Customer Billing discount request",
    "Customer Shipment discount request",
    "Customer Billing correction issue",
]

def get_email_template(topic):
    """Generate a base email template using Ollama"""
    template_prompt = f"""
    Generate a formal business email template for a {topic}.
    Write it as a customer sending an inquiry to a company.
    Include a subject line and proper email formatting.
    Use these exact placeholders:
    [COMPANY_CONTACT]
    [AMOUNT]
    [PHONE]
    [CUSTOMER_NAME]
    [CUSTOMER_TITLE]
    [ENQUIRY_DATE]
    [PROCESS_DATE]
    
    Only output the email template with no additional text or explanations.
    """
    
    response = requests.post(
        "http://192.168.0.185:11434/api/generate",
        json={"model": "llama3.2:latest", "prompt": template_prompt, "stream": False}
    )
    
    if response.status_code == 200:
        return response.json().get("response", "")
    else:
        raise Exception(f"Template generation failed: {response.status_code}")

def generate_email_content(topic):
    # Generate fake data
    fake_data = {
        '[COMPANY_CONTACT]': fake.name(),
        '[AMOUNT]': f"${fake.random_int(min=1000, max=10000):,}",
        '[PHONE]': fake.phone_number(),
        '[CUSTOMER_NAME]': fake.name(),
        '[CUSTOMER_TITLE]': fake.job(),
        '[ENQUIRY_DATE]': fake.date_object().strftime('%B %d, %Y'),
        '[PROCESS_DATE]': fake.date_object().strftime('%B %d, %Y')
    }
    
    try:
        # Get template from Ollama
        template = get_email_template(topic)
        
        # Replace placeholders with fake data
        for placeholder, value in fake_data.items():
            template = template.replace(placeholder, str(value))
        
        # Clean up any remaining placeholders with a more specific regex
        template = re.sub(r'\[([A-Z_]+)\]', '', template)
        
        return template.strip()
    
    except Exception as e:
        return f"Error generating email: {str(e)}"

def background_email_task():
    # Extract SMTP server and port
    smtp_server = "192.168.0.185"
    smtp_port = 25

    while True:
        selected_topic = random.choice(topics_list)
        email_content = generate_email_content(selected_topic)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} Generated Email for Topic '{selected_topic}':\n{email_content}\n")

        msg = MIMEMultipart()
        msg['From'] = random.choice(["customer1@email.com", "customer2@email.com", "customer3@email.com"])
        msg['To'] = "support@company.com"
        msg['Subject'] = f"{selected_topic}"
        msg.attach(MIMEText(email_content, 'plain'))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.send_message(msg)
                print(f"{timestamp} Email sent successfully to support@company.com")
        except Exception as e:
            print(f"{timestamp} Failed to send email: {str(e)}")

        time.sleep(15)

# Start the background thread when the Flask app starts
threading.Thread(target=background_email_task, daemon=True).start()

@app.route('/generate_email', methods=['POST'])
def generate_email():
    try:
        data = request.get_json()
        if not data or "topic" not in data:
            return jsonify({"error": "Missing topic in the request."}), 400
        
        topic = data["topic"]
        email_content = generate_email_content(topic)

        return jsonify({"email": email_content, "topic": topic})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request to Ollama API failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5012)