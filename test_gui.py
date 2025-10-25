#!/usr/bin/env python3
"""Simple test to check if tkinter works"""

try:
    import tkinter as tk
    print("✓ tkinter imported successfully")
    
    root = tk.Tk()
    root.title("Test")
    root.geometry("300x200")
    
    label = tk.Label(root, text="tkinter is working!")
    label.pack(pady=50)
    
    print("✓ GUI window created")
    print("Close the window to exit")
    
    root.mainloop()
    print("✓ Test completed successfully")
except ImportError as e:
    print(f"✗ tkinter not available: {e}")
    print("\nOn macOS, tkinter should come with Python.")
    print("Try installing python-tk: brew install python-tk")
except Exception as e:
    print(f"✗ Error: {e}")
