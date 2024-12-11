#!/usr/bin/env python3
"""
Unified USB Relay Control
Compatible with Windows DLL protocol and Mac HID implementation
"""

import sys
import time
import logging
import signal
import atexit
from typing import Optional, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('relay_unified.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class RelayCommands:
    """Unified command structure"""
    # HID protocol commands (Mac)
    HID_COMMANDS = {
        'OPEN_ONE': lambda channel: [0x0, 0xFF, channel],
        'CLOSE_ONE': lambda channel: [0x0, 0xFD, channel],
        'OPEN_ALL': lambda _: [0x0, 0xFF, 0x0],
        'CLOSE_ALL': lambda _: [0x0, 0xFD, 0x0],
        'GET_STATUS': lambda _: [0x0, 0x00, 0x0]
    }

class RelayDevice:
    """Unified relay device implementation"""
    
    def __init__(self):
        self.platform = sys.platform
        self.device = None
        self.connected = False
        self._init_device()
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _init_device(self):
        """Initialize device based on platform"""
        try:
            if self.platform == 'darwin':
                import hid
                self.device = hid.device()
            else:
                raise NotImplementedError(f"Platform {self.platform} not supported")
                
        except Exception as e:
            logger.error(f"Device initialization error: {e}")
            self.device = None
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        logger.info(f"Received signal {signum}")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Ensure all relays are off and device is closed"""
        if self.connected:
            logger.info("Cleaning up...")
            try:
                self.close_all_channels()
                time.sleep(0.1)  # Small delay to ensure command is sent
                self.close()
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    def open(self) -> bool:
        """Open device connection"""
        try:
            if not self.device:
                return False
                
            if self.platform == 'darwin':
                self.device.open(0x16c0, 0x05df)
                logger.info(f"Connected to {self.device.get_manufacturer_string()}")
                self.connected = True
                return True
                
        except Exception as e:
            logger.error(f"Open error: {e}")
            return False
    
    def close(self):
        """Close device connection"""
        try:
            if self.device and self.connected:
                if self.platform == 'darwin':
                    self.device.close()
                self.connected = False
            self.device = None
            
        except Exception as e:
            logger.error(f"Close error: {e}")
    
    def _send_command(self, command_type: str, channel: int = 1) -> bool:
        """Send command to device"""
        try:
            if not self.device or not self.connected:
                return False
                
            if self.platform == 'darwin':
                cmd = RelayCommands.HID_COMMANDS[command_type](channel)
                # Pad to 8 bytes
                full_cmd = cmd + [0x0] * (8 - len(cmd))
                
                # Send command with retry
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        self.device.write(full_cmd)
                        response = self.device.read(8, timeout_ms=100)
                        logger.debug(f"Response: {[hex(x) for x in response]}")
                        return True
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise
                        time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Command error: {e}")
            self.connected = False
            return False
    
    def open_channel(self, channel: int) -> bool:
        """Open specific relay channel"""
        logger.info(f"Opening channel {channel}")
        return self._send_command('OPEN_ONE', channel)
    
    def close_channel(self, channel: int) -> bool:
        """Close specific relay channel"""
        logger.info(f"Closing channel {channel}")
        return self._send_command('CLOSE_ONE', channel)
    
    def open_all_channels(self) -> bool:
        """Open all relay channels"""
        logger.info("Opening all channels")
        return self._send_command('OPEN_ALL')
    
    def close_all_channels(self) -> bool:
        """Close all relay channels"""
        logger.info("Closing all channels")
        return self._send_command('CLOSE_ALL')
    
    def get_status(self) -> Optional[Dict[str, bool]]:
        """Get relay status"""
        try:
            if not self.device or not self.connected:
                return None
                
            if self.platform == 'darwin':
                self._send_command('GET_STATUS')
                response = self.device.read(8, timeout_ms=100)
                status = response[0]
                
                return {
                    f'relay{i+1}': bool(status & (1 << i))
                    for i in range(2)  # We only have 2 channels
                }
            
        except Exception as e:
            logger.error(f"Status error: {e}")
            self.connected = False
            return None

def main():
    """Interactive test routine"""
    print("=== Unified USB Relay Control ===")
    print(f"Platform: {sys.platform}")
    
    relay = RelayDevice()
    
    if not relay.open():
        print("Failed to open relay device")
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
            print("7: Open All Channels")
            print("8: Close All Channels")
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
                status = relay.get_status()
                if status:
                    for relay_num, state in status.items():
                        print(f"{relay_num}: {'ON' if state else 'OFF'}")
            elif cmd == '1':
                relay.open_channel(1)
                time.sleep(0.5)
                relay.close_channel(1)
            elif cmd == '2':
                relay.open_channel(2)
                time.sleep(0.5)
                relay.close_channel(2)
            elif cmd == '3':
                relay.open_channel(1)
            elif cmd == '4':
                relay.close_channel(1)
            elif cmd == '5':
                relay.open_channel(2)
            elif cmd == '6':
                relay.close_channel(2)
            elif cmd == '7':
                relay.open_all_channels()
            elif cmd == '8':
                relay.close_all_channels()
            
            # Small delay to ensure command completion
            time.sleep(0.1)
    
    finally:
        print("\nClosing relays and cleaning up...")
        relay.cleanup()

if __name__ == "__main__":
    main() 