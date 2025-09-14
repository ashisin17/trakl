FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . ./rec

# Expose port
EXPOSE 8001

# Set PYTHONPATH and run the application
ENV PYTHONPATH=/app
# Use uvicorn and explicitly set app directory so reload subprocesses can import the `rec` package
CMD ["uvicorn", "rec.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload", "--app-dir", "/app"]
