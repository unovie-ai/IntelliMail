import time
import requests
import json
import logging
from confluent_kafka import Producer
import socket

# Base API URL for Mail4Dev
BASE_URL = 'http://192.168.0.185:5000/api'

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'redpanda:9092'  # IP address of the system running Redpanda

# Function to get new messages from the 'support' mailbox
def get_messages(mailbox_name='support', page_size=50):
    url = f'{BASE_URL}/Messages/new?mailboxName={mailbox_name}&pageSize={page_size}'
    try:
        response = requests.get(url, headers={'accept': 'application/json'})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch messages. Status code: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"Error fetching messages: {str(e)}")
        return []
# Function to mark a message as read by ID
def mark_message_as_read(message_id):
    url = f'{BASE_URL}/Messages/{message_id}/markRead'
    response = requests.post(url, headers={'accept': '*/*'})
    
    if response.status_code == 200:
        print(f"Marked message with ID: {message_id} as read.")
    else:
        print(f"Failed to mark message {message_id} as read. Status code: {response.status_code}")

# Function to fetch the plain text content of the email by ID
def get_message_plaintext(message_id):
    url = f'{BASE_URL}/Messages/{message_id}/plaintext'
    try:
        response = requests.get(url, headers={'accept': 'application/json'})
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch message content for ID: {message_id}. Status code: {response.status_code}")
            return "Message content unavailable."
    except requests.RequestException as e:
        print(f"Error fetching message content: {str(e)}")
        return "Message content unavailable."

# Function to delete a message by ID
def delete_message(message_id):
    url = f'{BASE_URL}/Messages/{message_id}'
    try:
        response = requests.delete(url, headers={'accept': '*/*'})
        if response.status_code == 200:
            print(f"Deleted message with ID: {message_id}")
        else:
            print(f"Failed to delete message {message_id}. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error deleting message: {str(e)}")

# Function to produce messages to Kafka using confluent_kafka.Producer
def send_message_to_kafka(message):
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'client.id': socket.gethostname()
    }

    producer = Producer(conf)

    def delivery_report(err, msg):
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    try:
        producer.produce(
            topic="support_topic",
            key=message['id'],  # Use message ID as the key
            value=json.dumps(message),  # Convert to JSON
            callback=delivery_report
        )
        
        print("Flushing records...")
        producer.flush(timeout=15)  # Wait for delivery before exiting

        # Add a small delay to ensure the delivery report callback is executed
        time.sleep(1)
        
    except Exception as e:
        print(f"An error occurred while producing message: {e}")

# Main function to check mailbox, process emails, send to Kafka, and log details
def check_mailbox():
    while True:
        messages = get_messages()

        if messages:
            for message in messages:
                if message["isUnread"] is True:
                    # Fetch and print detailed message content
                    plaintext_content = get_message_plaintext(message['id'])
                    print(f"From: {message['from']}")
                    print(f"To: {message['to']}")
                    print(f"Subject: {message['subject']}")
                    print(f"Received Date: {message['receivedDate']}")
                    print(f"Message ID: {message['id']}")
                    print("=" * 40)
                    print("Message Content:")
                    print(plaintext_content)
                    print("=" * 40)

                    # Prepare the message for Kafka
                    log_message = {
                        "id": message['id'],
                        "from": message['from'],
                        "to": message['to'],
                        "subject": message['subject'],
                        "received_date": message['receivedDate'],
                        "content": plaintext_content
                    }

                    # Send the message to Kafka
                    send_message_to_kafka(log_message)
                    print(f"Processed and sent message ID: {message['id']} to Kafka topic 'support_topic'.")
                    # Mark the message as read instead of deleting it
                    mark_message_as_read(message['id'])
                    # Delete the message after processing
                    #delete_message(message['id'])
                else:
                    print(f"Message ID: {message['id']} is already marked as read.")
                    continue
        else:
            print("No new messages found.")
        # Sleep for 60 seconds before checking again
        time.sleep(60)

if __name__ == '__main__':
    check_mailbox()
