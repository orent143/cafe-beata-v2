#!/usr/bin/env python
"""
Database Update Script for Inventory Cafe System

This script ensures the database has the correct structure, especially 
for the users table with email and created_at fields.
"""

import mysql.connector
import logging
import os
import time
import sys
from mysql.connector import Error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db-update")

# Main database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Warweapons19",
    "database": "cafe_beata"
}

def update_users_table():
    """Update the users table structure to ensure it has all required fields"""
    try:
        logger.info("Connecting to database...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Check if email column exists, if not add it
        cursor.execute("SHOW COLUMNS FROM users LIKE 'email'")
        email_column_exists = cursor.fetchone()
        if not email_column_exists:
            logger.info("Adding email column to users table")
            cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(100) NULL")
            connection.commit()
            logger.info("Email column added successfully")
        else:
            logger.info("Email column already exists")
        
        # Check if created_at column exists, if not add it
        cursor.execute("SHOW COLUMNS FROM users LIKE 'created_at'")
        created_at_column_exists = cursor.fetchone()
        if not created_at_column_exists:
            logger.info("Adding created_at column to users table")
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            connection.commit()
            logger.info("created_at column added successfully")
        else:
            logger.info("created_at column already exists")
        
        # Update existing users to have an email if none exists
        cursor.execute("UPDATE users SET email = CONCAT(username, '@cafebeata.com') WHERE email IS NULL OR email = ''")
        rows_updated = cursor.rowcount
        connection.commit()
        logger.info(f"Updated {rows_updated} users with default email addresses")
        
        cursor.close()
        connection.close()
        logger.info("Database updated successfully")
        return True
    
    except Error as e:
        logger.error(f"Error updating database: {str(e)}")
        if connection:
            connection.rollback()
        return False
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    print("Starting database update...")
    success = update_users_table()
    if success:
        print("Database updated successfully.")
    else:
        print("Database update failed. Check the logs for details.") 