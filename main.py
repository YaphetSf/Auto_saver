#!/usr/bin/env python3
"""
Auto Saver - Game Save File Monitor and Backup Daemon (CLI)

Monitors for Silksong game process and automatically backs up save files
every 60 seconds while the game is running. Maintains up to 100 timestamped
backups using FIFO (First In, First Out) deletion.
"""

import signal
import sys
import threading
from monitor_core import AutoSaveMonitor


class CLIMonitor:
    """CLI wrapper for AutoSaveMonitor with signal handling."""
    
    def __init__(self):
        self.monitor = AutoSaveMonitor()
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.monitor.stop()
        sys.exit(0)
    
    def run(self):
        """Main daemon loop."""
        print("Auto Save Monitor - Starting daemon...")
        print(f"Monitoring process: {self.monitor.process_name}")
        print(f"Monitoring save file: {self.monitor.save_file_path}")
        print(f"Backup directory: {self.monitor.backup_dir.absolute()}")
        print(f"Max backups: {self.monitor.max_backups}")
        print(f"Check interval: {self.monitor.check_interval}s")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        try:
            self.monitor.start()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received")
        finally:
            print("Auto Save Monitor - Shutdown complete")


def main():
    """Main function - entry point for the application."""
    cli_monitor = CLIMonitor()
    cli_monitor.run()


if __name__ == "__main__":
    main()
