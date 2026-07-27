#!/bin/bash

# set -e

# mkdir -p /backups

# while true
# do
#     timestamp=$(date +"%Y-%m-%d_%H-%M-%S")

#     echo "Creating backup..."

#     pg_dump -U postgres -d studentDB > "/backups/db_${timestamp}.dump"

#     echo "Backup complete."

#     # Keep only newest 30 backups
#     ls -tp /backups/*.dump | tail -n +31 | xargs -r rm

#     sleep "$BACKUP_INTERVAL"
# done

set -e

mkdir -p /backups

while true
do
    timestamp=$(date +"%Y-%m-%d_%H-%M-%S")

    echo "[$(date)] Creating backup..."

    pg_dump \
    -h "$PGHOST" \
    -p "$PGPORT" \
    -U "$PGUSER" \
    -d "$PGDATABASE" \
    -f "/backups/studentDB_${timestamp}.sql"

    echo "[$(date)] Backup complete."

    # Keep only the newest 30 backups
    ls -tp /backups/*.dump 2>/dev/null | tail -n +31 | xargs -r rm

    sleep "$BACKUP_INTERVAL"
done