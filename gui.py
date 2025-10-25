#!/usr/bin/env python3
"""
Auto Save Monitor - GUI Interface

Light-themed tkinter GUI for monitoring game save files and creating backups.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import time
from datetime import datetime
from pathlib import Path
from monitor_core import AutoSaveMonitor


class AutoSaveGUI:
    """Main GUI application for Auto Save Monitor."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Save Monitor")
        self.root.geometry("700x700")
        self.root.resizable(True, True)
        
        # Monitor instance
        self.monitor = None
        self.monitoring_active = False
        
        # Settings variables
        self.process_name = tk.StringVar(value="Silksong")
        self.original_path = tk.StringVar(value="/Users/dingzhong/Library/Application Support/unity.Team-Cherry.Silksong/1018808405/user1.dat")
        self.backup_path = tk.StringVar(value="./backups")
        self.check_interval = tk.StringVar(value="60")
        self.max_backups = tk.StringVar(value="100")
        
        # Status variables
        self.game_status = tk.StringVar(value="Not Running")
        self.last_backup = tk.StringVar(value="Never")
        self.backup_count = tk.StringVar(value="0 / 100")
        
        # Initialize monitor state
        self.monitor_thread = None
        
        self.setup_ui()
        
        # Start status update loop
        self.update_status()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Create notebook (tabbed interface)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status tab
        self.setup_status_tab(notebook)
        
        # Settings tab
        self.setup_settings_tab(notebook)
    
    def setup_status_tab(self, notebook):
        """Setup the Status tab."""
        status_frame = ttk.Frame(notebook, padding="10")
        notebook.add(status_frame, text="Status")
        
        # Title
        title_label = ttk.Label(status_frame, text="Auto Save Monitor", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Status section
        status_section = ttk.LabelFrame(status_frame, text="Game Status", padding="10")
        status_section.pack(fill=tk.X, pady=(0, 20))
        
        # Game status indicator
        status_label = ttk.Label(status_section, text="Status:", font=("Arial", 10))
        status_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.status_indicator = ttk.Label(status_section, textvariable=self.game_status,
                                         font=("Arial", 10, "bold"), foreground="red")
        self.status_indicator.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Last backup
        last_backup_label = ttk.Label(status_section, text="Last Backup:", font=("Arial", 10))
        last_backup_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(status_section, textvariable=self.last_backup, font=("Arial", 10)).grid(
            row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Backup count
        backup_count_label = ttk.Label(status_section, text="Backups:", font=("Arial", 10))
        backup_count_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(status_section, textvariable=self.backup_count, font=("Arial", 10)).grid(
            row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Control buttons
        controls_section = ttk.LabelFrame(status_frame, text="Controls", padding="10")
        controls_section.pack(fill=tk.X, pady=(0, 20))
        
        button_frame = ttk.Frame(controls_section)
        button_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(button_frame, text="Start Monitor", 
                                       command=self.start_monitoring, width=15)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Monitor", 
                                      command=self.stop_monitoring, width=15, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_log_button = ttk.Button(button_frame, text="Clear Log", 
                                           command=self.clear_log, width=12)
        self.clear_log_button.pack(side=tk.RIGHT, padx=5)
        
        # Log section
        log_section = ttk.LabelFrame(status_frame, text="Activity Log", padding="10")
        log_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_section, height=8, wrap=tk.WORD, 
                                                   state=tk.DISABLED, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Recent backups
        backups_section = ttk.LabelFrame(status_frame, text="Recent Backups", padding="10")
        backups_section.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for backups
        columns = ("Timestamp", "Size")
        self.backups_tree = ttk.Treeview(backups_section, columns=columns, show="tree headings", height=4)
        self.backups_tree.heading("#0", text="File")
        self.backups_tree.heading("Timestamp", text="Timestamp")
        self.backups_tree.heading("Size", text="Size")
        self.backups_tree.column("#0", width=50)
        self.backups_tree.column("Timestamp", width=180)
        self.backups_tree.column("Size", width=100)
        
        scrollbar = ttk.Scrollbar(backups_section, orient=tk.VERTICAL, command=self.backups_tree.yview)
        self.backups_tree.configure(yscrollcommand=scrollbar.set)
        
        self.backups_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_settings_tab(self, notebook):
        """Setup the Settings tab."""
        settings_frame = ttk.Frame(notebook, padding="10")
        notebook.add(settings_frame, text="Settings")
        
        # Process name
        process_frame = ttk.LabelFrame(settings_frame, text="Process Settings", padding="10")
        process_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(process_frame, text="Process Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(process_frame, textvariable=self.process_name, width=40).grid(
            row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Path settings
        path_frame = ttk.LabelFrame(settings_frame, text="Path Settings", padding="10")
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Original save path (file or folder)
        ttk.Label(path_frame, text="Original Save Path:").grid(row=0, column=0, sticky=tk.W, pady=5)
        path_entry_frame = ttk.Frame(path_frame)
        path_entry_frame.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        self.original_path_entry = ttk.Entry(path_entry_frame, textvariable=self.original_path, width=40)
        self.original_path_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        original_browse_button = ttk.Button(path_entry_frame, text="Browse...", 
                                           command=self.browse_original_path, width=10)
        original_browse_button.pack(side=tk.LEFT)
        
        # Backup save path (folder only)
        ttk.Label(path_frame, text="Backup Save Path:").grid(row=1, column=0, sticky=tk.W, pady=5)
        backup_entry_frame = ttk.Frame(path_frame)
        backup_entry_frame.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        self.backup_path_entry = ttk.Entry(backup_entry_frame, textvariable=self.backup_path, width=40)
        self.backup_path_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        backup_browse_button = ttk.Button(backup_entry_frame, text="Browse...", 
                                          command=self.browse_backup_path, width=10)
        backup_browse_button.pack(side=tk.LEFT)
        
        # Backup settings
        backup_frame = ttk.LabelFrame(settings_frame, text="Backup Settings", padding="10")
        backup_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(backup_frame, text="Check Interval (s):").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(backup_frame, textvariable=self.check_interval, width=20).grid(
            row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Label(backup_frame, text="Max Backups:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(backup_frame, textvariable=self.max_backups, width=20).grid(
            row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Apply button
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        apply_button = ttk.Button(button_frame, text="Apply Settings", command=self.apply_settings)
        apply_button.pack()
    
    def start_monitoring(self):
        """Start the monitoring loop."""
        if self.monitoring_active:
            messagebox.showinfo("Already Running", "Monitor is already running.")
            return
        
        # Apply settings before starting
        self.apply_settings()
        
        if self.monitor is None:
            messagebox.showerror("Error", "Monitor not initialized. Please check your settings.")
            return
        
        # Start monitoring in separate thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
    
    def log_message(self, message):
        """Add a message to the log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # Scroll to bottom
        self.log_text.config(state=tk.DISABLED)
    
    def clear_log(self):
        """Clear the log area."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log_message("Log cleared")
    
    def monitoring_loop(self):
        """Run the monitoring loop in background thread."""
        self.log_message("Monitoring started")
        
        game_was_running = False
        
        while self.monitoring_active and self.monitor is not None:
            try:
                is_running = self.monitor.is_game_running()
                
                # Only log when game state changes
                if is_running and not game_was_running:
                    # Game just started
                    self.log_message(f"✓ Game started: {self.monitor.process_name}")
                    game_was_running = True
                elif not is_running and game_was_running:
                    # Game just stopped
                    self.log_message(f"✗ Game stopped: {self.monitor.process_name}")
                    game_was_running = False
                
                if is_running:
                    # Check if save file exists
                    if not self.monitor.save_file_path.exists():
                        if game_was_running:  # Only log once if we just detected it
                            self.log_message(f"Warning: Save file not found at {self.monitor.save_file_path}")
                            game_was_running = False  # Prevent repeated warnings
                    else:
                        # Create backup while game is running
                        backup_result = self.monitor.create_backup()
                        if backup_result:
                            self.monitor.manage_fifo_backups()
                            self.log_message(f"✓ Backup created successfully")
                        else:
                            # Only log "No changes detected" to show it's working
                            if game_was_running:  # Only log once right after starting
                                self.log_message("No changes detected, skipping backup")
                                game_was_running = False  # Prevent repeated "no changes" messages
                
                # Sleep for the check interval
                time.sleep(self.monitor.check_interval)
            except Exception as e:
                self.log_message(f"Error: {str(e)}")
                time.sleep(self.monitor.check_interval)
        
        if game_was_running:
            self.log_message(f"✗ Game stopped: {self.monitor.process_name}")
        
        self.log_message("Monitoring stopped")
    
    def stop_monitoring(self):
        """Stop the monitoring loop."""
        self.monitoring_active = False
        if self.monitor is not None:
            self.monitor.stop()
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message("Stop monitoring requested")
    
    def browse_original_path(self):
        """Browse for original save path (file or folder)."""
        # First try to select a file
        path = filedialog.askopenfilename(
            title="Select Original Save File (or Cancel to select folder)",
            filetypes=[("All files", "*.*"), ("DAT files", "*.dat")]
        )
        if path:
            self.original_path.set(path)
        else:
            # If canceled, offer to select a folder instead
            path = filedialog.askdirectory(title="Select Original Save Folder")
            if path:
                self.original_path.set(path)
    
    def browse_backup_path(self):
        """Browse for backup save path (folder only)."""
        path = filedialog.askdirectory(title="Select Backup Folder")
        if path:
            self.backup_path.set(path)
    
    def apply_settings(self):
        """Apply settings and create monitor instance."""
        try:
            # Stop existing monitor if running
            was_running = self.monitoring_active
            if self.monitoring_active:
                self.stop_monitoring()
            
            # Get paths
            original_path = Path(self.original_path.get())
            backup_path = Path(self.backup_path.get())
            
            # Determine save file name from original path
            if original_path.is_file():
                save_file_name = original_path.name
                save_file_path = str(original_path)
                backup_mode = "file"
            elif original_path.is_dir():
                # If it's a directory, we'll back up the whole folder
                save_file_name = original_path.name
                save_file_path = str(original_path)
                backup_mode = "folder"
            else:
                # Treat as file path string
                save_file_name = Path(self.original_path.get()).name
                save_file_path = self.original_path.get()
                backup_mode = "file"
            
            # Create new monitor with settings
            self.monitor = AutoSaveMonitor(
                process_name=self.process_name.get(),
                save_file_name=save_file_name,
                save_file_path=save_file_path,
                backup_dir=str(backup_path),
                max_backups=int(self.max_backups.get()),
                check_interval=int(self.check_interval.get()),
                backup_mode=backup_mode
            )
            
            self.log_message(f"Settings applied - Process: {self.process_name.get()}")
            self.log_message(f"Original path: {save_file_path}")
            self.log_message(f"Backup path: {backup_path}")
            
            # If it was running, restart it
            if was_running:
                self.start_monitoring()
            else:
                messagebox.showinfo("Settings Applied", "Settings have been applied successfully.")
        except ValueError as e:
            self.log_message(f"Error applying settings: {str(e)}")
            messagebox.showerror("Invalid Settings", f"Please check your settings: {e}")
        except Exception as e:
            self.log_message(f"Error applying settings: {str(e)}")
            messagebox.showerror("Error", f"Failed to apply settings: {e}")
    
    def update_backups_list(self):
        """Update the recent backups list."""
        if self.monitor is None:
            return
        
        # Clear existing items
        for item in self.backups_tree.get_children():
            self.backups_tree.delete(item)
        
        # Get recent backups
        recent_backups = self.monitor.get_recent_backups(limit=10)
        
        for backup in recent_backups:
            # Format timestamp
            timestamp = backup['timestamp'].replace('_', ' ')
            timestamp = timestamp.replace('-', ':')
            
            # Format size
            size = backup['size']
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            
            # Insert into tree
            self.backups_tree.insert("", tk.END, text=backup['timestamp'], 
                                    values=(timestamp, size_str))
            
            # Update last backup
            if len(recent_backups) > 0:
                self.last_backup.set(timestamp)
    
    def update_status(self):
        """Update the status display."""
        if self.monitor is not None:
            # Update game status
            is_running = self.monitor.is_game_running()
            if is_running:
                self.game_status.set("Running")
                self.status_indicator.config(foreground="green")
            else:
                self.game_status.set("Not Running")
                self.status_indicator.config(foreground="red")
            
            # Update backup count
            count = self.monitor.get_backup_count()
            max_bk = self.max_backups.get()
            self.backup_count.set(f"{count} / {max_bk}")
            
            # Update recent backups
            self.update_backups_list()
        
        # Schedule next update
        self.root.after(1000, self.update_status)


def main():
    """Main function to launch the GUI."""
    root = tk.Tk()
    app = AutoSaveGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
