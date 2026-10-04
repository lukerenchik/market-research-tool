#!/usr/bin/env bash
# scripts/setup_db.sh
#
# Applies every SQL migration in db/migrations/ in order, then loads the GICS
# seed data. Safe to re-run: applied migrations are recorded in
# schema_migrations and skipped, and the GICS seed only runs on an empty
# gics_sectors table.
#
# Usage: DATABASE_URL=postgresql://... ./scripts/setup_db.sh

set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL must be set, e.g. postgresql://postgres:password@localhost:6543/postgres}"

PSQL=(psql "$DATABASE_URL" -v ON_ERROR_STOP=1 --quiet --no-psqlrc)
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Waiting for database to be ready..."
until "${PSQL[@]}" -c '\q' 2>/dev/null; do
    sleep 1
done

"${PSQL[@]}" -c "
    CREATE TABLE IF NOT EXISTS schema_migrations (
        filename   TEXT PRIMARY KEY,
        applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );"

echo "Running migrations..."
for file in "$ROOT"/db/migrations/*.sql; do
    name="$(basename "$file")"
    applied="$("${PSQL[@]}" -tA -c "SELECT 1 FROM schema_migrations WHERE filename = '$name'")"
    if [[ "$applied" == "1" ]]; then
        echo "  skip   $name (already applied)"
        continue
    fi
    echo "  apply  $name"
    "${PSQL[@]}" -1 -o /dev/null -f "$file" -c "INSERT INTO schema_migrations (filename) VALUES ('$name')"
done

seeded="$("${PSQL[@]}" -tA -c "SELECT 1 FROM gics_sectors LIMIT 1")"
if [[ "$seeded" == "1" ]]; then
    echo "GICS seed: already loaded, skipping."
else
    echo "Running GICS seed..."
    "${PSQL[@]}" -1 -o /dev/null -f "$ROOT/db/seeds/gics.sql"
fi

echo "Database ready. Next: python scripts/seed_tickers.py db/seeds/sp500_tickers.csv"
