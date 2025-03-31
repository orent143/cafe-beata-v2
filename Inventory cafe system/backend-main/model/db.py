# model/db.py
import mysql.connector
from mysql.connector import Error
import logging
import contextlib
from functools import wraps
import time
import threading
import gc

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("inventory-system-backend")

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Warweapons19",  # Match password from cafe-beata-main
    "database": "cafe_beata"
}

# Connection pool
connection_pool = None
connection_lock = threading.RLock()  # Add a lock for thread safety
active_connections = set()  # Track active connections
last_cleanup_time = time.time()

def init_connection_pool():
    """Initialize the database connection pool"""
    global connection_pool, last_cleanup_time
    with connection_lock:
        try:
            if connection_pool is not None:
                # Try to close any existing connections in the pool
                logger.info("Cleaning up existing connection pool...")
                try:
                    connection_pool._remove_connections()
                except:
                    logger.warning("Could not clean up existing connection pool, recreating...")
            
            # Force garbage collection to clean up any lingering connections
            gc.collect()
            
            # Create a new connection pool
            connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="inventory_pool",
                pool_size=32,  # Set to maximum allowed value (32)
                pool_reset_session=True,
                autocommit=False,
                **DB_CONFIG
            )
            
            # Reset active connections tracking
            active_connections.clear()
            
            # Reset cleanup timer
            last_cleanup_time = time.time()
            
            logger.info("Database connection pool initialized successfully")
        except Error as e:
            logger.error(f"Error initializing database connection pool: {e}")
            raise

def force_cleanup_connections():
    """Force cleanup of all active connections"""
    global active_connections
    with connection_lock:
        cleanup_count = 0
        remove_list = []
        
        # First collect dead connections
        for conn in active_connections:
            try:
                if not conn.is_connected():
                    remove_list.append(conn)
                    cleanup_count += 1
            except:
                # If we can't check, assume it's dead
                remove_list.append(conn)
                cleanup_count += 1
        
        # Then remove them from the set
        for conn in remove_list:
            try:
                conn.close()
            except:
                pass
            active_connections.discard(conn)
        
        # If we're still over 25 connections, force close the oldest
        if len(active_connections) > 25:
            extra_to_close = len(active_connections) - 25
            close_list = list(active_connections)[:extra_to_close]
            
            for conn in close_list:
                try:
                    conn.close()
                    active_connections.discard(conn)
                    cleanup_count += 1
                except:
                    pass
        
        if cleanup_count > 0:
            logger.info(f"Forced cleanup of {cleanup_count} connections. Active: {len(active_connections)}")
        
        return cleanup_count

