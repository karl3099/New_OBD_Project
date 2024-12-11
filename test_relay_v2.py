#!/usr/bin/env python3
"""
Relay Test Utility for M-series Mac

A structured test script for USB relay using serial communication:
1. CH340 Serial Communication
2. 9600 Baud Rate
3. Command Protocol Implementation
4. Status Verification
"""

import sys
import time
import logging
import platform
import subprocess
from typing import Optional, List, Dict
import serial
import serial.tools.list_ports

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_system_requirements():
    """Verify system requirements for M-series Mac"""
    logger.info("Checking system requirements...")
    
    # Check OS
    if platform.system() != "Darwin":
        logger.error("This script requires macOS")
        return False
        
    # Check for CH340 driver
    try:
        ports = list(serial.tools.list_ports.grep("CH340"))
        if not ports:
            logger.warning("No CH340 devices found - make sure driver is installed")
    except:
        logger.warning("Could not check for CH340 devices")
    
    return True

def find_relay_port():
    """Find the serial port for the relay"""
    logger.info("Looking for relay serial port...")
    
    # Try to find CH340 device
    try:
        ports = list(serial.tools.list_ports.grep("CH340"))
        if ports:
            logger.info(f"Found CH340 device at {ports[0].device}")
            return ports[0].device
    except:
        pass
        
    # List all potential ports
    try:
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            logger.debug(f"Found port: {port.device} - {port.description}")
            if "USB" in port.description:
                logger.info(f"Found USB serial device at {port.device}")
                return port.device
    except:
        pass
        
    return None

