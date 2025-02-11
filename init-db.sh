#!/bin/bash

echo "Waiting for PostgreSQL to start..."

# Keep checking if PostgreSQL is ready
while ! PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1" &> /dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 5  # Increase wait time
done

echo "PostgreSQL is ready!"
# Check if database exists
DB_EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -tAc "SELECT 1 FROM pg_database WHERE datname='chatbot'")

if [ "$DB_EXISTS" == "1" ]; then
  echo "Database 'chatbot' already exists."
else
  echo "Creating database 'chatbot'..."
  PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -c "CREATE DATABASE chatbot;"
  echo "Database 'chatbot' created successfully."
fi
