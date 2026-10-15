FROM python:3.11-slim

ARG DEBIAN_FRONTEND=noninteractive

# Chromium + Playwright ke liye zaroori system libraries install karo (root ke roop mein)
RUN apt-get update -q && \
    apt-get install -y -qq --no-install-recommends \
    xvfb \
    libxcomposite1 \
    libxdamage1 \
    libatk1.0-0 \
    libasound2 \
    libdbus-1-3 \
    libnspr4 \
    libgbm1 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libnss3 \
    libxrandr2 \
    libxfixes3 \
    libx11-xcb1 \
    libxcursor1 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libcairo2 \
    libglib2.0-0 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements install karo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright Chromium browser install karo (system libs already installed hain)
RUN playwright install chromium

# Bot code copy karo
COPY . .

ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright
ENV PYTHONUNBUFFERED=1

CMD ["python", "NetflixTrailV3.py"]
