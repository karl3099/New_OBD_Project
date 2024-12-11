#!/usr/bin/env python3
"""
NOYITO USB Relay Controller for Mac
Using CH340 Serial Protocol
"""

import time
import serial
import serial.tools.list_ports

# CH340 USB-Serial converter identifiers
VENDOR_ID = '1a86'   # QinHeng Electronics
PRODUCT_ID = '7523'  # CH340 converter

# Command sequences
COMMANDS = {
    'relay1_on':  [0xA0, 0x01, 0x01, 0xA2],
    'relay1_off': [0xA0, 0x01, 0x00, 0xA1],
    'relay2_on':  [0xA0, 0x02, 0x01, 0xA3],
    'relay2_off': [0xA0, 0x02, 0x00, 0xA2]
}

def find_ch340_device():
    """Find CH340 device port"""
    print("Searching for CH340 device...")
    
    ports = list(serial.tools.list_ports.comports())
    device_port = None
    
    for p in ports:
        # Print all port information for debugging
        print(f"\nPort: {p.device}")
        print(f"Description: {p.description}")
        print(f"Hardware ID: {p.hwid}")
        
        # Check if this is our CH340 device
        if f"{VENDOR_ID}:{PRODUCT_ID}" in p.hwid.lower():
            print(f"\n✓ Found CH340 device at {p.device}")
            device_port = p.device
            break
            
    return device_port

def control_relay(relay_num=1, state=True, duration=None):
    """Control relay state"""
    # Find device
    port = find_ch340_device()
    if not port:
        print("✗ CH340 device not found!")
        return False
    
    try:
        # Open serial connection
        print(f"\nOpening {port}...")
        ser = serial.Serial(port, 9600, timeout=1)
        
        # Determine command
        cmd_key = f"relay{relay_num}_{'on' if state else 'off'}"
        command = COMMANDS[cmd_key]
        
        # Send command
        print(f"Sending command: {[hex(x) for x in command]}")
        ser.write(command)
        
        # Wait if duration specified
        if duration:
            print(f"Waiting {duration} seconds...")
            time.sleep(duration)
            
            # Send opposite command
            cmd_key = f"relay{relay_num}_{'off' if state else 'on'}"
            command = COMMANDS[cmd_key]
            print(f"Sending command: {[hex(x) for x in command]}")
            ser.write(command)
        
        # Close connection
        ser.close()
        print("✓ Command(s) sent successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Interactive relay control"""
    print("=== NOYITO USB Relay Control ===")
    
    while True:
        print("\nCommands:")
        print("1: Toggle Relay 1")
        print("2: Toggle Relay 2")
        print("3: Turn Relay 1 ON for 10 seconds")
        print("4: Turn Relay 2 ON for 10 seconds")
        print("q: Quit")
        
        cmd = input("\nEnter command (1/2/3/4/q): ").lower()
        
        if cmd == 'q':
            break
        elif cmd == '1':
            control_relay(relay_num=1, state=True)
            time.sleep(1)
            control_relay(relay_num=1, state=False)
        elif cmd == '2':
            control_relay(relay_num=2, state=True)
            time.sleep(1)
            control_relay(relay_num=2, state=False)
        elif cmd == '3':
            control_relay(relay_num=1, state=True, duration=10)
        elif cmd == '4':
            control_relay(relay_num=2, state=True, duration=10)

if __name__ == "__main__":
    main() 