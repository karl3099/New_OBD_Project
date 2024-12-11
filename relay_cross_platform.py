#!/usr/bin/env python3
"""
Cross-Platform USB Relay Control
Supports both Windows and Mac implementations
"""

import sys
import time
import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('relay_control.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class RelayCommands:
    """Unified command structure for both platforms"""
    RELAY1_ON =  {'windows': b'\x00\x00\x01', 'darwin': [0x0, 0xFF, 0x01]}
    RELAY1_OFF = {'windows': b'\x00\x00\x00', 'darwin': [0x0, 0xFD, 0x01]}
    RELAY2_ON =  {'windows': b'\x00\x01\x01', 'darwin': [0x0, 0xFF, 0x02]}
    RELAY2_OFF = {'windows': b'\x00\x01\x00', 'darwin': [0x0, 0xFD, 0x02]}

class RelayImplementation(ABC):
    """Abstract base class for relay implementations"""
    
    @abstractmethod
    def connect(self):
        """Establish connection to relay device"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close connection to relay device"""
        pass
    
    @abstractmethod
    def send_command(self, command):
        """Send command to relay"""
        pass
    
    @abstractmethod
    def get_status(self):
        """Get relay status"""
        pass

class WindowsRelayImplementation(RelayImplementation):
    """Windows-specific implementation"""
    
    def __init__(self):
        self.device = None
        self.platform = 'windows'
        
    def connect(self):
        try:
            # Windows implementation using pyusb or similar
            import usb.core
            import usb.util
            
            # Find device
            self.device = usb.core.find(idVendor=0x16c0, idProduct=0x05df)
            if self.device is None:
                raise RuntimeError("Device not found")
                
            # Set configuration
            self.device.set_configuration()
            
            logger.info("Connected to relay device on Windows")
            return True
            
        except Exception as e:
            logger.error(f"Windows connection error: {e}")
            return False
    
    def disconnect(self):
        try:
            if self.device:
                usb.util.dispose_resources(self.device)
            logger.info("Disconnected from relay device")
            return True
        except Exception as e:
            logger.error(f"Windows disconnection error: {e}")
            return False
    
    def send_command(self, command):
        try:
            if not self.device:
                raise RuntimeError("Device not connected")
            
            # Get command bytes for Windows
            cmd_bytes = RelayCommands.__dict__[command]['windows']
            
            # Send command
            self.device.ctrl_transfer(0x21, 0x09, 0x0300, 0x0000, cmd_bytes)
            logger.info(f"Sent command: {command}")
            return True
            
        except Exception as e:
            logger.error(f"Windows command error: {e}")
            return False
    
    def get_status(self):
        try:
            if not self.device:
                raise RuntimeError("Device not connected")
            
            # Read status
            status = self.device.ctrl_transfer(0xA1, 0x01, 0x0300, 0x0000, 8)
            return {'relay1': bool(status[0] & 1), 'relay2': bool(status[0] & 2)}
            
        except Exception as e:
            logger.error(f"Windows status error: {e}")
            return None

class MacRelayImplementation(RelayImplementation):
    """Mac-specific implementation"""
    
    def __init__(self):
        self.device = None
        self.platform = 'darwin'
        
    def connect(self):
        try:
            import hid
            
            # Find and open device
            self.device = hid.device()
            self.device.open(0x16c0, 0x05df)
            
            logger.info(f"Connected to relay device on Mac")
            logger.info(f"Manufacturer: {self.device.get_manufacturer_string()}")
            logger.info(f"Product: {self.device.get_product_string()}")
            
            return True
            
        except Exception as e:
            logger.error(f"Mac connection error: {e}")
            return False
    
    def disconnect(self):
        try:
            if self.device:
                self.device.close()
            logger.info("Disconnected from relay device")
            return True
        except Exception as e:
            logger.error(f"Mac disconnection error: {e}")
            return False
    
    def send_command(self, command):
        try:
            if not self.device:
                raise RuntimeError("Device not connected")
            
            # Get command for Mac
            cmd = RelayCommands.__dict__[command]['darwin']
            
            # Pad command to 8 bytes
            full_command = cmd + [0x0] * (8 - len(cmd))
            
            # Send command
            self.device.write(full_command)
            logger.info(f"Sent command: {command}")
            
            # Read response
            response = self.device.read(8)
            logger.info(f"Response: {[hex(x) for x in response]}")
            
            return True
            
        except Exception as e:
            logger.error(f"Mac command error: {e}")
            return False
    
    def get_status(self):
        try:
            if not self.device:
                raise RuntimeError("Device not connected")
            
            # Send status query
            self.device.write([0x0] * 8)
            response = self.device.read(8)
            
            return {
                'relay1': bool(response[0] & 1),
                'relay2': bool(response[0] & 2)
            }
            
        except Exception as e:
            logger.error(f"Mac status error: {e}")
            return None

class RelayController:
    """Main relay control interface"""
    
    def __init__(self):
        self.platform = sys.platform
        self.implementation = self._get_implementation()
        self.connected = False
    
    def _get_implementation(self):
        """Get platform-specific implementation"""
        if self.platform == 'darwin':
            return MacRelayImplementation()
        elif self.platform == 'win32':
            return WindowsRelayImplementation()
        else:
            raise NotImplementedError(f"Platform {self.platform} not supported")
    
    def connect(self):
        """Connect to relay device"""
        self.connected = self.implementation.connect()
        return self.connected
    
    def disconnect(self):
        """Disconnect from relay device"""
        if self.connected:
            self.connected = not self.implementation.disconnect()
        return not self.connected
    
    def control_relay(self, relay_num, state):
        """Control relay state"""
        if not self.connected:
            if not self.connect():
                return False
        
        command = f"RELAY{relay_num}_{'ON' if state else 'OFF'}"
        return self.implementation.send_command(command)
    
    def get_status(self):
        """Get relay status"""
        if not self.connected:
            if not self.connect():
                return None
        
        return self.implementation.get_status()

def main():
    """Interactive test routine"""
    print("=== Cross-Platform USB Relay Control ===")
    
    controller = RelayController()
    
    if not controller.connect():
        print("Failed to connect to relay device")
        return
    
    while True:
        print("\nCommands:")
        print("1: Toggle Relay 1")
        print("2: Toggle Relay 2")
        print("3: Turn Relay 1 ON")
        print("4: Turn Relay 1 OFF")
        print("5: Turn Relay 2 ON")
        print("6: Turn Relay 2 OFF")
        print("s: Get Status")
        print("q: Quit")
        
        cmd = input("\nEnter command (1-6/s/q): ").lower()
        
        if cmd == 'q':
            break
        elif cmd == 's':
            status = controller.get_status()
            if status:
                print(f"Relay 1: {'ON' if status['relay1'] else 'OFF'}")
                print(f"Relay 2: {'ON' if status['relay2'] else 'OFF'}")
        elif cmd == '1':
            controller.control_relay(1, True)
            time.sleep(1)
            controller.control_relay(1, False)
        elif cmd == '2':
            controller.control_relay(2, True)
            time.sleep(1)
            controller.control_relay(2, False)
        elif cmd == '3':
            controller.control_relay(1, True)
        elif cmd == '4':
            controller.control_relay(1, False)
        elif cmd == '5':
            controller.control_relay(2, True)
        elif cmd == '6':
            controller.control_relay(2, False)
    
    controller.disconnect()

if __name__ == "__main__":
    main() 