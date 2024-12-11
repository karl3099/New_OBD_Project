#!/usr/bin/env python3
"""
Simple NOYITO USB Relay Controller
Uses direct HID commands
"""

import sys
import time
import hid
import argparse

# Device identifiers
VENDOR_ID = 0x16c0
PRODUCT_ID = 0x05df

# Command format:
# First byte is report ID (0x00)
# Second byte is the command:
# - 0xFF: All relays ON
# - 0x00: All relays OFF
# - 0xFE: Relay 1 ON
# - 0x01: Relay 1 OFF
# - 0xFD: Relay 2 ON
# - 0x02: Relay 2 OFF

COMMANDS = {
    'relay1_on':  [0x00, 0xFE],
    'relay1_off': [0x00, 0x01],
    'relay2_on':  [0x00, 0xFD],
    'relay2_off': [0x00, 0x02],
    'all_on':     [0x00, 0xFF],
    'all_off':    [0x00, 0x00]
}

def find_relay():
    """Find and open relay device"""
    try:
        device = hid.device()
        device.open(VENDOR_ID, PRODUCT_ID)
        device.set_nonblocking(1)
        return device
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_command(command, device=None):
    """Send command to relay"""
    if not device:
        device = find_relay()
        if not device:
            print("Error: Relay not found!")
            return False
    
    try:
        # Send command
        device.write(command)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if device:
            device.close()

def control_relay(relay_num, state, device=None):
    """Control specific relay"""
    cmd_key = f"relay{relay_num}_{'on' if state else 'off'}"
    if cmd_key in COMMANDS:
        return send_command(COMMANDS[cmd_key], device)
    return False

def interactive_mode():
    """Interactive relay control"""
    device = find_relay()
    if not device:
        print("Error: Relay not found!")
        return
    
    print(f"Connected to: {device.get_manufacturer_string()} {device.get_product_string()}")
    print("\nCommands:")
    print("1: Toggle Relay 1")
    print("2: Toggle Relay 2")
    print("3: Turn Relay 1 ON for 10 seconds")
    print("4: Turn Relay 2 ON for 10 seconds")
    print("a: Toggle ALL Relays")
    print("q: Quit")
    
    while True:
        cmd = input("\nEnter command (1/2/3/4/a/q): ").lower()
        
        if cmd == 'q':
            # Turn off all relays before quitting
            send_command(COMMANDS['all_off'], device)
            device.close()
            break
        elif cmd in ['1', '2']:
            relay_num = int(cmd)
            # Toggle ON
            if control_relay(relay_num, True, device):
                print(f"Relay {relay_num} ON")
            time.sleep(1)
            # Toggle OFF
            if control_relay(relay_num, False, device):
                print(f"Relay {relay_num} OFF")
        elif cmd in ['3', '4']:
            relay_num = int(cmd) - 2
            # Turn ON
            if control_relay(relay_num, True, device):
                print(f"Relay {relay_num} ON")
                time.sleep(10)
                # Turn OFF
                if control_relay(relay_num, False, device):
                    print(f"Relay {relay_num} OFF")
        elif cmd == 'a':
            # Toggle ALL ON
            if send_command(COMMANDS['all_on'], device):
                print("All relays ON")
            time.sleep(1)
            # Toggle ALL OFF
            if send_command(COMMANDS['all_off'], device):
                print("All relays OFF")

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Control NOYITO USB Relay')
    parser.add_argument('relay', type=int, choices=[1, 2], 
                       help='Relay number (1 or 2)')
    parser.add_argument('action', choices=['on', 'off'], 
                       help='Action to perform')
    parser.add_argument('--duration', type=float, 
                       help='Duration in seconds (optional)')
    
    if len(sys.argv) == 1:
        interactive_mode()
        return
    
    args = parser.parse_args()
    
    # Execute command
    device = find_relay()
    if device:
        if control_relay(args.relay, args.action == 'on', device):
            print(f"Relay {args.relay} {args.action.upper()}")
            
            # Handle duration if specified
            if args.duration:
                time.sleep(args.duration)
                control_relay(args.relay, False, device)
                print(f"Relay {args.relay} OFF")
        device.close()

if __name__ == "__main__":
    main() 