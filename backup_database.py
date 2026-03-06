#!/usr/bin/env python3
"""
Database backup script for JobTracker AI
Backs up PostgreSQL database to local file with timestamp
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

# Database connection from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/jobtracker")

# Parse DATABASE_URL
# Format: postgresql://user:password@host:port/database
try:
    from urllib.parse import urlparse
    parsed = urlparse(DATABASE_URL)
    DB_USER = parsed.username
    DB_PASSWORD = parsed.password
    DB_HOST = parsed.hostname
    DB_PORT = parsed.port or 5432
    DB_NAME = parsed.path.lstrip('/')
except Exception as e:
    logger.error(f"Failed to parse DATABASE_URL: {e}")
    exit(1)


def create_backup():
    """Create database backup using pg_dump"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"jobtracker_backup_{timestamp}.sql"
    
    logger.info("=" * 60)
    logger.info("DATABASE BACKUP STARTED")
    logger.info("=" * 60)
    logger.info(f"Database: {DB_NAME}")
    logger.info(f"Host: {DB_HOST}:{DB_PORT}")
    logger.info(f"Backup file: {backup_file}")
    logger.info("-" * 60)
    
    try:
        # Set password environment variable for pg_dump
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_PASSWORD
        
        # Run pg_dump
        command = [
            'pg_dump',
            '-h', DB_HOST,
            '-p', str(DB_PORT),
            '-U', DB_USER,
            '-d', DB_NAME,
            '-F', 'p',  # Plain text format
            '-f', str(backup_file)
        ]
        
        logger.info("Running pg_dump...")
        result = subprocess.run(
            command,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            file_size = backup_file.stat().st_size
            logger.info(f"✅ Backup successful!")
            logger.info(f"File size: {file_size / (1024*1024):.2f} MB")
            logger.info(f"Location: {backup_file.absolute()}")
            
            # Cleanup old backups (keep last 7)
            cleanup_old_backups()
            
        else:
            logger.error(f"❌ Backup failed!")
            logger.error(f"Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        logger.error("❌ pg_dump not found! Please install PostgreSQL client tools.")
        logger.error("Install: sudo apt-get install postgresql-client (Linux)")
        logger.error("        brew install postgresql (Mac)")
        return False
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        return False
    
    logger.info("=" * 60)
    return True


def cleanup_old_backups(keep_last=7):
    """Keep only the last N backups"""
    backups = sorted(BACKUP_DIR.glob("jobtracker_backup_*.sql"))
    
    if len(backups) > keep_last:
        old_backups = backups[:-keep_last]
        logger.info(f"Cleaning up {len(old_backups)} old backup(s)...")
        
        for backup in old_backups:
            try:
                backup.unlink()
                logger.info(f"  Deleted: {backup.name}")
            except Exception as e:
                logger.warning(f"  Failed to delete {backup.name}: {e}")


def restore_backup(backup_file: str):
    """Restore database from backup file"""
    
    backup_path = Path(backup_file)
    if not backup_path.exists():
        logger.error(f"Backup file not found: {backup_file}")
        return False
    
    logger.info("=" * 60)
    logger.info("DATABASE RESTORE STARTED")
    logger.info("=" * 60)
    logger.info(f"Backup file: {backup_path}")
    logger.info(f"Target database: {DB_NAME}")
    logger.warning("⚠️  This will overwrite the current database!")
    logger.info("-" * 60)
    
    # Confirm restore
    confirm = input("Type 'YES' to confirm restore: ")
    if confirm != 'YES':
        logger.info("Restore cancelled.")
        return False
    
    try:
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_PASSWORD
        
        command = [
            'psql',
            '-h', DB_HOST,
            '-p', str(DB_PORT),
            '-U', DB_USER,
            '-d', DB_NAME,
            '-f', str(backup_path)
        ]
        
        logger.info("Running psql restore...")
        result = subprocess.run(
            command,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Restore successful!")
        else:
            logger.error(f"❌ Restore failed!")
            logger.error(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Restore failed: {e}")
        return False
    
    logger.info("=" * 60)
    return True


def list_backups():
    """List all available backups"""
    backups = sorted(BACKUP_DIR.glob("jobtracker_backup_*.sql"), reverse=True)
    
    if not backups:
        logger.info("No backups found.")
        return
    
    logger.info("=" * 60)
    logger.info("AVAILABLE BACKUPS")
    logger.info("=" * 60)
    
    for i, backup in enumerate(backups, 1):
        size = backup.stat().st_size / (1024*1024)
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        logger.info(f"{i}. {backup.name}")
        logger.info(f"   Size: {size:.2f} MB | Created: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "backup":
            create_backup()
        elif command == "restore":
            if len(sys.argv) < 3:
                logger.error("Usage: python backup_database.py restore <backup_file>")
                sys.exit(1)
            restore_backup(sys.argv[2])
        elif command == "list":
            list_backups()
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Usage: python backup_database.py [backup|restore|list]")
            sys.exit(1)
    else:
        # Default: create backup
        create_backup()
