"""
Migration script to add datetime columns to all database tables.
This script adds created_at and updated_at columns to existing tables.

Run this once to migrate your existing database:
    python migrate_add_datetime.py
"""

import os
import sqlite3
from datetime import datetime

# Determine database path based on environment
if os.environ.get('RUNNING_IN_DOCKER'):
    DB_PATH = '/app/data/myfuckingdb.db'
else:
    DB_PATH = '../myfuckingdb.db'

def migrate_database():
    """Add datetime columns to all tables."""
    print(f"Connecting to database: {DB_PATH}")
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()

    # Get current timestamp for existing records
    current_timestamp = datetime.now().isoformat()

    try:
        # Migrate qr2loc table
        print("\nMigrating qr2loc table...")
        try:
            cur.execute("ALTER TABLE qr2loc ADD COLUMN created_at TEXT;")
            cur.execute(f"UPDATE qr2loc SET created_at = ? WHERE created_at IS NULL;", (current_timestamp,))
            print("✓ Added created_at to qr2loc")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✓ created_at already exists in qr2loc")
            else:
                raise

        # Migrate vote2qr table (needs both created_at and updated_at)
        print("\nMigrating vote2qr table...")
        try:
            cur.execute("ALTER TABLE vote2qr ADD COLUMN created_at TEXT;")
            cur.execute(f"UPDATE vote2qr SET created_at = ? WHERE created_at IS NULL;", (current_timestamp,))
            print("✓ Added created_at to vote2qr")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✓ created_at already exists in vote2qr")
            else:
                raise

        try:
            cur.execute("ALTER TABLE vote2qr ADD COLUMN updated_at TEXT;")
            cur.execute(f"UPDATE vote2qr SET updated_at = ? WHERE updated_at IS NULL;", (current_timestamp,))
            print("✓ Added updated_at to vote2qr")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✓ updated_at already exists in vote2qr")
            else:
                raise

        # Migrate email_signups table
        print("\nMigrating email_signups table...")
        try:
            cur.execute("ALTER TABLE email_signups ADD COLUMN created_at TEXT;")
            cur.execute(f"UPDATE email_signups SET created_at = ? WHERE created_at IS NULL;", (current_timestamp,))
            print("✓ Added created_at to email_signups")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✓ created_at already exists in email_signups")
            else:
                raise

        # Migrate user_sports table
        print("\nMigrating user_sports table...")
        try:
            cur.execute("ALTER TABLE user_sports ADD COLUMN created_at TEXT;")
            cur.execute(f"UPDATE user_sports SET created_at = ? WHERE created_at IS NULL;", (current_timestamp,))
            print("✓ Added created_at to user_sports")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✓ created_at already exists in user_sports")
            else:
                raise

        # Commit all changes
        db.commit()
        print("\n✓ Migration completed successfully!")

        # Show summary
        print("\n=== Migration Summary ===")
        for table in ['qr2loc', 'vote2qr', 'email_signups', 'user_sports']:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            count = cur.fetchone()[0]
            print(f"{table}: {count} records updated")

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        cur.close()
        db.close()

if __name__ == '__main__':
    migrate_database()
