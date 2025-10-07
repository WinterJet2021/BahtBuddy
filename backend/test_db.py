"""
test_db.py
-----------------------
Checks if Flask + SQLAlchemy can connect to bahtbuddy.db
and lists all tables in the database.
"""

from app import create_app
from app.extensions import db
from sqlalchemy import text

print("🔧 Starting Flask app for BahtBuddy DB test...")

try:
    # Initialize the Flask app
    app = create_app()
    print("✅ Flask app created successfully!")

    # Use app context to access the database
    with app.app_context():
        print("🔍 Testing database connection...")
        # Run a simple query to list all tables
        result = db.session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table';")
        )
        tables = [row[0] for row in result]

        print("✅ Database connection successful!")
        if tables:
            print("📋 Tables found in bahtbuddy.db:")
            for table in tables:
                print(f"   • {table}")
        else:
            print("⚠️ No tables found in the database.")
except Exception as e:
    print("❌ Database connection failed:")
    print("Error details:", e)
