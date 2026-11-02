FROM python:3.10-slim

# Yalnızca standart Debian depolarında bulunan temel ağ ve sistem araçlarını kuruyoruz
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
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
