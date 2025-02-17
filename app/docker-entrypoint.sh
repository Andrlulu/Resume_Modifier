#!/bin/bash
set -e

# Wait for Postgres to be ready
echo "Waiting for postgres..."
while ! nc -z $DB_HOST 5432; do
  sleep 1
done
echo "PostgreSQL started"

# Initialize the database
python -c "from app.server import app; from app.init_db import init_db; init_db()"

# Start the Flask application
exec "$@" 