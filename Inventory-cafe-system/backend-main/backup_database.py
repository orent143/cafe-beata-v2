import os
import sys
import time
import logging
import subprocess
import datetime
import shutil
import json
import configparser
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("database_backup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("db-backup")

# Default backup settings
DEFAULT_CONFIG = {
    "mysql": {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "cafe_beata",
        "port": "3306"
    },
    "backup": {
        "backup_dir": "backups",
        "keep_days": "30",
        "compression": "gzip"
    }
}

# Create config parser and set defaults
config = configparser.ConfigParser()
for section, options in DEFAULT_CONFIG.items():
    if not config.has_section(section):
        config.add_section(section)
    for option, value in options.items():
        config.set(section, option, value)

# Try to read config file
config_file = Path("backup_config.ini")
if config_file.exists():
    try:
        config.read(config_file)
        logger.info(f"Loaded configuration from {config_file}")
    except Exception as e:
        logger.error(f"Error reading config file: {e}")
else:
    # Create default config file
    try:
        with open(config_file, 'w') as f:
            config.write(f)
        logger.info(f"Created default configuration file at {config_file}")
    except Exception as e:
        logger.error(f"Error creating default config file: {e}")

# Get configuration values
DB_HOST = config.get("mysql", "host")
DB_USER = config.get("mysql", "user")
DB_PASSWORD = config.get("mysql", "password")
DB_NAME = config.get("mysql", "database")
DB_PORT = config.get("mysql", "port")
BACKUP_DIR = config.get("backup", "backup_dir")
KEEP_DAYS = int(config.get("backup", "keep_days"))
COMPRESSION = config.get("backup", "compression")

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

def get_timestamp():
    """Get a timestamp for the backup filename"""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def backup_database():
    """Create a backup of the MySQL database"""
    timestamp = get_timestamp()
    backup_file = os.path.join(BACKUP_DIR, f"{DB_NAME}_{timestamp}.sql")
    
    if COMPRESSION == "gzip":
        backup_file += ".gz"
        command = f"mysqldump --host={DB_HOST} --port={DB_PORT} --user={DB_USER} --password={DB_PASSWORD} " \
                 f"--single-transaction --routines --triggers --events " \
                 f"{DB_NAME} | gzip > {backup_file}"
    else:
        command = f"mysqldump --host={DB_HOST} --port={DB_PORT} --user={DB_USER} --password={DB_PASSWORD} " \
                 f"--single-transaction --routines --triggers --events " \
                 f"{DB_NAME} > {backup_file}"
    
    start_time = time.time()
    
    try:
        logger.info(f"Starting database backup to {backup_file}")
        
        # Use shell=True cautiously, but it's needed for the pipe in gzip command
        # For production, consider using a more secure approach
        subprocess.run(command, shell=True, check=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Get file size
        file_size = os.path.getsize(backup_file)
        file_size_mb = file_size / (1024 * 1024)
        
        logger.info(f"Backup completed successfully in {duration:.2f} seconds")
        logger.info(f"Backup file size: {file_size_mb:.2f} MB")
        
        # Record backup metadata
        record_backup_metadata(backup_file, timestamp, duration, file_size_mb, "success")
        
        # Cleanup old backups
        cleanup_old_backups()
        
        return True, backup_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Database backup failed: {e}")
        record_backup_metadata(backup_file, timestamp, time.time() - start_time, 0, "failed", str(e))
        return False, None
    except Exception as e:
        logger.error(f"An error occurred during backup: {e}")
        record_backup_metadata(backup_file, timestamp, time.time() - start_time, 0, "failed", str(e))
        return False, None

def record_backup_metadata(backup_file, timestamp, duration, size_mb, status, error_message=None):
    """Record metadata about the backup for tracking purposes"""
    metadata_file = os.path.join(BACKUP_DIR, "backup_history.json")
    
    try:
        # Load existing metadata if it exists
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                backup_history = json.load(f)
        else:
            backup_history = []
        
        # Add new backup metadata
        backup_record = {
            "timestamp": timestamp,
            "filename": os.path.basename(backup_file),
            "database": DB_NAME,
            "duration_seconds": round(duration, 2),
            "size_mb": round(size_mb, 2),
            "status": status,
            "error_message": error_message
        }
        
        backup_history.append(backup_record)
        
        # Write updated metadata
        with open(metadata_file, 'w') as f:
            json.dump(backup_history, f, indent=2)
            
        logger.info(f"Recorded backup metadata to {metadata_file}")
    except Exception as e:
        logger.error(f"Error recording backup metadata: {e}")

def cleanup_old_backups():
    """Remove backup files older than KEEP_DAYS days"""
    logger.info(f"Cleaning up backups older than {KEEP_DAYS} days")
    
    now = time.time()
    count = 0
    
    for filename in os.listdir(BACKUP_DIR):
        if filename == "backup_history.json":
            continue
            
        filepath = os.path.join(BACKUP_DIR, filename)
        
        # Check if the file is a regular file (not a directory)
        if os.path.isfile(filepath):
            # Get the file's modification time
            file_time = os.path.getmtime(filepath)
            
            # If the file is older than KEEP_DAYS, delete it
            if (now - file_time) / (24 * 3600) > KEEP_DAYS:
                try:
                    os.remove(filepath)
                    count += 1
                    logger.info(f"Deleted old backup: {filename}")
                except Exception as e:
                    logger.error(f"Error deleting old backup {filepath}: {e}")
    
    logger.info(f"Cleanup completed: removed {count} old backup files")

if __name__ == "__main__":
    logger.info("=== Database Backup Script Started ===")
    
    try:
        success, backup_file = backup_database()
        
        if success:
            logger.info(f"Backup completed successfully: {backup_file}")
            sys.exit(0)
        else:
            logger.error("Backup failed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Unhandled exception during backup: {e}")
        sys.exit(1) 





