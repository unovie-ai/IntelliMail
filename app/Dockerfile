FROM python:3.12.4-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
curl \
unzip \
git \
&& rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Clone the repository
ADD ./* /app

# Create necessary directories
RUN mkdir -p /root/.local/bin
COPY rpk /root/.local/bin

# Add ~/.local/bin to PATH
ENV PATH="/root/.local/bin:$PATH"

# Keep container running
CMD ["tail", "-f", "/dev/null"]