def test_connection():
    """Test database connection and return True if successful, False otherwise"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_info = cursor.fetchone()
            logger.info(f"Connected to database: {db_info[0]}")
            cursor.close()
            connection.close()
            return True
        else:
            logger.error("Failed to connect to database")
            return False
    except Error as e:
        logger.error(f"Error connecting to database: {e}")
        return False

def get_db():
    """Get a connection from the pool and ensure it's properly closed after use"""
    global connection_pool, active_connections, last_cleanup_time
    
    # Check if we need to do periodic cleanup (every 5 seconds max)
    current_time = time.time()
    if current_time - last_cleanup_time > 5:
        with connection_lock:
            if current_time - last_cleanup_time > 5:  # Double-check after lock
                force_cleanup_connections()
                last_cleanup_time = current_time
    
    if connection_pool is None:
        with connection_lock:
            if connection_pool is None:  # Double-check after acquiring lock
                init_connection_pool()
    
    # If we're above 28 active connections, force cleanup before continuing
    if len(active_connections) > 28:
        with connection_lock:
            if len(active_connections) > 28:  # Double-check after lock
                force_cleanup_connections()
    
    # Retry logic for getting a connection
    max_retries = 5
    retry_delay = 0.5  # seconds
    
    for attempt in range(max_retries):
        try:
            connection = connection_pool.get_connection()
            connection.autocommit = False  # Ensure we have explicit transaction control
            
            # Test that the connection is actually valid
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                
                # Add to active connections set
                with connection_lock:
                    active_connections.add(connection)
                
                return connection
            except Error as conn_test_error:
                logger.warning(f"Got invalid connection from pool: {conn_test_error}")
                try:
                    connection.close()
                except:
                    pass
                raise
                
        except Error as e:
            if "pool exhausted" in str(e).lower():
                logger.warning(f"Connection pool exhausted on attempt {attempt+1}/{max_retries}")
                
                # Try cleaning up before creating a direct connection
                cleaned = force_cleanup_connections()
                
                # If we cleaned up some connections, try the pool again
                if cleaned > 0 and attempt < max_retries - 1:
                    continue
                    
                # If we're at the last attempt, create a direct connection
                if attempt == max_retries - 1:
                    logger.warning("Creating temporary direct connection due to pool exhaustion")
                    try:
                        temp_conn = mysql.connector.connect(**DB_CONFIG)
                        temp_conn.autocommit = False
                        
                        # Add to active connections for tracking
                        with connection_lock:
                            active_connections.add(temp_conn)
                            
                        return temp_conn
                    except Error as direct_conn_error:
                        logger.error(f"Failed to create direct connection: {direct_conn_error}")
            
            if attempt < max_retries - 1:
                logger.warning(f"Connection pool retry {attempt+1}/{max_retries}: {e}")
                time.sleep(retry_delay)
                # Exponential backoff
                retry_delay *= 2
            else:
                logger.error(f"Error getting database connection from pool after {max_retries} retries: {e}")
                # If all retries fail, try to re-initialize the pool
                try:
                    with connection_lock:
                        init_connection_pool()
                    connection = connection_pool.get_connection()
                    connection.autocommit = False
                    
                    # Add to active connections
                    with connection_lock:
                        active_connections.add(connection)
                        
                    return connection
                except Error as reinit_error:
                    logger.error(f"Failed to reinitialize connection pool: {reinit_error}")
                    raise

@contextlib.contextmanager
def db_connection():
    """Context manager for database connections to ensure proper release"""
    connection = None
    try:
        connection = get_db()
        yield connection
        # If no exception occurs, commit the transaction
        try:
            connection.commit()
        except Error as commit_error:
            logger.error(f"Error committing transaction: {commit_error}")
            try:
                connection.rollback()
            except:
                pass
    except Exception as e:
        if connection:
            try:
                connection.rollback()
                logger.error(f"Transaction rolled back due to error: {e}")
            except Error as rollback_error:
                logger.error(f"Error rolling back transaction: {rollback_error}")
        raise
    finally:
        if connection:
            try:
                # Remove from active connections set
                with connection_lock:
                    active_connections.discard(connection)
                
                connection.close()
                logger.debug("Connection closed and returned to pool")
            except Error as e:
                logger.error(f"Error closing database connection: {e}")
                # Force pool cleanup if connections are problematic
                if "MySQL Connection not available" in str(e) or "pool exhausted" in str(e):
                    try:
                        with connection_lock:
                            init_connection_pool()
                    except:
                        logger.error("Failed to reinitialize connection pool during cleanup")

