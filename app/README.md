### Running the Applications

This project involves running seven different scripts, each contributing to the overall flow of customer complaint handling, classification, and resolution using Redpanda as a message broker and Ollama for generating responses. Below is an expanded and detailed guide on what each script does and how to run them in separate terminal windows or tabs. The services should be executed in the order presented.

---

#### **Terminal 1 - Flask Application (Initial Data Generation)**
The following scripts can be run inside the container directly or run independently if you have the dependencies installed locally.
**Purpose**: The `flask_app.py` script initializes and generates synthetic customer complaints, simulating email messages sent to `support@company.com`. These complaints will later be picked up by other components for processing.

**Command**: 
```bash
docker-compose exec python-app python flask_app.py
```

**Explanation**: This service simulates customer complaints and sends them to the support system, generating messages for the system to process. It serves as the entry point of the workflow.

---

#### **Terminal 2 - Redpanda Connection (Email Fetching and Producing to Redpanda)**

**Purpose**: The `fet_redpanda_connect.py` script fetches emails from the support mailbox and produces the contents into a `support_topic` in the Redpanda broker. This is the message queue used to pass the data for further processing by Ollama and other services.

**Command**: 
```bash
docker-compose exec python-app python fet_redpanda_connect.py
```

**Explanation**: This script interfaces with the Redpanda message broker to produce email content into the queue, which will then be processed by Ollama. The fetched emails are parsed into JSON format for easier downstream handling.

---

#### **Terminal 3 - Classifier Consumer (Message Classification and Forwarding)**

**Purpose**: The `classifier_consumer_kafka.py` script consumes messages from the `output_support_topic`. It processes the output from Ollama, specifically reading the `forward` field in the JSON, and forwards the message to either the billing or shipping topics based on classification. If it is unable to classify the message, it forwards it to the helpdesk.

**Command**: 
```bash
docker-compose exec python-app python classifier_consumer_kafka.py
```

**Explanation**: The classifier acts as a decision-maker, sorting messages into billing or shipping topics. It relies on Ollama's LLM to classify the messages correctly, ensuring appropriate handling by the next consumers.

---

#### **Terminal 4 - Billing Database (Billing Complaint Management)**

**Purpose**: The `billing_db.py` script provides a simple user interface for checking the local SQLite database containing billing complaints. It matches complaints with customer details to allow for follow-up actions.

**Command**: 
```bash
docker-compose exec python-app python billing_db.py
```

**Explanation**: This service serves as the database interface for billing complaints, allowing users to check customer details associated with specific complaints. It initializes and manages the local database.

---

#### **Terminal 5 - Shipping Database (Shipping Complaint Management)**

**Purpose**: The `shipping_db.py` script provides a similar interface for managing the shipping database. It initializes the shipping database and displays shipping-related complaints.

**Command**: 
```bash
docker-compose exec python-app python shipping_db.py
```

**Explanation**: This service functions like the billing database but focuses on shipping complaints, enabling users to track and manage shipping issues reported by customers.

---

#### **Terminal 6 - Billing Consumer (Response Generation and Email Reply for Billing)**

**Purpose**: The `billing_consumer.py` script consumes messages from the billing topic in Redpanda. It generates a response using Ollama and sends the reply to `shipaccount1@email.com` for approval before it is sent to the customer.

**Command**: 
```bash
docker-compose exec python-app python billing_consumer.py
```

**Explanation**: This script handles billing-related messages, generating an appropriate response using Ollama's LLM and routing it for approval. Once approved, the response is sent back to the customer.

---

#### **Terminal 7 - Shipping Consumer (Response Generation and Email Reply for Shipping)**

**Purpose**: The `shipping_consumer.py` script consumes messages from the shipping topic in Redpanda. Similar to the billing consumer, it generates responses using Ollama and sends them to `billaccount1@email.com` for approval.

**Command**: 
```bash
docker-compose exec python-app python shipping_consumer.py
```

**Explanation**: The shipping consumer script processes shipping complaints, generates replies, and sends them for approval before dispatching the final response to the customer.

---

### **Approval Script**

**Purpose**: After all messages have been processed, the `approval.py` script simulates the role of an approver. It checks the responses generated by the billing and shipping consumers and sends the approved replies back to the customers.

---

### **Redpanda Overview**

#### **Redpanda Broker**
**Role**: Redpanda is used as the message broker to handle the queuing of emails and the classification output. It efficiently handles high-throughput data and acts as the backbone of the messaging system, ensuring that all communication between components is properly queued and processed.