class RelayTester:
    def __init__(self):
        self.serial = None
        self.connected = False
        self.relay_states = [False, False]  # State of relay 1 and 2
        
        # Command constants
        self.START_FLAG = 0xA0  # Start flag
        self.STATE_ON = 0x01
        self.STATE_OFF = 0x00
        self.QUERY_CMD = 0xFF
        
        # Verify system requirements
        if not check_system_requirements():
            raise RuntimeError("System requirements not met")
            
        # Find relay port
        self.port = find_relay_port()
        if not self.port:
            raise RuntimeError("Could not find relay serial port")
    
    def connect(self) -> bool:
        """Establish connection to relay"""
        logger.info("\n=== Connecting to Relay ===")
        
        try:
            logger.debug(f"Opening serial port {self.port}...")
            self.serial = serial.Serial(
                port=self.port,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            
            # Test connection by querying status
            if self.get_relay_states():
                self.connected = True
                logger.info("✓ Successfully connected to relay")
                return True
            else:
                logger.error("Could not get relay status")
                return False
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return False
    
    def calculate_checksum(self, data: List[int]) -> int:
        """Calculate checksum for command"""
        return sum(data) & 0xFF
    
    def build_command(self, relay_num: int, state: bool) -> bytes:
        """Build command with proper format and checksum"""
        cmd = [
            self.START_FLAG,           # Start flag
            relay_num,                 # Switch address
            0x01 if state else 0x00    # Operation
        ]
        cmd.append(self.calculate_checksum(cmd))  # Add checksum
        return bytes(cmd)
    
    def get_relay_states(self) -> List[bool]:
        """Query current relay states"""
        if not self.connected:
            logger.error("Not connected to relay")
            return self.relay_states
            
        try:
            # Send query command
            self.serial.write(bytes([self.QUERY_CMD]))
            time.sleep(0.1)  # Wait for response
            
            # Read response
            if self.serial.in_waiting:
                response = self.serial.read_until(b'\n').decode('ascii')
                logger.debug(f"Status response: {response}")
                
                # Parse response
                self.relay_states[0] = "CH1:ON" in response
                self.relay_states[1] = "CH2:ON" in response
                
                logger.debug(f"Parsed states: {[int(s) for s in self.relay_states]}")
            else:
                logger.warning("No response to status query")
                
        except Exception as e:
            logger.error(f"Error reading relay states: {e}")
            
        return self.relay_states
    
    def send_command(self, relay_num: int, state: bool, verify: bool = True) -> bool:
        """Send command to relay with verification"""
        if not self.connected:
            logger.error("Not connected to relay")
            return False
            
        try:
            # Build and send command
            cmd = self.build_command(relay_num, state)
            logger.info(f"Sending command: {[hex(x) for x in cmd]}")
            
            self.serial.write(cmd)
            time.sleep(0.1)  # Wait for relay to respond
            
            if verify:
                # Read back states
                states = self.get_relay_states()
                logger.info(f"Current relay states: Relay1={'ON' if states[0] else 'OFF'}, Relay2={'ON' if states[1] else 'OFF'}")
                
                # Verify correct state
                if relay_num == 1:
                    return states[0] == state
                elif relay_num == 2:
                    return states[1] == state
                else:
                    return all(s == state for s in states)
            
            return True
            
        except Exception as e:
            logger.error(f"Command failed: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return False
    
    def test_relay(self, relay_num: int, state: bool) -> bool:
        """Test specific relay with state verification"""
        logger.info(f"\nTesting Relay {relay_num} -> {'ON' if state else 'OFF'}")
        
        # Get current states first
        current_states = self.get_relay_states()
        logger.info(f"Current states before change: Relay1={'ON' if current_states[0] else 'OFF'}, Relay2={'ON' if current_states[1] else 'OFF'}")
        
        if relay_num in [1, 2]:
            success = self.send_command(relay_num, state, verify=True)
        else:
            # Control both relays
            success = True
            for relay in [1, 2]:
                if not self.send_command(relay, state, verify=True):
                    success = False
                    break
                time.sleep(0.1)  # Small delay between relay commands
        
        if success:
            logger.info(f"✓ Relay {relay_num} {'ON' if state else 'OFF'}")
        else:
            logger.error(f"✗ Relay {relay_num} state verification failed!")
            states = self.get_relay_states()
            logger.info(f"  Expected: {'ON' if state else 'OFF'}")
            logger.info(f"  Actual: Relay1={'ON' if states[0] else 'OFF'}, Relay2={'ON' if states[1] else 'OFF'}")
            
        return success
    
    def cleanup(self):
        """Safe cleanup of relay connection"""
        if self.connected:
            try:
                logger.info("\nCleaning up...")
                # Turn all relays off
                for relay in [1, 2]:
                    self.send_command(relay, False)
                    time.sleep(0.1)
                self.serial.close()
                logger.info("✓ Relay connection closed")
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                import traceback
                logger.debug(f"Traceback: {traceback.format_exc()}")

def interactive_test():
    """Interactive relay testing with error handling"""
    try:
        tester = RelayTester()
    except Exception as e:
        logger.error(f"Could not initialize tester: {e}")
        return
    
    try:
        # Connection
        if not tester.connect():
            logger.error("Failed to connect to relay!")
            return
        
        # Interactive Testing
        logger.info("\n=== Interactive Relay Test ===")
        logger.info("Commands:")
        logger.info("1: Toggle Relay 1")
        logger.info("2: Toggle Relay 2")
        logger.info("a: Toggle All Relays")
        logger.info("s: Show Status")
        logger.info("q: Quit")
        
        relay1_state = False
        relay2_state = False
        
        while True:
            try:
                cmd = input("\nEnter command (1/2/a/s/q): ").lower()
                
                if cmd == 'q':
                    break
                elif cmd == 's':
                    states = tester.get_relay_states()
                    logger.info(f"Current states: Relay1={'ON' if states[0] else 'OFF'}, Relay2={'ON' if states[1] else 'OFF'}")
                elif cmd == '1':
                    relay1_state = not relay1_state
                    tester.test_relay(1, relay1_state)
                elif cmd == '2':
                    relay2_state = not relay2_state
                    tester.test_relay(2, relay2_state)
                elif cmd == 'a':
                    relay1_state = relay2_state = not relay1_state
                    tester.test_relay(0, relay1_state)  # 0 means all relays
                else:
                    logger.warning("Invalid command")
                    
            except Exception as e:
                logger.error(f"Command error: {e}")
                import traceback
                logger.debug(f"Traceback: {traceback.format_exc()}")
                
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test error: {e}")
        import traceback
        logger.debug(f"Traceback: {traceback.format_exc()}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    logger.info("=== USB Relay Test Utility ===")
    interactive_test() 