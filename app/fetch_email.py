import time
import requests

# Base API URL for Mail4Dev
BASE_URL = 'http://192.168.68.97:5000/api'

# Function to get new messages from the 'support' mailbox
def get_messages(mailbox_name='support', page_size=50):
    url = f'{BASE_URL}/Messages/new?mailboxName={mailbox_name}&pageSize={page_size}'
    response = requests.get(url, headers={'accept': 'application/json'})
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch messages. Status code: {response.status_code}")
        return []

# Function to fetch the plain text content of the email by ID
def get_message_plaintext(message_id):
    url = f'{BASE_URL}/Messages/{message_id}/plaintext'
    response = requests.get(url, headers={'accept': 'application/json'})
    
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch message content for ID: {message_id}. Status code: {response.status_code}")
        return "Message content unavailable."

# Function to delete a message by ID
def delete_message(message_id):
    url = f'{BASE_URL}/Messages/{message_id}'
    response = requests.delete(url, headers={'accept': '*/*'})
    
    if response.status_code == 200:
        print(f"Deleted message with ID: {message_id}")
    else:
        print(f"Failed to delete message {message_id}. Status code: {response.status_code}")

# Main function to check mailbox and process emails
def check_mailbox():
    while True:
        messages = get_messages()

        if messages:
            for message in messages:
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

                # Delete the message after processing
                delete_message(message['id'])
        
        # Sleep for a bit before checking again (e.g., 60 seconds)
        time.sleep(60)

if __name__ == '__main__':
    check_mailbox()
