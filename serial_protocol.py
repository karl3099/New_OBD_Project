#!/usr/bin/env python3
"""
NOYITO USB Relay Serial Protocol Handler

Implements the serial protocol for NOYITO 2-channel USB relay:
- CH340 USB-Serial chip
- 9600 baud rate
- Command format: [START][ADDR][CMD][CHECKSUM]
"""

import time
from typing import List, Optional, Tuple
import serial
import serial.tools.list_ports

class RelayProtocol:
    """NOYITO USB Relay protocol implementation"""
    
    # Protocol constants
    START_FLAG = 0xA0
    STATE_ON = 0x01
    STATE_OFF = 0x00
    QUERY_CMD = 0xFF
    
    # Command format:
    # Byte 1: Start flag (0xA0)
    # Byte 2: Switch address (0x01 or 0x02)
    # Byte 3: Operation (0x00 = off, 0x01 = on)
    # Byte 4: Checksum (sum of bytes 1-3 & 0xFF)
    
    @staticmethod
    def find_relay_port() -> Optional[str]:
        """Find the relay's serial port"""
        # Try to find CH340 device first
        ports = list(serial.tools.list_ports.grep("CH340"))
        if ports:
            return ports[0].device
            
        # Fall back to any USB serial device
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if "USB" in port.description:
                return port.device
                
        return None
    
    @staticmethod
    def calculate_checksum(data: List[int]) -> int:
        """Calculate command checksum"""
        return sum(data) & 0xFF
    
    @staticmethod
    def build_command(relay_num: int, state: bool) -> bytes:
        """Build relay command with checksum"""
        if relay_num not in [1, 2]:
            raise ValueError("Relay number must be 1 or 2")
            
        cmd = [
            RelayProtocol.START_FLAG,  # Start flag
            relay_num,                 # Switch address
            0x01 if state else 0x00    # Operation
        ]
        
        # Add checksum
        cmd.append(RelayProtocol.calculate_checksum(cmd))
        return bytes(cmd)
    
    @staticmethod
    def parse_status(response: str) -> Tuple[bool, bool]:
        """Parse status response string"""
        relay1 = "CH1:ON" in response
        relay2 = "CH2:ON" in response
        return (relay1, relay2)
    
    def __init__(self, port: Optional[str] = None, baud_rate: int = 9600):
        """Initialize protocol handler"""
        self.port = port or self.find_relay_port()
        if not self.port:
            raise RuntimeError("Could not find relay serial port")
            
        self.serial = serial.Serial(
            port=self.port,
            baudrate=baud_rate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
    
    def close(self):
        """Close serial connection"""
        if self.serial and self.serial.is_open:
            self.serial.close()
    
    def send_command(self, cmd: bytes) -> bool:
        """Send command and verify transmission"""
        if not self.serial or not self.serial.is_open:
            raise RuntimeError("Serial port not open")
            
        bytes_written = self.serial.write(cmd)
        return bytes_written == len(cmd)
    
    def read_response(self, timeout_ms: int = 100) -> Optional[str]:
        """Read response with timeout"""
        if not self.serial or not self.serial.is_open:
            raise RuntimeError("Serial port not open")
            
        # Wait for data
        start_time = time.time()
        while (time.time() - start_time) * 1000 < timeout_ms:
            if self.serial.in_waiting:
                return self.serial.read_until(b'\n').decode('ascii')
            time.sleep(0.01)
            
        return None
    
    def set_relay(self, relay_num: int, state: bool) -> bool:
        """Set relay state"""
        cmd = self.build_command(relay_num, state)
        return self.send_command(cmd)
    
    def query_status(self) -> Tuple[bool, bool]:
        """Query relay status"""
        # Send query command
        self.send_command(bytes([self.QUERY_CMD]))
        
        # Read response
        response = self.read_response()
        if response:
            return self.parse_status(response)
        else:
            raise RuntimeError("No response to status query")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

def main():
    """Test the protocol implementation"""
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        with RelayProtocol() as relay:
            # Query initial status
            logger.info("Querying initial status...")
            status = relay.query_status()
            logger.info(f"Relay states: 1={'ON' if status[0] else 'OFF'}, 2={'ON' if status[1] else 'OFF'}")
            
            # Test sequence
            test_sequence = [
                (1, True),   # Relay 1 ON
                (1, False),  # Relay 1 OFF
                (2, True),   # Relay 2 ON
                (2, False),  # Relay 2 OFF
            ]
            
            for relay_num, state in test_sequence:
                logger.info(f"\nSetting Relay {relay_num} {'ON' if state else 'OFF'}")
                if relay.set_relay(relay_num, state):
                    logger.info("Command sent successfully")
                    
                    # Verify state
                    time.sleep(0.1)
                    status = relay.query_status()
                    logger.info(f"New states: 1={'ON' if status[0] else 'OFF'}, 2={'ON' if status[1] else 'OFF'}")
                else:
                    logger.error("Failed to send command")
                
                time.sleep(1)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.debug(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main() 