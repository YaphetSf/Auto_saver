#!/usr/bin/env python3
"""
Auto Saver - Game Save File Monitor and Backup Daemon

Monitors for Silksong game process and automatically backs up save files
every 60 seconds while the game is running. Maintains up to 100 timestamped
backups using FIFO (First In, First Out) deletion.
"""

import subprocess
import shutil
import time
import signal
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional


class AutoSaveMonitor:
    """Main daemon class for monitoring game process and backing up save files."""
    
    def __init__(self):
        # Configuration - Change this to switch save files
        self.save_file_name = "user1.dat"  # Change to "user1.dat" or "user2.dat" as needed
        
        self.save_file_path = Path(f"/Users/dingzhong/Library/Application Support/unity.Team-Cherry.Silksong/1018808405/{self.save_file_name}")
        self.backup_dir = Path("./backups")
        self.max_backups = 100
        self.check_interval = 60  # seconds
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.running = False
        # Force exit to avoid waiting for sleep
        sys.exit(0)
    
    def is_game_running(self) -> bool:
        """Check if Silksong game process is running using pgrep."""
        try:
            result = subprocess.run(['pgrep', '-f', 'Silksong'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0 and result.stdout.strip() != ""
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_file_hash(self, file_path: Path) -> Optional[str]:
        """Calculate MD5 hash of a file for comparison."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return None
    
    def get_latest_backup_hash(self) -> Optional[str]:
        """Get hash of the most recent backup file for comparison."""
        if not self.backup_dir.exists():
            return None
        
        # Get all backup folders and sort by name (timestamp) - newest first
        backup_folders = [f for f in self.backup_dir.iterdir() if f.is_dir()]
        if not backup_folders:
            return None
        
        backup_folders.sort(key=lambda x: x.name, reverse=True)
        latest_backup_file = backup_folders[0] / self.save_file_name
        
        if latest_backup_file.exists():
            return self.get_file_hash(latest_backup_file)
        
        return None
    
    def has_save_file_changed(self) -> bool:
        """Check if the current save file is different from the latest backup."""
        if not self.save_file_path.exists():
            return False
        
        # Get current save file hash
        current_hash = self.get_file_hash(self.save_file_path)
        if not current_hash:
            return False
        
        # Get hash of latest backup
        latest_backup_hash = self.get_latest_backup_hash()
        
        # If no previous backup exists, consider it changed
        if latest_backup_hash is None:
            return True
        
        # Check if current hash is different from latest backup
        return current_hash != latest_backup_hash
    
    def create_backup(self) -> bool:
        """Create a timestamped backup of the save file if it has changed."""
        if not self.save_file_path.exists():
            print(f"Warning: Save file not found at {self.save_file_path}")
            return False
        
        # Check if save file has changed from latest backup
        if not self.has_save_file_changed():
            print("Save file unchanged, skipping backup")
            return False
        
        # Create timestamped backup folder
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_folder = self.backup_dir / timestamp
        backup_file = backup_folder / self.save_file_name
        
        try:
            # Create backup directory
            backup_folder.mkdir(parents=True, exist_ok=True)
            
            # Copy save file to backup location
            shutil.copy2(self.save_file_path, backup_file)
            
            print(f"Backup created: {backup_folder}")
            return True
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def manage_fifo_backups(self):
        """Maintain maximum number of backups using FIFO deletion."""
        if not self.backup_dir.exists():
            return
        
        # Get all backup folders and sort by name (timestamp)
        backup_folders = [f for f in self.backup_dir.iterdir() if f.is_dir()]
        backup_folders.sort(key=lambda x: x.name)
        
        # Remove oldest backups if we exceed the limit
        while len(backup_folders) > self.max_backups:
            oldest_folder = backup_folders.pop(0)
            try:
                shutil.rmtree(oldest_folder)
                print(f"Removed oldest backup: {oldest_folder}")
            except Exception as e:
                print(f"Error removing backup {oldest_folder}: {e}")
    
    def run(self):
        """Main daemon loop."""
        print("Auto Save Monitor - Starting daemon...")
        print(f"Monitoring save file: {self.save_file_path}")
        print(f"Backup directory: {self.backup_dir.absolute()}")
        print(f"Max backups: {self.max_backups}")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        game_was_running = False
        
        while self.running:
            try:
                is_running = self.is_game_running()
                
                if is_running:
                    if not game_was_running:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Silksong detected! Starting backup mode...")
                        game_was_running = True
                    
                    # Create backup while game is running
                    backup_result = self.create_backup()
                    if backup_result:
                        self.manage_fifo_backups()
                    # Note: create_backup() returns False when file is unchanged (which is correct behavior)
                
                elif game_was_running:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Silksong stopped. Monitoring for restart...")
                    game_was_running = False
                
                # Sleep for the check interval
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("Keyboard interrupt received")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(self.check_interval)
        
        print("Auto Save Monitor - Shutdown complete")


def main():
    """Main function - entry point for the application."""
    monitor = AutoSaveMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
