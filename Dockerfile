FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

# Install fonts for better Windows-like rendering
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    fontconfig \
    fonts-liberation \
    fonts-dejavu \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fonts-crosextra-carlito \
    fonts-crosextra-caladea \
    fonts-freefont-ttf \
    wget \
    cabextract \
    && \
    # Install MS Core Fonts manually
    mkdir -p /tmp/fonts && \
    cd /tmp/fonts && \
    wget -q http://ftp.de.debian.org/debian/pool/contrib/m/msttcorefonts/ttf-mscorefonts-installer_3.8_all.deb && \
    echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections && \
    apt-get install -y --no-install-recommends ./ttf-mscorefonts-installer_3.8_all.deb && \
    fc-cache -f -v && \
    cd / && rm -rf /tmp/fonts && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium

COPY . .

EXPOSE 2701

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "2701"]