#### **Redpanda Connect**
**Role**: Redpanda Connect is responsible for integrating Ollama into the workflow. It processes the messages produced by the system (from the support mailbox) and ensures that Ollama can parse and classify the emails, outputting structured JSON.

#### **Redpanda Data Transformation**
**Role**: Data transformation is performed by Redpanda to ensure that the data flowing between the services is correctly formatted and that messages are passed from one stage to another efficiently. It ensures that the email data is transformed into a format that Ollama can process, and Ollama’s output is then transformed again for further handling by the classifier.

---

### **Important Notes**

1. **Dependencies**:
   - Docker and Docker Compose must be installed and running.
   - Ensure that Ollama is up and running on your local machine.
   - Ensure that the Redpanda broker is running and configured to handle the relevant topics.

2. **Network Configuration**:
   - The system uses host networking to ensure seamless communication between the services, especially for Ollama and Redpanda.


### Redpanda Connect Runtime Configuration

In this project, Redpanda Connect is responsible for integrating the Ollama processor, classifying emails, and forwarding them for further processing. Below is the YAML configuration used to set up the Redpanda Connect runtime, including the input from `support_topic`, processing through the Ollama model, and outputting the results to `output_support_topic`.

```yaml
input:
  label: ""
  kafka:
    addresses: 
      - localhost:19092
    topics: 
      - support_topic
    target_version: 2.1.0
    checkpoint_limit: 1024
    auto_replay_nacks: true
    consumer_group: test_group  # Add your consumer group here

pipeline:
  processors:
    - label: ""
      ollama_chat:
        model: llama3.2:latest  # Updated model version
        prompt: "Extract the following details from the email: 1. To Email, 2. From Email, 3. Content, 4. Type of Message, 5. Summary, 6. Forward (strictly either 'shipping','billing' or 'unknown' based on the content of the email). Output a JSON file with the following fields: { 'to': '', 'from': '', 'content': '', 'type': '', 'summary': '', 'forward': '' } Email: '${! content() }'"
        response_format: json
        max_tokens: 0
        temperature: 0
        runner:
          context_size: 0
          batch_size: 0
        server_address: http://localhost:11434

output:
  label: ""
  kafka:
    addresses: 
      - localhost:19092
    topic: output_support_topic
    target_version: 2.1.0
    key: ""
    partitioner: fnv1a_hash
    compression: none
    static_headers: {}
    metadata:
      exclude_prefixes: []
    max_in_flight: 64
    batching:
      count: 0
      byte_size: 0
      period: ""
      check: ""
```

---

### **Explanation of Key Components**:

#### **Input Section**:
- **Kafka Broker**: Redpanda listens on `localhost:19092` to consume messages from the `support_topic`.
- **Consumer Group**: The consumer group for the input topic is defined as `test_group`, ensuring that multiple consumers can process messages together.

#### **Pipeline Section**:
- **Ollama Model**: The processor uses the latest version of the Ollama model `llama3.2:latest` to classify emails.
- **Prompt**: A specific prompt instructs the model to extract key fields (e.g., to/from email, content, summary, etc.) from the email content.
- **JSON Output**: The processed data is outputted in JSON format.

#### **Output Section**:
- **Kafka Broker**: The output is sent to `output_support_topic` on the same Redpanda broker at `localhost:19092`.
- **Partitioning**: The partitioner is set to `fnv1a_hash` to ensure consistent distribution across partitions in Kafka.

---

### Redpanda Connect Runtime Command

To run the Redpanda Connect runtime with your YAML configuration file, use the following command:

```bash
rpk connect run ./config.yaml
```

This command starts the Redpanda Connect runtime using the configurations defined in `config.yaml`. This will set up the pipeline where:
1. Redpanda consumes messages from `support_topic`.
2. Ollama processes the email content based on the provided prompt.
3. The output is published to `output_support_topic`.

#### **Redpanda Connect Runtime**:
Redpanda Connect plays a critical role in the project, facilitating the integration of Ollama for email classification. The `connect.yaml` file provided above outlines how Redpanda consumes email data from the `support_topic`, processes it with Ollama, and outputs the structured response in JSON format to the `output_support_topic`. This configuration ensures that emails are appropriately classified and forwarded based on their content.

#### **Important Notes**:
- Ensure Ollama is installed and running on `http://localhost:11434`.
- Verify that the Redpanda broker is running and accessible on `localhost:19092`.
