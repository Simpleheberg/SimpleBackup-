#!/usr/bin/env python3
"""
SimpleBackup - Automatic Website & Database Backup Tool
Created by SimpleHeberg (https://simpleheberg.fr)

Simple, reliable backup solution for your websites and databases.
"""

import os
import sys
import json
import argparse
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
import tarfile
import logging

__version__ = "1.0.0"


class BackupConfig:
    """Configuration manager for backups"""
    
    def __init__(self, config_file="backup_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_file):
            return self.create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON in {self.config_file}")
            sys.exit(1)
    
    def create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "backup_dir": "./backups",
            "retention_days": 7,
            "compression": "gz",
            "websites": [
                {
                    "name": "example_site",
                    "path": "/var/www/html/example",
                    "enabled": False
                }
            ],
            "databases": [
                {
                    "name": "example_db",
                    "type": "mysql",
                    "host": "localhost",
                    "port": 3306,
                    "user": "backup_user",
                    "password": "your_password",
                    "database": "example_database",
                    "enabled": False
                }
            ],
            "notifications": {
                "enabled": False,
                "email": "admin@example.com"
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        
        print(f"✓ Default configuration created: {self.config_file}")
        print("  Please edit this file with your backup settings.")
        return default_config
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)


class BackupManager:
    """Main backup manager"""
    
    def __init__(self, config):
        self.config = config
        self.backup_dir = Path(config['backup_dir'])
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.backup_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"backup_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def get_timestamp(self):
        """Get formatted timestamp for backup naming"""
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def backup_website(self, website):
        """Backup website files"""
        if not website.get('enabled', False):
            logging.info(f"Skipping disabled website: {website['name']}")
            return None
        
        site_path = Path(website['path'])
        if not site_path.exists():
            logging.error(f"Website path does not exist: {site_path}")
            return None
        
        timestamp = self.get_timestamp()
        backup_name = f"{website['name']}_website_{timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_name
        
        logging.info(f"Backing up website: {website['name']}")
        
        try:
            with tarfile.open(backup_path, "w:gz") as tar:
                tar.add(site_path, arcname=website['name'])
            
            backup_size = backup_path.stat().st_size / (1024 * 1024)  # MB
            logging.info(f"✓ Website backup completed: {backup_name} ({backup_size:.2f} MB)")
            return backup_path
        
        except Exception as e:
            logging.error(f"✗ Website backup failed: {str(e)}")
            return None
    
    def backup_mysql_database(self, db_config):
        """Backup MySQL/MariaDB database"""
        timestamp = self.get_timestamp()
        backup_name = f"{db_config['name']}_mysql_{timestamp}.sql.gz"
        backup_path = self.backup_dir / backup_name
        
        logging.info(f"Backing up MySQL database: {db_config['database']}")
        
        try:
            # Build mysqldump command
            cmd = [
                'mysqldump',
                f"--host={db_config['host']}",
                f"--port={db_config['port']}",
                f"--user={db_config['user']}",
                f"--password={db_config['password']}",
                '--single-transaction',
                '--quick',
                '--lock-tables=false',
                db_config['database']
            ]
            
            # Execute mysqldump and compress
            with open(backup_path, 'wb') as f:
                dump_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                gzip_process = subprocess.Popen(['gzip'], stdin=dump_process.stdout, stdout=f, stderr=subprocess.PIPE)
                dump_process.stdout.close()
                
                gzip_output, gzip_error = gzip_process.communicate()
                dump_output, dump_error = dump_process.communicate()
                
                if dump_process.returncode != 0:
                    raise Exception(f"mysqldump error: {dump_error.decode()}")
                
                if gzip_process.returncode != 0:
                    raise Exception(f"gzip error: {gzip_error.decode()}")
            
            backup_size = backup_path.stat().st_size / (1024 * 1024)  # MB
            logging.info(f"✓ MySQL backup completed: {backup_name} ({backup_size:.2f} MB)")
            return backup_path
        
        except FileNotFoundError:
            logging.error("✗ mysqldump not found. Please install MySQL client tools.")
            return None
        except Exception as e:
            logging.error(f"✗ MySQL backup failed: {str(e)}")
            if backup_path.exists():
                backup_path.unlink()
            return None
    
    def backup_postgresql_database(self, db_config):
        """Backup PostgreSQL database"""
        timestamp = self.get_timestamp()
        backup_name = f"{db_config['name']}_postgresql_{timestamp}.sql.gz"
        backup_path = self.backup_dir / backup_name
        
        logging.info(f"Backing up PostgreSQL database: {db_config['database']}")
        
        try:
            # Set PostgreSQL password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['password']
            
            # Build pg_dump command
            cmd = [
                'pg_dump',
                f"--host={db_config['host']}",
                f"--port={db_config.get('port', 5432)}",
                f"--username={db_config['user']}",
                '--format=plain',
                '--no-owner',
                '--no-acl',
                db_config['database']
            ]
            
            # Execute pg_dump and compress
            with open(backup_path, 'wb') as f:
                dump_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
                gzip_process = subprocess.Popen(['gzip'], stdin=dump_process.stdout, stdout=f, stderr=subprocess.PIPE)
                dump_process.stdout.close()
                
                gzip_output, gzip_error = gzip_process.communicate()
                dump_output, dump_error = dump_process.communicate()
                
                if dump_process.returncode != 0:
                    raise Exception(f"pg_dump error: {dump_error.decode()}")
                
                if gzip_process.returncode != 0:
                    raise Exception(f"gzip error: {gzip_error.decode()}")
            
            backup_size = backup_path.stat().st_size / (1024 * 1024)  # MB
            logging.info(f"✓ PostgreSQL backup completed: {backup_name} ({backup_size:.2f} MB)")
            return backup_path
        
        except FileNotFoundError:
            logging.error("✗ pg_dump not found. Please install PostgreSQL client tools.")
            return None
        except Exception as e:
            logging.error(f"✗ PostgreSQL backup failed: {str(e)}")
            if backup_path.exists():
                backup_path.unlink()
            return None
    
    def backup_database(self, db_config):
        """Backup database based on type"""
        if not db_config.get('enabled', False):
            logging.info(f"Skipping disabled database: {db_config['name']}")
            return None
        
        db_type = db_config.get('type', 'mysql').lower()
        
        if db_type == 'mysql' or db_type == 'mariadb':
            return self.backup_mysql_database(db_config)
        elif db_type == 'postgresql' or db_type == 'postgres':
            return self.backup_postgresql_database(db_config)
        else:
            logging.error(f"Unsupported database type: {db_type}")
            return None
    
    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        retention_days = self.config.get('retention_days', 7)
        current_time = datetime.now().timestamp()
        retention_seconds = retention_days * 24 * 3600
        
        logging.info(f"Cleaning up backups older than {retention_days} days...")
        
        removed_count = 0
        freed_space = 0
        
        for backup_file in self.backup_dir.glob('*'):
            if backup_file.is_file() and backup_file.suffix in ['.gz', '.sql', '.tar']:
                file_age = current_time - backup_file.stat().st_mtime
                
                if file_age > retention_seconds:
                    file_size = backup_file.stat().st_size
                    backup_file.unlink()
                    removed_count += 1
                    freed_space += file_size
                    logging.info(f"  Removed old backup: {backup_file.name}")
        
        if removed_count > 0:
            freed_mb = freed_space / (1024 * 1024)
            logging.info(f"✓ Cleaned up {removed_count} old backup(s), freed {freed_mb:.2f} MB")
        else:
            logging.info("  No old backups to remove")
    
    def run_backup(self):
        """Execute full backup process"""
        logging.info("=" * 60)
        logging.info("Starting backup process...")
        logging.info("=" * 60)
        
        success_count = 0
        fail_count = 0
        
        # Backup websites
        for website in self.config.get('websites', []):
            result = self.backup_website(website)
            if result:
                success_count += 1
            else:
                fail_count += 1
        
        # Backup databases
        for database in self.config.get('databases', []):
            result = self.backup_database(database)
            if result:
                success_count += 1
            else:
                fail_count += 1
        
        # Cleanup old backups
        self.cleanup_old_backups()
        
        logging.info("=" * 60)
        logging.info(f"Backup process completed: {success_count} successful, {fail_count} failed")
        logging.info("=" * 60)
        
        return success_count, fail_count


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='SimpleBackup - Automatic Website & Database Backup Tool',
        epilog='Created by SimpleHeberg - https://simpleheberg.fr'
    )
    
    parser.add_argument(
        '--config',
        default='backup_config.json',
        help='Path to configuration file (default: backup_config.json)'
    )
    
    parser.add_argument(
        '--init',
        action='store_true',
        help='Create default configuration file and exit'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'SimpleBackup v{__version__}'
    )
    
    args = parser.parse_args()
    
    # Initialize configuration
    config_manager = BackupConfig(args.config)
    
    if args.init:
        print("\n✓ Configuration initialized successfully!")
        print(f"  Edit {args.config} to configure your backups.")
        sys.exit(0)
    
    # Run backup
    backup_manager = BackupManager(config_manager.config)
    success, failed = backup_manager.run_backup()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
