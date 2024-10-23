# Instructions for Ports and Access to RedPanda Hackathon

### Setup the environment

Capacity Requirements : 
  - 4 vCPU 
  - 12 GB of RAM
  - 100 GB of SSD Disk Space.

To Build and start the containers 

```
docker-compose up --build -d
```

Run the following commands to ensure llama3.2 is SLM model 

```
docker exec -it ollama ollama pull llama3.2;
docker exec -it ollama ollama pull gemma:2b

```

### Ports Systems is accessable on.

Mail4Dev : 
  Web Interface : Port 5000


WireGuard for VPN : 
  Web Interface : Port 51821


Redpanda 
  Web Interface : Port 8080 
  username: "john"
  password: "some-secret-password"

