# ------------ Base Stage ------------
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ------------ Final Stage ------------
FROM python:3.11-slim AS final

# Set working directory
WORKDIR /app

# Copy everything from the base stage (including installed dependencies)
COPY --from=base /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy app source code
COPY . .

# Set environment variable to production
ENV FLASK_ENV=production

# Expose the port Flask will run on
EXPOSE 8502

# Start the app with Gunicorn (WSGI server)
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8502", "--workers", "4"]
