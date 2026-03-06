#!/usr/bin/env python3
"""
Quick script to test PostgreSQL connection with different passwords
"""
import psycopg2
import sys

# Common default passwords to try
passwords = ["postgres", "admin", "password", "", "root", "12345"]

print("Testing PostgreSQL connection...")
print("=" * 50)

for pwd in passwords:
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password=pwd,
            database="postgres"  # Connect to default postgres db first
        )
        print(f"✓ SUCCESS! Password is: '{pwd}'")
        print(f"\nUpdate your .env file with:")
        print(f"DATABASE_URL=postgresql://postgres:{pwd}@localhost:5432/jobtracker")
        conn.close()
        sys.exit(0)
    except psycopg2.OperationalError as e:
        if "password authentication failed" in str(e):
            print(f"✗ Wrong password: '{pwd}'")
        elif "does not exist" in str(e):
            print(f"✗ Database doesn't exist (but password '{pwd}' might be correct)")
        else:
            print(f"✗ Error with '{pwd}': {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

print("\n" + "=" * 50)
print("None of the common passwords worked.")
print("\nOptions:")
print("1. Check PostgreSQL installation and ensure it's running")
print("2. Reset PostgreSQL password using pgAdmin or command line")
print("3. Check if PostgreSQL is installed: run 'psql --version'")
