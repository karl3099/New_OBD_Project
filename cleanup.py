#!/usr/bin/env python3
"""
Project Directory Cleanup Utility

This script helps maintain a clean project directory by:
1. Removing redundant and temporary files
2. Creating backups before deletion
3. Cleaning cache files
4. Managing virtual environments
"""

import os
import shutil
import json
from datetime import datetime
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class DirectoryCleaner:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.backup_dir = None
        
    def backup_files(self, files_to_backup):
        """Create backups of files before removal"""
        if not files_to_backup:
            return None
            
        self.backup_dir = "backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        if not self.dry_run:
            os.makedirs(self.backup_dir)
            for file in files_to_backup:
                if os.path.exists(file):
                    shutil.copy2(file, os.path.join(self.backup_dir, file))
        logger.info(f"Backup created in: {self.backup_dir}")
        return self.backup_dir
    
    def remove_files(self, files):
        """Remove specified files"""
        for file in files:
            if os.path.exists(file):
                if not self.dry_run:
                    os.remove(file)
                logger.info(f"Removed: {file}")
    
    def clean_cache(self, patterns):
        """Clean cache files matching patterns"""
        for pattern in patterns:
            if not self.dry_run:
                os.system(f"find . -name '{pattern}' -type f -delete")
            logger.info(f"Cleaned cache files: {pattern}")
    
    def check_venv(self):
        """Check virtual environment status"""
        if os.path.exists("venv"):
            logger.info("\nVirtual environment management:")
            logger.info("1. Remove existing: rm -rf venv")
            logger.info("2. Create new: python -m venv venv")
            logger.info("3. Install deps: pip install -r requirements.txt")
    
    def list_remaining_files(self):
        """List remaining core files"""
        logger.info("\nRemaining core files:")
        os.system("ls -l *.py *.txt *.json")

def get_cleanup_config():
    """Get configuration for cleanup"""
    return {
        "files_to_remove": [
            "test_obd.py",          # Consolidated into setup_obd.py
            "setup_relay.py",       # Merged into setup_obd.py
            "relay_controller.py",  # Replaced by v2
            "probe_relay.py",      # Debug only
            "discover_commands.py", # Debug only
            "diagnose_relay.py",   # Debug only
            "relay_debug.py",      # Debug only
            "scan_ports.py",       # Debug only
            "simple_relay.py",     # Test only
            "simple_test.py",      # Test only
        ],
        "cache_patterns": [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".DS_Store"
        ]
    }

def main():
    """Main cleanup function"""
    parser = argparse.ArgumentParser(description="Clean up project directory")
    parser.add_argument("--dry-run", action="store_true", 
                      help="Show what would be done without making changes")
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("Performing dry run - no files will be modified")
    
    try:
        # Initialize cleaner
        cleaner = DirectoryCleaner(dry_run=args.dry_run)
        config = get_cleanup_config()
        
        # Show cleanup plan
        logger.info("\nCleanup Plan:")
        logger.info("1. Create backup of files to be removed")
        logger.info("2. Remove redundant files")
        logger.info("3. Clean cache files")
        logger.info("4. Check virtual environment")
        
        # Get user confirmation
        if not args.dry_run:
            response = input("\nProceed with cleanup? (y/N): ")
            if response.lower() != 'y':
                logger.info("Cleanup cancelled")
                return
        
        # Execute cleanup
        cleaner.backup_files(config["files_to_remove"])
        cleaner.remove_files(config["files_to_remove"])
        cleaner.clean_cache(config["cache_patterns"])
        cleaner.check_venv()
        cleaner.list_remaining_files()
        
        logger.info("\nCleanup completed successfully!")
        if cleaner.backup_dir:
            logger.info(f"Backup available in: {cleaner.backup_dir}")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 