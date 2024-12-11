#!/usr/bin/env python3
"""
NOYITO USB Relay Controller using HID protocol
Specifically for Mac M-series compatibility
"""

import hid
import time
import logging

class HIDRelay:
    """NOYITO USB HID Relay Controller"""
    
    def __init__(self, vendor_id=0x16c0, product_id=0x05df):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self):
        """Connect to the relay device"""
        try:
            # List all HID devices
            self.logger.info("Searching for HID devices...")
            for device in hid.enumerate():
                if device['vendor_id'] == self.vendor_id and device['product_id'] == self.product_id:
                    self.logger.info(f"Found relay device: {device.get('manufacturer_string', 'N/A')}")
                    
            # Open our relay
            self.device = hid.device()
            self.device.open(self.vendor_id, self.product_id)
            self.device.set_nonblocking(1)
            
            self.logger.info(f"Connected to: {self.device.get_manufacturer_string()} {self.device.get_product_string()}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            return False
    
    def send_command(self, data):
        """Send raw command to relay"""
        if not self.device:
            raise RuntimeError("Device not connected")
            
        try:
            # Ensure first byte is 0x00 (report ID)
            if not isinstance(data, (list, bytes)):
                data = [data]
            if isinstance(data, list):
                data = [0x00] + data
            else:
                data = b'\x00' + data
                
            # Send command
            self.logger.debug(f"Sending: {[hex(x) for x in data]}")
            self.device.write(data)
            
            # Wait for response
            time.sleep(0.05)
            
            # Try to read response
            try:
                response = self.device.read(64, timeout_ms=100)
                if response:
                    self.logger.debug(f"Response: {[hex(x) for x in response]}")
                return True
            except:
                return True  # Some commands don't return data
                
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return False
    
    def set_relay(self, relay_num, state):
        """Set relay state"""
        if relay_num not in [1, 2]:
            raise ValueError("Relay number must be 1 or 2")
            
        self.logger.info(f"Setting Relay {relay_num} {'ON' if state else 'OFF'}")
        
        # Command format for this relay:
        # Relay 1: 0xFE (ON) / 0x01 (OFF)
        # Relay 2: 0xFD (ON) / 0x02 (OFF)
        if relay_num == 1:
            cmd = 0xFE if state else 0x01
        else:
            cmd = 0xFD if state else 0x02
            
        return self.send_command([cmd])
    
    def set_all_relays(self, state):
        """Set all relays to same state"""
        self.logger.info(f"Setting ALL relays {'ON' if state else 'OFF'}")
        cmd = 0xFF if state else 0x00
        return self.send_command([cmd])
    
    def close(self):
        """Close the connection"""
        if self.device:
            try:
                self.set_all_relays(False)  # Turn everything off
                self.device.close()
            except:
                pass

def main():
    """Test the relay"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=== NOYITO USB Relay Test ===")
    
    relay = HIDRelay()
    
    try:
        if not relay.connect():
            logger.error("Failed to connect!")
            return
            
        while True:
            print("\nCommands:")
            print("1: Toggle Relay 1")
            print("2: Toggle Relay 2")
            print("a: Toggle All Relays")
            print("q: Quit")
            
            cmd = input("\nEnter command (1/2/a/q): ").lower()
            
            if cmd == 'q':
                break
            elif cmd == '1':
                relay.set_relay(1, True)
                time.sleep(1)
                relay.set_relay(1, False)
            elif cmd == '2':
                relay.set_relay(2, True)
                time.sleep(1)
                relay.set_relay(2, False)
            elif cmd == 'a':
                relay.set_all_relays(True)
                time.sleep(1)
                relay.set_all_relays(False)
                
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        relay.close()

if __name__ == "__main__":
    main() 