"""
restart.py

Script to manage database table creation for the Flask application. 
It allows two options: dropping and recreating all tables, or creating missing tables only.

Usage:
- Option 1: Drop all tables and recreate them (data loss warning).
- Option 2: Create tables only if they do not exist (safe).

Note:
- This script must not be run in a production environment.
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from myapp import app
from models.models_definitions import db

if os.getenv("FLASK_ENV") == "production":
    print("Execution of this script is not allowed in the production environment.")
    sys.exit()

print("Warning: This script interacts with the database.")
print("Please choose one of the following options:")
print("1. Drop all tables and recreate them (This will erase all existing data!)")
print("2. Create tables only if they do not already exist (Safe option)")

choice = input("Enter your choice (1 or 2): ").strip()

with app.app_context():
    if choice == "1":
        db.drop_all()
        db.create_all()
        print("All tables have been dropped and recreated successfully.")
    elif choice == "2":
        db.create_all()
        print("Missing tables have been created successfully.")
    else:
        print("Invalid choice. No action was performed.")
