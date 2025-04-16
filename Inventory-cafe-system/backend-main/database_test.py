#!/usr/bin/env python
"""
Database Test Script for Inventory Cafe System

This script tests the database connection and ensures tables are created correctly.
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
logger = logging.getLogger("db-test")

# Main database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Warweapons19",
    "database": "cafe_beata"
}

# Fallback configurations to try if the main one fails
FALLBACK_CONFIGS = [
    {
        "host": "localhost", 
        "user": "root",
        "password": "",  # Empty password
        "database": "cafe_beata"
    },
    {
        "host": "127.0.0.1",  # Use IP instead of hostname
        "user": "root",
        "password": "Warweapons19",
        "database": "cafe_beata"
    },
    {
        "host": "localhost",
        "user": "root",
        "password": "Warweapons19",
        # No database specified - will try to create it
    }
]

def test_connection(config=None, attempt=0, max_attempts=3):
    """Test the database connection with retries"""
    if config is None:
        config = DB_CONFIG.copy()
    
    if attempt >= max_attempts:
        logger.error(f"Maximum connection attempts ({max_attempts}) reached")
        return False
        
    try:
        logger.info(f"Testing database connection (attempt {attempt+1}/{max_attempts})...")
        logger.info(f"Using config: host={config['host']}, user={config['user']}, db={config.get('database', 'None')}")
        
        # Try to connect without specifying database first if it's missing
        if 'database' not in config:
            temp_config = config.copy()
            connection = mysql.connector.connect(**temp_config)
            
            if connection.is_connected():
                db_info = connection.get_server_info()
                logger.info(f"Connected to MySQL Server version {db_info}")
                
                # Try to create and use the database
                cursor = connection.cursor()
                cursor.execute("CREATE DATABASE IF NOT EXISTS cafe_beata")
                cursor.execute("USE cafe_beata")
                logger.info("Created and using database: cafe_beata")
                
                cursor.close()
                connection.close()
                
                # Update config with database
                config['database'] = 'cafe_beata'
                return True
        else:
            # Connect with specified database
            connection = mysql.connector.connect(**config)
            
            if connection.is_connected():
                db_info = connection.get_server_info()
                logger.info(f"Connected to MySQL Server version {db_info}")
                
                cursor = connection.cursor()
                cursor.execute("SELECT DATABASE();")
                db_name = cursor.fetchone()[0]
                logger.info(f"Connected to database: {db_name}")
                
                cursor.close()
                connection.close()
                logger.info("MySQL connection is working properly")
                return True
                
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        
        # If this was the main config, try updating the global config for future use
        if config == DB_CONFIG and attempt == 0:
            if attempt < len(FALLBACK_CONFIGS):
                fallback = FALLBACK_CONFIGS[attempt]
                logger.info(f"Trying fallback configuration #{attempt+1}")
                if test_connection(fallback, 0, 1):
                    # Update the global config
                    DB_CONFIG.update(fallback)
                    logger.info("Updated global database configuration")
                    return True
        
        # Wait before retrying
        time.sleep(1)
        return test_connection(config, attempt + 1, max_attempts)
        
    return False

def check_tables():
    """Check if required tables exist"""
    try:
        logger.info("Checking if required tables exist...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # List of required tables
        required_tables = [
            "users", 
            "inventoryproduct", 
            "stockin", 
            "category", 
            "suppliers",
            "stock_adjustments"
        ]
        
        # Check each table
        tables_exist = {}
        for table in required_tables:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            result = cursor.fetchone()
            tables_exist[table] = bool(result)
            
            if result:
                logger.info(f"✓ Table '{table}' exists")
                
                # Check table structure
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                logger.info(f"  - Table '{table}' has {len(columns)} columns")
                column_names = [column[0] for column in columns]
                logger.info(f"  - Columns: {', '.join(column_names)}")
            else:
                logger.warning(f"✗ Table '{table}' does not exist")
        
        cursor.close()
        connection.close()
        
        return tables_exist
    except Error as e:
        logger.error(f"Error checking tables: {e}")
        return {}

def create_test_users():
    """Create test users for development"""
    try:
        logger.info("Creating test users...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Check if users table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        users_table_exists = cursor.fetchone()
        
        if not users_table_exists:
            logger.warning("Users table doesn't exist, creating it...")
            
            # Create users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'cafe_staff',
                profile_pic VARCHAR(255),
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            logger.info("Users table created")
        
        # Check if admin user exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin_exists = cursor.fetchone()
        
        if not admin_exists:
            logger.info("Admin user doesn't exist, creating it...")
            
            # Create admin user with plain text password for testing
            cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES ('admin', 'admin123', 'admin')
            """)
            
            logger.info("Admin user created (username: admin, password: admin123)")
        
        # Check if staff user exists
        cursor.execute("SELECT * FROM users WHERE username = 'staff'")
        staff_exists = cursor.fetchone()
        
        if not staff_exists:
            logger.info("Staff user doesn't exist, creating it...")
            
            # Create staff user with plain text password for testing
            cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES ('staff', 'staff123', 'cafe_staff')
            """)
            
            logger.info("Staff user created (username: staff, password: staff123)")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info("Test users creation completed")
    except Error as e:
        logger.error(f"Error creating test users: {e}")

def create_minimum_db_structure():
    """Create the minimum database structure required for the system to work"""
    try:
        logger.info("Creating minimum database structure...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'cafe_staff',
            profile_pic VARCHAR(255),
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create category table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INT AUTO_INCREMENT PRIMARY KEY,
            CategoryName VARCHAR(100) NOT NULL,
            CategoryType VARCHAR(50) NOT NULL,
            Icon VARCHAR(50),
            CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create suppliers table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            SupplierName VARCHAR(255) NOT NULL,
            ContactPerson VARCHAR(255),
            ContactNumber VARCHAR(20),
            Email VARCHAR(255),
            Address TEXT,
            Status ENUM('Active', 'Inactive') DEFAULT 'Active',
            CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create inventoryproduct table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventoryproduct (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ProductName VARCHAR(255) NOT NULL,
            ItemCode VARCHAR(50) NOT NULL,
            Description TEXT,
            Price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
            Quantity INT NOT NULL DEFAULT 0,
            Threshold INT NOT NULL DEFAULT 0,
            InStock ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
            SupplierID INT,
            CategoryID INT,
            ProcessType VARCHAR(50) DEFAULT 'Standard',
            ProductImage VARCHAR(255),
            CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info("Minimum database structure created successfully")
    except Error as e:
        logger.error(f"Error creating minimum database structure: {e}")

if __name__ == "__main__":
    print("=" * 80)
    print(" INVENTORY CAFE SYSTEM DATABASE TEST")
    print("=" * 80)
    
    connection_successful = test_connection()
    
    if connection_successful:
        tables = check_tables()
        
        # Check if we need to create minimum structure
        missing_tables = [table for table, exists in tables.items() if not exists]
        if missing_tables:
            logger.warning(f"Missing tables: {', '.join(missing_tables)}")
            logger.info("Creating minimum database structure...")
            create_minimum_db_structure()
        
        create_test_users()
        
        # Write DB_CONFIG to a Python file for reuse
        try:
            with open('model/db_config.py', 'w') as f:
                f.write("# Auto-generated database configuration\n")
                f.write("DB_CONFIG = {\n")
                for key, value in DB_CONFIG.items():
                    f.write(f"    \"{key}\": \"{value}\",\n")
                f.write("}\n")
            logger.info("Generated db_config.py with successful configuration")
        except Exception as e:
            logger.error(f"Failed to write db_config.py: {e}")
        
        print("\nTest completed successfully. The database connection is working.")
        print("\nTest users available:")
        print("  - Admin: username=admin, password=admin123")
        print("  - Staff: username=staff, password=staff123")
        print("\nYou can now start the Inventory Cafe System with:")
        print("  python -m uvicorn main:app --reload --port 8001")
    else:
        print("\nTest failed. Please check your database configuration.")
        print("Make sure MySQL is running and the credentials are correct.")
        print("\nTried the following configurations:")
        print(f"  - Main: {DB_CONFIG}")
        for i, config in enumerate(FALLBACK_CONFIGS):
            print(f"  - Fallback #{i+1}: {config}")
        
        # Ask if the user wants to enter database details manually
        print("\nWould you like to enter database details manually? (y/n)")
        choice = input().strip().lower()
        
        if choice == 'y':
            print("\nEnter database details:")
            host = input("Host (default: localhost): ") or "localhost"
            user = input("Username (default: root): ") or "root"
            password = input("Password: ")
            database = input("Database (default: cafe_beata): ") or "cafe_beata"
            
            # Update config
            DB_CONFIG.update({
                "host": host,
                "user": user,
                "password": password,
                "database": database
            })
            
            print("\nTrying with new configuration...")
            if test_connection():
                check_tables()
                create_test_users()
                
                print("\nTest completed successfully with your configuration.")
                print("You can now start the Inventory Cafe System.")
            else:
                print("\nStill unable to connect. Please check your MySQL installation.")
                sys.exit(1)
    
    print("=" * 80) 