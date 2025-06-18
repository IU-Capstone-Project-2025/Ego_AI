#!/bin/bash
set -e

# Wait for Postgres
echo "Waiting for PostgreSQL at $DATABASE_URL..."
until python - <<EOF
import os, sys
from urllib.parse import urlparse
import psycopg2
url = os.getenv("DATABASE_URL")
parts = urlparse(url)
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

echo "PostgreSQL is up — launching the app"
exec "$@"