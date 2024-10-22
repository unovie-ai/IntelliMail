from confluent_kafka import Producer
import json
import socket
import time

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def send_single_message():
    conf = {
        'bootstrap.servers': 'localhost:19092',  # IP address of the system running Redpanda
        'client.id': socket.gethostname()
    }

    producer = Producer(conf)

    message = {
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "subject": "Test Subject",
        "content": "This is a test message."
    }

    topic = "support_topic"
    
    try:
        producer.produce(
            topic,
            key="my_key",
            value=json.dumps(message),
            callback=delivery_report
        )
        
        # Wait for any outstanding messages to be delivered and delivery reports to be received
        print("Flushing records...")
        producer.flush(timeout=15)  # Wait for delivery before exiting
        
        # Add a small delay to ensure the delivery report callback is executed
        time.sleep(1)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    send_single_message()