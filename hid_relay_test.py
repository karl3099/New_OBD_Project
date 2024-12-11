#!/usr/bin/env python3
"""
USB Relay Control using HID protocol
For NOYITO USB relay on Mac M-series
"""

import hid
import time

# USB Relay device identifiers
VENDOR_ID = 0x16c0
PRODUCT_ID = 0x05df

def find_relay():
    """Find and open USB relay device"""
    print("Searching for USB relay...")
    
    try:
        device = hid.device()
        device.open(VENDOR_ID, PRODUCT_ID)
        
        print(f"\n✓ Found device:")
        print(f"Manufacturer: {device.get_manufacturer_string()}")
        print(f"Product: {device.get_product_string()}")
        print(f"Serial Number: {device.get_serial_number_string()}")
        
        return device
    except Exception as e:
        print(f"✗ Error finding device: {e}")
        return None

def control_relay(relay_num, state):
    """Control relay state"""
    try:
        device = find_relay()
        if not device:
            return False
        
        # Command format: [0x0, state, relay_num, 0x0, 0x0, 0x0, 0x0, 0x0]
        command = [0x0] * 8
        command[0] = 0x0
        command[1] = 0xFF if state else 0xFD
        command[2] = relay_num
        
        print(f"\nSending command: {[hex(x) for x in command]}")
        device.write(command)
        
        # Read response
        response = device.read(8)
        print(f"Response: {[hex(x) for x in response]}")
        
        device.close()
        print("✓ Command sent successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Interactive relay control"""
    print("=== USB Relay HID Control ===")
    
    while True:
        print("\nCommands:")
        print("1: Toggle Relay 1")
        print("2: Toggle Relay 2")
        print("3: Turn Relay 1 ON")
        print("4: Turn Relay 1 OFF")
        print("5: Turn Relay 2 ON")
        print("6: Turn Relay 2 OFF")
        print("q: Quit")
        
        cmd = input("\nEnter command (1-6/q): ").lower()
        
        if cmd == 'q':
            break
        elif cmd == '1':
            control_relay(1, True)
            time.sleep(1)
            control_relay(1, False)
        elif cmd == '2':
            control_relay(2, True)
            time.sleep(1)
            control_relay(2, False)
        elif cmd == '3':
            control_relay(1, True)
        elif cmd == '4':
            control_relay(1, False)
        elif cmd == '5':
            control_relay(2, True)
        elif cmd == '6':
            control_relay(2, False)

if __name__ == "__main__":
    main() 