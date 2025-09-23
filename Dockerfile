# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libxml2-dev \
        libxslt-dev \
        libffi-dev \
        libssl-dev \
        pkg-config \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Create logs directory
RUN mkdir -p /app/logs

# Set default environment variables (can be overridden)
ENV MONGODB_URI=""
ENV MONGODB_DATABASE=cineulagam
ENV MONGODB_COLLECTION=posted_articles
ENV BLOGGER_BLOG_ID=""
ENV BLOGGER_CREDENTIALS_FILE=credentials.json
ENV BLOGGER_TOKEN_FILE=token.pickle
ENV TELEGRAM_BOT_TOKEN=""
ENV TELEGRAM_CHANNEL_ID=""
ENV LOG_LEVEL=INFO
ENV LOG_FILE=cineulagam_publisher.log

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Add labels for better metadata
LABEL maintainer="your-email@example.com"
LABEL description="Cineulagam Publisher - Automated content publishing application"
LABEL version="1.0.0"

# Run the application
CMD ["python", "app.py"]
