#!/usr/bin/env python3
"""
USB Device Detection Script
Specifically for finding CH340 or similar USB-Serial devices on Mac
"""

import sys
import subprocess
import serial.tools.list_ports

def check_system_profiler():
    """Check USB devices using system_profiler"""
    print("\n=== System Profiler USB Devices ===")
    try:
        result = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                              capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Error running system_profiler: {e}")

def check_serial_ports():
    """Check available serial ports"""
    print("\n=== Serial Ports ===")
    try:
        ports = list(serial.tools.list_ports.comports())
        if not ports:
            print("No serial ports found")
        for port in ports:
            print(f"\nPort: {port.device}")
            print(f"Description: {port.description}")
            print(f"Hardware ID: {port.hwid}")
            print(f"Manufacturer: {port.manufacturer}")
            print(f"Product: {port.product}")
            print(f"Interface: {port.interface}")
    except Exception as e:
        print(f"Error checking serial ports: {e}")

def check_dev_entries():
    """Check /dev entries"""
    print("\n=== /dev Entries ===")
    try:
        result = subprocess.run(['ls', '-l', '/dev/tty.*'], 
                              capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Error checking /dev entries: {e}")

def main():
    """Main detection routine"""
    print("=== USB Device Detection ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    check_system_profiler()
    check_serial_ports()
    check_dev_entries()

if __name__ == "__main__":
    main() 