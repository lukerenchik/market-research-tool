# scripts/setup_db.sh
#!/bin/bash

echo "Waiting for database to be ready..."
until psql "$DATABASE_URL" -c '\q' 2>/dev/null; do
    sleep 1
done

echo "Running migrations..."
psql "$DATABASE_URL" -f db/migrations/001_initial_schema.sql

echo "Running GICS seed..."
psql "$DATABASE_URL" -f db/seeds/gics.sql

echo "Database ready."