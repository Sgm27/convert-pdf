FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

# Install Windows fonts (Arial, Times New Roman, Calibri, etc.)
RUN apt-get update && apt-get install -y \
    wget \
    cabextract \
    xfonts-utils \
    fontconfig \
    && wget -q https://downloads.sourceforge.net/project/mscorefonts2/rpms/msttcorefonts-2.6-1.noarch.rpm \
    && apt-get install -y rpm \
    && rpm -Uvh --nodeps msttcorefonts-2.6-1.noarch.rpm \
    && fc-cache -f -v \
    && rm -f msttcorefonts-2.6-1.noarch.rpm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install additional fonts for Vietnamese support
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    fonts-dejavu \
    fonts-noto \
    fonts-noto-cjk \
    && fc-cache -f -v \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium

COPY . .

EXPOSE 2701

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "2701"]
