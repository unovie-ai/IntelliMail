import json
import time
import sqlite3
from confluent_kafka import Consumer, Producer, KafkaError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from db_for_classifier import initialize_database
class CustomerDatabase:
    def __init__(self, db_path='db_for_classification.sqlite'):
        self.db_path = db_path

    def update_customer_from_email(self, email_data):
        initialize_database()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Extract customer details from email_data
            email = email_data.get('from', '').lower()
            issue_type = email_data.get('forward', 'other')
            email_content = email_data.get('content', '')

            # Check if customer exists now
            cursor.execute('SELECT customer_id FROM customers WHERE LOWER(email) = ?', (email,))
            result = cursor.fetchone()

            if result:
                customer_id = result[0]
                # Update customer details
                cursor.execute('''
                    UPDATE customers 
                    SET last_contact_date = ?,
                        last_email_content = ?,
                        billing_issues_count = CASE WHEN ? = 'billing' THEN billing_issues_count + 1 ELSE billing_issues_count END,
                        shipping_issues_count = CASE WHEN ? = 'shipping' THEN shipping_issues_count + 1 ELSE shipping_issues_count END,
                        other_issues_count = CASE WHEN ? = 'other' THEN other_issues_count + 1 ELSE other_issues_count END
                    WHERE customer_id = ?
                ''', (datetime.now().isoformat(), email_content, issue_type, issue_type, issue_type, customer_id))

                # Add to email history
                cursor.execute('''
                    INSERT INTO email_history (customer_id, email_content, issue_type)
                    VALUES (?, ?, ?)
                ''', (customer_id, email_content, issue_type))

                conn.commit()
                return True
            return False

        finally:
            conn.close()

    def get_customer_stats(self, email):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT name, email, billing_issues_count, shipping_issues_count, other_issues_count
                FROM customers WHERE LOWER(email) = ?
            ''', (email.lower(),))
            return cursor.fetchone()
        finally:
            conn.close()

def main():
    # Kafka configuration
    KAFKA_BOOTSTRAP_SERVERS = 'redpanda:9092'
    OUTPUT_TOPIC = 'output_support_topic'

    # Initialize database handler
    db = CustomerDatabase()

    # Configure Kafka consumer and producer
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'my_consumer_group',
        'auto.offset.reset': 'earliest',
    })

    producer = Producer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    })

    consumer.subscribe([OUTPUT_TOPIC])

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                print("No message available.")
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Error occurred: {msg.error()}")
                    break

            # Process message
            try:
                message_value = msg.value().decode('utf-8')
                json_data = json.loads(message_value)
                print(type(json_data))
                print(type(message_value))
                # Update customer database
                validate=db.update_customer_from_email(json_data)
                if not validate:
                    print("Customer not found")
                    continue
                # Forward to appropriate topic
                forward_value = json_data.get("forward", "other")
                if forward_value in ["billing", "shipping"]:
                    producer.produce(f"{forward_value}_topic", value=message_value)
                    print(f"Produced to {forward_value}_topic: {message_value}")
                else:
                    # Handle unknown forward value
                    email_msg = MIMEMultipart()
                    email_msg['From'] = json_data.get('from', 'customer1@example.com')
                    email_msg['To'] = "hpdesk1@company.com"
                    email_msg['Subject'] = "Forwarded Email"
                    # Convert json_data back to a formatted string
                    formatted_message = f"{json_data.get('content', '')}" # Pretty print the JSON
                    email_msg.attach(MIMEText(formatted_message, 'plain'))

                    with smtplib.SMTP('192.168.0.185', 25) as server:
                        server.send_message(email_msg)
                        print("Email forwarded to hpdesk1@company.com")
                        print(f"Email: {message_value}")
                        print("")

                producer.flush()

            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON: {e}")
            print("\n||||||\n")
            time.sleep(5)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    main()