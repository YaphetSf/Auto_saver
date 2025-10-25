#!/usr/bin/env python3
"""
Auto Save Monitor Core - Shared Monitoring Logic

Core monitoring functionality that can be used by both CLI and GUI implementations.
"""

import subprocess
import shutil
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional


class AutoSaveMonitor:
    """Main daemon class for monitoring game process and backing up save files."""
    
    def __init__(self, process_name="Silksong", save_file_name="user1.dat", save_file_path=None, 
                 backup_dir="./backups", max_backups=100, check_interval=60, backup_mode="file"):
        # Configuration
        self.process_name = process_name
        self.save_file_name = save_file_name
        self.backup_mode = backup_mode  # "file" or "folder"
        
        # Use provided path or default macOS path
        if save_file_path:
            self.save_file_path = Path(save_file_path)
        else:
            self.save_file_path = Path(f"/Users/dingzhong/Library/Application Support/unity.Team-Cherry.Silksong/1018808405/{self.save_file_name}")
        
        # Determine if we're backing up a file or folder
        if self.backup_mode == "folder" or self.save_file_path.is_dir():
            self.is_folder_backup = True
            if save_file_name and save_file_name != "user1.dat":
                # If we have a specific file name, construct the path
                self.source_name = self.save_file_path.name
            else:
                self.source_name = self.save_file_path.name
        else:
            self.is_folder_backup = False
            self.source_name = save_file_name
        
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.check_interval = check_interval
        self.running = False
        self.game_detected = False
    
    def is_game_running(self) -> bool:
        """Check if game process is running using pgrep."""
        try:
            result = subprocess.run(['pgrep', '-f', self.process_name], 
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
            return None
    
    def get_folder_hash(self, folder_path: Path) -> Optional[str]:
        """Calculate MD5 hash of a folder for comparison."""
        try:
            hash_md5 = hashlib.md5()
            # Walk through all files in the folder
            for file_path in sorted(folder_path.rglob("*")):
                if file_path.is_file():
                    # Add file path and content to hash
                    rel_path = file_path.relative_to(folder_path)
                    hash_md5.update(str(rel_path).encode())
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            return None
    
    def get_latest_backup_hash(self) -> Optional[str]:
        """Get hash of the most recent backup for comparison."""
        if not self.backup_dir.exists():
            return None
        
        # Get all backup folders and sort by name (timestamp) - newest first
        backup_folders = [f for f in self.backup_dir.iterdir() if f.is_dir()]
        if not backup_folders:
            return None
        
        backup_folders.sort(key=lambda x: x.name, reverse=True)
        latest_backup = backup_folders[0]
        
        if self.is_folder_backup:
            # For folder backups, hash the entire folder
            return self.get_folder_hash(latest_backup)
        else:
            # For file backups, hash the specific file
            latest_backup_file = latest_backup / self.save_file_name
            if latest_backup_file.exists():
                return self.get_file_hash(latest_backup_file)
        
        return None
    
    def has_save_file_changed(self) -> bool:
        """Check if the current save file/folder is different from the latest backup."""
        if not self.save_file_path.exists():
            return False
        
        # Get current hash (file or folder)
        if self.is_folder_backup:
            current_hash = self.get_folder_hash(self.save_file_path)
        else:
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
        """Create a timestamped backup of the save file/folder if it has changed."""
        if not self.save_file_path.exists():
            return False
        
        # Check if save file/folder has changed from latest backup
        if not self.has_save_file_changed():
            return False
        
        # Create timestamped backup folder
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_folder = self.backup_dir / timestamp
        
        try:
            # Create backup directory
            backup_folder.mkdir(parents=True, exist_ok=True)
            
            if self.is_folder_backup:
                # Copy entire folder
                dest_folder = backup_folder / self.save_file_path.name
                shutil.copytree(self.save_file_path, dest_folder, dirs_exist_ok=True)
            else:
                # Copy single file
                backup_file = backup_folder / self.save_file_name
                shutil.copy2(self.save_file_path, backup_file)
            
            return True
            
        except Exception as e:
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
            except Exception:
                pass
    
    def get_backup_count(self) -> int:
        """Get the current number of backups."""
        if not self.backup_dir.exists():
            return 0
        return len([f for f in self.backup_dir.iterdir() if f.is_dir()])
    
    def get_recent_backups(self, limit=10) -> list:
        """Get list of recent backups sorted by timestamp (newest first)."""
        if not self.backup_dir.exists():
            return []
        
        backup_folders = [f for f in self.backup_dir.iterdir() if f.is_dir()]
        backup_folders.sort(key=lambda x: x.name, reverse=True)
        
        backups = []
        for folder in backup_folders[:limit]:
            if self.is_folder_backup:
                # For folder backups, get the size of the entire folder
                total_size = sum(f.stat().st_size for f in folder.rglob('*') if f.is_file())
                backups.append({
                    'timestamp': folder.name,
                    'path': folder,
                    'size': total_size
                })
            else:
                # For file backups, get the size of the specific file
                backup_file = folder / self.save_file_name
                if backup_file.exists():
                    size = backup_file.stat().st_size
                    backups.append({
                        'timestamp': folder.name,
                        'path': folder,
                        'size': size
                    })
        
        return backups
    
    def stop(self):
        """Stop the monitoring loop."""
        self.running = False
    
    def start(self):
        """Start the monitoring loop (blocks until stop is called)."""
        self.running = True
        game_was_running = False
        
        while self.running:
            try:
                is_running = self.is_game_running()
                
                if is_running:
                    if not game_was_running:
                        game_was_running = True
                    
                    # Create backup while game is running
                    backup_result = self.create_backup()
                    if backup_result:
                        self.manage_fifo_backups()
                
                elif game_was_running:
                    game_was_running = False
                
                self.game_detected = game_was_running
                
                # Sleep for the check interval
                time.sleep(self.check_interval)
                
            except Exception as e:
                # Continue running despite errors
                time.sleep(self.check_interval)
        
        self.running = False
