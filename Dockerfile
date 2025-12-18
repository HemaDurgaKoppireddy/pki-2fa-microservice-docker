# =========================
# Stage 1: Builder
# =========================
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# =========================
# Stage 2: Runtime
# =========================
FROM python:3.11-slim

# Set timezone to UTC (CRITICAL)
ENV TZ=UTC

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       cron \
       tzdata \
    && ln -snf /usr/share/zoneinfo/UTC /etc/localtime \
    && echo "UTC" > /etc/timezone \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application files
COPY app ./app
COPY scripts ./scripts
COPY cron /cron
COPY student_private.pem .
COPY instructor_public.pem .
COPY requirements.txt .

# Setup cron job
RUN chmod 0644 /cron/cronjob \
    && crontab /cron/cronjob

# Create volume mount points
RUN mkdir -p /data /cron \
    && chmod 755 /data /cron

# Expose API port
EXPOSE 8080

# 🔑 IMPORTANT FIX:
# Run cron in background and keep uvicorn in foreground
CMD ["sh", "-c", "cron && uvicorn app.main:app --host 0.0.0.0 --port 8080"]
