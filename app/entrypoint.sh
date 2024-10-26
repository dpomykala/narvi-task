#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Setting up the database..."

# Reset the database on startup (for demo purposes only)
if [ -f "db.sqlite3" ]; then
  echo "Removing the old database file..."
  rm db.sqlite3
fi

echo "Running migrations..."
poetry run python manage.py migrate

exec "$@"
