# Use Python 3.11 slim image
FROM python:3.11-slim

WORKDIR /app

# Install system and PostgreSQL client requirements
RUN apt-get update \
 && apt-get install -y gcc libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and entrypoint
COPY . .

# Copy entrypoint script
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# Use the entrypoint to wait for Postgres and then start Uvicorn
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
