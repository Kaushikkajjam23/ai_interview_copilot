# reset_db.py
import os
import sqlite3
import shutil

# Path to your database file
db_path = "app.db"

# 1. Delete the database file if it exists
if os.path.exists(db_path):
    print(f"Deleting existing database file: {db_path}")
    os.remove(db_path)
    print("Database file deleted.")
else:
    print("No existing database file found.")

# 2. Delete all migration files in the versions directory
versions_dir = "alembic/versions"
if os.path.exists(versions_dir):
    print(f"Cleaning up migration files in {versions_dir}")
    for file in os.listdir(versions_dir):
        if file.endswith(".py") or file.endswith(".pyc"):
            os.remove(os.path.join(versions_dir, file))
    print("Migration files deleted.")
else:
    print("No versions directory found.")

print("Database reset complete. Now you can create a new migration.")