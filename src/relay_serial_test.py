#!/usr/bin/env python3
"""
USB Relay Control using Serial Protocol
For NOYITO USB relay on Mac M-series
"""

import sys
import time
import serial
import signal
import logging
from serial.tools import list_ports

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('relay_serial.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class RelayController:
    """Serial-based relay controller"""
    
    def __init__(self):
        self.port = None
        self.serial = None
        self.connected = False
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        print("\nClosing relays and exiting...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Ensure relays are off and connection is closed"""
        if self.connected:
            try:
                self.close_all_relays()
                time.sleep(0.1)
                if self.serial:
                    self.serial.close()
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    def find_device(self):
        """Find the USB relay device"""
        try:
            # Known relay identifiers
            VENDOR_IDS = ['16c0', '1a86']  # Include both HID and CH340
            
            for port in list_ports.comports():
                logger.info(f"Checking port: {port.device}")
                logger.info(f"Description: {port.description}")
                logger.info(f"Hardware ID: {port.hwid}")
                
                # Check if this is our device
                if any(vid in port.hwid.lower() for vid in VENDOR_IDS):
                    logger.info(f"Found relay device at {port.device}")
                    return port.device
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding device: {e}")
            return None
    
    def connect(self):
        """Connect to the relay device"""
        try:
            if self.connected:
                return True
            
            # Find device
            port = self.find_device()
            if not port:
                logger.error("Relay device not found")
                return False
            
            # Open serial connection
            self.serial = serial.Serial(
                port=port,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            
            self.connected = True
            logger.info(f"Connected to {port}")
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.connected = False
            return False
    
    def _send_command(self, command, retries=3):
        """Send command with retry logic"""
        if not self.connected and not self.connect():
            return False
        
        for attempt in range(retries):
            try:
                self.serial.write(command)
                time.sleep(0.1)  # Allow time for command processing
                return True
            except Exception as e:
                logger.error(f"Command error (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(0.5)
                    continue
                self.connected = False
                return False
    
    def open_relay(self, relay_num):
        """Open specific relay"""
        logger.info(f"Opening relay {relay_num}")
        if relay_num == 1:
            return self._send_command(bytes([0xA0, 0x01, 0x01, 0xA2]))
        elif relay_num == 2:
            return self._send_command(bytes([0xA0, 0x02, 0x01, 0xA3]))
        return False
    
    def close_relay(self, relay_num):
        """Close specific relay"""
        logger.info(f"Closing relay {relay_num}")
        if relay_num == 1:
            return self._send_command(bytes([0xA0, 0x01, 0x00, 0xA1]))
        elif relay_num == 2:
            return self._send_command(bytes([0xA0, 0x02, 0x00, 0xA2]))
        return False
    
    def open_all_relays(self):
        """Open all relays"""
        logger.info("Opening all relays")
        return (self.open_relay(1) and 
                self.open_relay(2))
    
    def close_all_relays(self):
        """Close all relays"""
        logger.info("Closing all relays")
        return (self.close_relay(1) and 
                self.close_relay(2))
    
    def get_status(self):
        """Get relay status"""
        try:
            if not self.connected and not self.connect():
                return None
            
            # Send status query
            self.serial.write(bytes([0xFF]))
            time.sleep(0.1)
            
            if self.serial.in_waiting:
                response = self.serial.read(self.serial.in_waiting)
                return {
                    'relay1': bool(response[0] & 1),
                    'relay2': bool(response[0] & 2)
                }
            return None
            
        except Exception as e:
            logger.error(f"Status error: {e}")
            self.connected = False
            return None

def main():
    """Interactive test routine"""
    print("=== Serial USB Relay Control ===")
    
    controller = RelayController()
    
    if not controller.connect():
        print("Failed to connect to relay device")
        return
    
    try:
        while True:
            print("\nCommands:")
            print("1: Toggle Relay 1")
            print("2: Toggle Relay 2")
            print("3: Turn Relay 1 ON")
            print("4: Turn Relay 1 OFF")
            print("5: Turn Relay 2 ON")
            print("6: Turn Relay 2 OFF")
            print("7: Open All Relays")
            print("8: Close All Relays")
            print("s: Get Status")
            print("q: Quit")
            
            try:
                cmd = input("\nEnter command (1-8/s/q): ").lower().strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
                break
            
            if cmd == 'q':
                break
            elif cmd == 's':
                status = controller.get_status()
                if status:
                    for relay_num, state in status.items():
                        print(f"{relay_num}: {'ON' if state else 'OFF'}")
            elif cmd == '1':
                controller.open_relay(1)
                time.sleep(0.5)
                controller.close_relay(1)
            elif cmd == '2':
                controller.open_relay(2)
                time.sleep(0.5)
                controller.close_relay(2)
            elif cmd == '3':
                controller.open_relay(1)
            elif cmd == '4':
                controller.close_relay(1)
            elif cmd == '5':
                controller.open_relay(2)
            elif cmd == '6':
                controller.close_relay(2)
            elif cmd == '7':
                controller.open_all_relays()
            elif cmd == '8':
                controller.close_all_relays()
            
            # Small delay between commands
            time.sleep(0.1)
    
    finally:
        controller.cleanup()

if __name__ == "__main__":
    main() 