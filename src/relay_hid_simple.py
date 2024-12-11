#!/usr/bin/env python3
"""
Simple HID Relay Control
Specifically for NOYITO USB relay on Mac
"""

import hid
import time
import sys

def find_relay():
    """Find and open the relay device"""
    try:
        # Open the device
        h = hid.device()
        h.open(0x16c0, 0x05df)
        
        print(f"Found device:")
        print(f"  Manufacturer: {h.get_manufacturer_string()}")
        print(f"  Product: {h.get_product_string()}")
        return h
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_command(device, command):
    """Send command and read response"""
    try:
        # Commands must be 8 bytes
        padded_command = command + [0] * (8 - len(command))
        device.write(padded_command)
        
        # Read response
        response = device.read(8)
        print(f"Response: {[hex(x) for x in response]}")
        return True
    except Exception as e:
        print(f"Command error: {e}")
        return False

def main():
    print("=== Simple HID Relay Control ===")
    
    # Find device
    device = find_relay()
    if not device:
        print("Failed to open device")
        return
    
    try:
        while True:
            print("\nCommands:")
            print("1: Turn Relay 1 ON")
            print("2: Turn Relay 1 OFF")
            print("3: Turn Relay 2 ON")
            print("4: Turn Relay 2 OFF")
            print("5: Toggle Relay 1")
            print("6: Toggle Relay 2")
            print("q: Quit")
            
            cmd = input("\nEnter command (1-6/q): ").strip().lower()
            
            if cmd == 'q':
                # Turn off all relays before quitting
                send_command(device, [0x0, 0xFD, 0x01])
                send_command(device, [0x0, 0xFD, 0x02])
                break
                
            elif cmd == '1':
                send_command(device, [0x0, 0xFF, 0x01])
            elif cmd == '2':
                send_command(device, [0x0, 0xFD, 0x01])
            elif cmd == '3':
                send_command(device, [0x0, 0xFF, 0x02])
            elif cmd == '4':
                send_command(device, [0x0, 0xFD, 0x02])
            elif cmd == '5':
                send_command(device, [0x0, 0xFF, 0x01])
                time.sleep(0.5)
                send_command(device, [0x0, 0xFD, 0x01])
            elif cmd == '6':
                send_command(device, [0x0, 0xFF, 0x02])
                time.sleep(0.5)
                send_command(device, [0x0, 0xFD, 0x02])
            
            # Small delay between commands
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Ensure relays are off
        try:
            send_command(device, [0x0, 0xFD, 0x01])
            send_command(device, [0x0, 0xFD, 0x02])
            device.close()
        except:
            pass

if __name__ == "__main__":
    main() 