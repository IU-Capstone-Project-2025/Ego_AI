#!/bin/bash
set -ex

# Wait for Postgres
echo "Waiting for PostgreSQL at $DATABASE_URL..."
until python - <<EOF
import os, sys
from urllib.parse import urlparse
import psycopg2
url = os.getenv("DATABASE_URL")
print(f"[DEBUG] DATABASE_URL: {url}")
# Remove +asyncpg from the URL for psycopg2 compatibility
url = url.replace("+asyncpg", "")
print(f"[DEBUG] Cleaned URL for psycopg2: {url}")
parts = urlparse(url)
print(f"[DEBUG] Connecting with dbname={parts.path.lstrip('/')} user={parts.username} host={parts.hostname} port={parts.port}")
conn = psycopg2.connect(
    dbname=parts.path.lstrip('/'),
    user=parts.username,
    password=parts.password,
    host=parts.hostname,
    port=parts.port
)
conn.close()
EOF
do
  echo -n "."
  sleep 1
done

ls -l /app
echo "PostgreSQL is up — running Alembic migrations"
cd /app
alembic upgrade head
echo "Database initialized — launching the app"
exec "$@"