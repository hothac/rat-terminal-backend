FROM python:3.10-slim

# Linux paketlərini (nmap, gobuster, whois, dnsutils, curl, net-tools) quraşdırırıq
RUN apt-get update && apt-get install -y \
    nmap \
    gobuster \
    whois \
    dnsutils \
    curl \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
