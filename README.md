# Instructions for Ports and Access to RedPanda Hackathon

### Setup the environment

Capacity Requirements : 
  - 4 vCPU 
  - 12 GB of RAM
  - 100 GB of SSD Disk Space.

Run the following commands to ensure the proper environment is set

```
docker exec -it ollama ollama pull llama3.2

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



### If you ssh into this Sandbox

ssh -L5000:127.0.0.1:5000 -L8080:127.0.0.1:8080 unovie@<<ip_address>>
password : unovie2024 
