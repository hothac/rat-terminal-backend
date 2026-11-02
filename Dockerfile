FROM python:3.10-slim

# Əsas Linux və kiber təhlükəsizlik alətlərini quraşdırırıq
RUN apt-get update && apt-get install -y \
    bash \
    nmap \
    gobuster \
    whois \
    dnsutils \
    curl \
    wget \
    net-tools \
    iputils-ping \
    nikto \
    sqlmap \
    hydra \
    john \
    git \
    vim \
    nano \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
