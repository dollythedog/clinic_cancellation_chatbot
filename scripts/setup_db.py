#!/usr/bin/env python3
"""
Create clinic_chatbot database on existing PostgreSQL server
"""

import sys

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connection details (update if needed)
DBHOST = "192.168.1.220"
DBPORT = 5432
DBUSER = "postgres"
DBPASSWORD = "securepassword"
NEW_DATABASE = "clinic_chatbot"


def create_database():
    """Create the clinic_chatbot database"""
    try:
        # Connect to default 'postgres' database to create new database
        print(f"🔌 Connecting to {DBHOST}:5432...")
        conn = psycopg2.connect(
            dbname="postgres", user=DBUSER, password=DBPASSWORD, host=DBHOST, port=DBPORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (NEW_DATABASE,))

        if cursor.fetchone():
            print(f"✅ Database '{NEW_DATABASE}' already exists")
        else:
            # Create database
            cursor.execute(f"CREATE DATABASE {NEW_DATABASE}")
            print(f"✅ Created database '{NEW_DATABASE}'")

        cursor.close()
        conn.close()

        # Now apply schema
        print("\n📋 Applying schema...")
        conn = psycopg2.connect(
            dbname=NEW_DATABASE, user=DBUSER, password=DBPASSWORD, host=DBHOST, port=DBPORT
        )
        cursor = conn.cursor()

        # Read and execute schema.sql
        schema_path = "scripts/schema.sql"
        print(f"📂 Reading {schema_path}...")

        with open(schema_path, encoding="utf-8") as f:
            schema_sql = f.read()

        cursor.execute(schema_sql)
        conn.commit()

        print("✅ Schema applied successfully!")

        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        tables = cursor.fetchall()
        print(f"\n📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")

        cursor.close()
        conn.close()

        print("\n✅ Setup complete!")
        print("\nAdd this to your .env file:")
        print(f"DATABASE_URL=postgresql://{DBUSER}:{DBPASSWORD}@{DBHOST}:{DBPORT}/{NEW_DATABASE}")

    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ schema.sql not found. Run this from project root.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_database()
