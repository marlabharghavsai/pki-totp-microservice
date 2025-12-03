# =========================
# Stage 1: Builder
# =========================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install Python deps using requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# =========================
# Stage 2: Runtime
# =========================
FROM python:3.11-slim

# Set timezone to UTC
ENV TZ=UTC

WORKDIR /app

# Install cron + timezone data
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        cron \
        tzdata && \
    rm -rf /var/lib/apt/lists/*

# Configure timezone to UTC
RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" > /etc/timezone

# Copy Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy app code & scripts
COPY app ./app
COPY scripts ./scripts

# Copy cron config
COPY cron/2fa-cron /etc/cron.d/2fa-cron

# Copy keys
COPY student_private.pem .
COPY student_public.pem .
COPY instructor_public.pem .

# Set permissions
RUN chmod 755 scripts/log_2fa_cron.py && \
    chmod 644 /etc/cron.d/2fa-cron

# Register cron job
RUN crontab /etc/cron.d/2fa-cron

# Create volume mount points
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Expose API port
EXPOSE 8080

# Start cron and API server
CMD sh -c "cron && uvicorn app.main:app --host 0.0.0.0 --port 8080"
