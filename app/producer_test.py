from confluent_kafka import Producer
import json

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:19092'
BILLING_TOPIC = 'billing_topic'

print(f"Using Kafka bootstrap servers: {KAFKA_BOOTSTRAP_SERVERS}")
print(f"Using Kafka topic: {BILLING_TOPIC}")

# Configure the producer
conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
}

# Create a Kafka producer
producer = Producer(**conf)

# Define a test complaint message
complaint_message_template = {
    "from": "customer1@example.com",
    "to": "support@example.com",
    "content": "I have an issue with my billing statement.",
    "type": "billing_complaint",
    "summary": "Billing statement discrepancy",
    "forward": "billing"
}

# Send multiple messages to the Kafka topic
for i in range(10):
    complaint_message = complaint_message_template.copy()  # Copy the template to avoid overwriting
    complaint_message["content"] += f" This is complaint number {i + 1}."
    
    try:
        producer.produce(BILLING_TOPIC, key=None, value=json.dumps(complaint_message))
        producer.flush()  # Ensure all messages are sent
        print(f"Complaint message {i + 1} sent successfully.")
    except Exception as e:
        print(f"Failed to send complaint message {i + 1}: {str(e)}")

# Final flush to ensure all messages are sent before exiting
producer.flush()