def db_transaction(func):
    """Decorator to handle database transactions"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        with db_connection() as conn:
            # Replace the db dependency with our connection
            for i, arg in enumerate(args):
                if arg.__class__.__name__ == 'MySQLConnection':
                    args = list(args)
                    args[i] = conn
                    args = tuple(args)
                    break
            else:
                if 'db' in kwargs:
                    kwargs['db'] = conn
                else:
                    kwargs['db'] = conn
            
            return await func(*args, **kwargs)
    return wrapper

def get_db_connection():
    """
    Get a direct database connection (not from pool)
    For use in functions that don't use the dependency injection pattern
    WARNING: This bypasses the connection pool. Make sure to close the connection manually!
    """
    try:
        # First, try to get a connection from the pool
        if connection_pool is not None:
            try:
                conn = connection_pool.get_connection()
                
                # Add to active connections
                with connection_lock:
                    active_connections.add(conn)
                    
                return conn
            except Error as pool_error:
                logger.warning(f"Could not get connection from pool, creating direct connection: {pool_error}")
        
        # If pool is not available or failed, create direct connection
        connection = mysql.connector.connect(**DB_CONFIG)
        logger.warning("Direct database connection created. Ensure it's properly closed!")
        
        # Add to active connections
        with connection_lock:
            active_connections.add(connection)
            
        return connection
    except Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise

def ensure_tables_exist():
    """
    Ensure that all necessary database tables exist
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First, ensure the database exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS cafe_beata")
        cursor.execute("USE cafe_beata")
        
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
        
        # Create a category for Ready-Made products if it doesn't exist
        cursor.execute("""
        INSERT IGNORE INTO category (CategoryName, CategoryType, Icon)
        VALUES ('Ready Made', 'Product', 'coffee')
        """)
        
        # Check and create inventoryproduct table if it doesn't exist
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
        
        # Drop existing stock_adjustments table if it exists to avoid foreign key issues
        cursor.execute("DROP TABLE IF EXISTS stock_adjustments")
        
        # Create the stock_adjustments table with simplified foreign key
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_adjustments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            previous_quantity INT NOT NULL,
            new_quantity INT NOT NULL,
            action VARCHAR(20) NOT NULL,
            reason TEXT,
            adjustment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_product_id (product_id)
        )
        """)
        
        # Drop existing stockin table if it exists to avoid foreign key issues
        cursor.execute("DROP TABLE IF EXISTS stockin")
        
        # Create the stockin table with simplified foreign key
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stockin (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ProductID INT NOT NULL,
            Quantity INT NOT NULL,
            UnitCost DECIMAL(10, 2) NOT NULL,
            TotalCost DECIMAL(10, 2) NOT NULL,
            ExpiryDate DATE,
            InvoiceNumber VARCHAR(50),
            StockImage VARCHAR(255),
            Notes TEXT,
            DateStocked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_product_id (ProductID)
        )
        """)
        
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
        
        # Create report tables if they don't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_reports (
            ReportID INT AUTO_INCREMENT PRIMARY KEY,
            ProductID INT,
            ProductName VARCHAR(255),
            Quantity INT,
            UnitPrice DECIMAL(10, 2),
            CategoryID INT,
            Status VARCHAR(50),
            ReportDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Image VARCHAR(255)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_reports (
            ReportID INT AUTO_INCREMENT PRIMARY KEY,
            StockID INT,
            StockName VARCHAR(255),
            Quantity INT,
            CostPrice DECIMAL(10, 2),
            SupplierID INT,
            Status VARCHAR(50),
            ReportDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Image VARCHAR(255)
        )
        """)
        
        # Create categories table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            CategoryName VARCHAR(255) NOT NULL,
            ImagePath VARCHAR(255),
            CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        connection.commit()
        logger.info("Database tables verified and created if needed")
        
        cursor.close()
        connection.close()
        
        # Call the function to ensure users are set up
        try:
            from .users import ensure_users_table_exists
            ensure_users_table_exists()
        except Exception as e:
            logger.error(f"Error in user setup, but continuing: {e}")
        
    except Error as e:
        logger.error(f"Error ensuring tables exist: {e}")
        # Don't re-raise, just log the error
        # This allows the application to continue even if table setup fails

def cleanup_connection_pool():
    """Periodically cleanup the connection pool to prevent stale connections"""
    global connection_pool
    logger.info("Running scheduled connection pool cleanup")
    try:
        with connection_lock:
            force_cleanup_connections()
            if connection_pool is not None:
                # Get all active connections and close them
                logger.info("Reinitializing connection pool...")
                init_connection_pool()
    except Exception as e:
        logger.error(f"Error during connection pool cleanup: {e}")
    finally:
        # Schedule the next cleanup in 5 minutes (reduced from 10)
        cleanup_thread = threading.Timer(300, cleanup_connection_pool)
        cleanup_thread.daemon = True
        cleanup_thread.start()

def start_connection_pool_cleanup():
    """Start the periodic connection pool cleanup"""
    cleanup_thread = threading.Timer(300, cleanup_connection_pool)  # Run every 5 minutes
    cleanup_thread.daemon = True
    cleanup_thread.start()
    logger.info("Connection pool cleanup scheduler started")