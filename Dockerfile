FROM python:3.10-slim

# Əsas sistem paketləri və asılılıqları quraşdırırıq
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    nmap \
    whois \
    dnsutils \
    curl \
    wget \
    net-tools \
    iputils-ping \
    git \
    vim \
    nano \
    gobuster \
    && rm -rf /var/lib/apt/lists/*

# sqlmap-i rəsmi GitHub repozitoriyasından çəkirik
RUN git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap \
    && ln -s /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap

# Əsas wordlist-ləri yaratmaq üçün daxili papka hazırlayırıq
RUN mkdir -p /usr/share/wordlists/dirb \
    && curl -s https://raw.githubusercontent.com/v0space/payloads/main/wordlists/common.txt -o /usr/share/wordlists/dirb/common.txt

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
