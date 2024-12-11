#!/usr/bin/env python3
"""
NOYITO USB Relay Controller

Main controller class for NOYITO 2-channel USB relay.
Uses serial protocol for M-series Mac compatibility.
"""

import json
import logging
import time
from typing import Dict, Optional, Tuple
from serial_protocol import RelayProtocol

class RelayController:
    """Controller for NOYITO USB Relay"""
    
    def __init__(self, config_file: str = "config.json"):
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load config
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            raise
            
        self.protocol = None
        self.connected = False
        self.relay_states = [False, False]  # State of relay 1 and 2
    
    def connect(self) -> bool:
        """Connect to the relay device"""
        try:
            # Initialize protocol handler
            self.protocol = RelayProtocol(
                baud_rate=self.config.get('relay_baud_rate', 9600)
            )
            
            # Test connection by querying status
            self.relay_states = list(self.protocol.query_status())
            self.connected = True
            self.logger.info("✓ Successfully connected to relay")
            self.logger.info(f"Current states: Relay1={'ON' if self.relay_states[0] else 'OFF'}, Relay2={'ON' if self.relay_states[1] else 'OFF'}")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            import traceback
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return False
    
    def get_relay_states(self) -> Tuple[bool, bool]:
        """Query current relay states"""
        if not self.connected:
            self.logger.error("Not connected to relay")
            return tuple(self.relay_states)
            
        try:
            self.relay_states = list(self.protocol.query_status())
            self.logger.debug(f"Current states: Relay1={'ON' if self.relay_states[0] else 'OFF'}, Relay2={'ON' if self.relay_states[1] else 'OFF'}")
            return tuple(self.relay_states)
            
        except Exception as e:
            self.logger.error(f"Error reading relay states: {e}")
            return tuple(self.relay_states)
    
    def set_relay(self, relay_num: int, state: bool) -> bool:
        """Set state of a specific relay"""
        if not self.connected:
            self.logger.error("Not connected to relay")
            return False
            
        if relay_num not in [1, 2]:
            self.logger.error("Invalid relay number. Must be 1 or 2")
            return False
            
        self.logger.info(f"\nSetting Relay {relay_num} {'ON' if state else 'OFF'}")
        
        try:
            # Get current states first
            current_states = self.get_relay_states()
            self.logger.info(f"Current states before change: Relay1={'ON' if current_states[0] else 'OFF'}, Relay2={'ON' if current_states[1] else 'OFF'}")
            
            # Send command
            if self.protocol.set_relay(relay_num, state):
                # Update cached state
                self.relay_states[relay_num - 1] = state
                
                # Verify state
                time.sleep(0.1)
                actual_states = self.get_relay_states()
                if actual_states[relay_num - 1] == state:
                    self.logger.info(f"✓ Relay {relay_num} {'ON' if state else 'OFF'}")
                    return True
                else:
                    self.logger.error(f"✗ Relay {relay_num} state verification failed!")
                    self.logger.info(f"  Expected: {'ON' if state else 'OFF'}")
                    self.logger.info(f"  Actual: Relay1={'ON' if actual_states[0] else 'OFF'}, Relay2={'ON' if actual_states[1] else 'OFF'}")
                    return False
            else:
                self.logger.error("✗ Failed to send command!")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting relay: {e}")
            import traceback
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return False
    
    def set_all_relays(self, state: bool) -> bool:
        """Set state of all relays"""
        if not self.connected:
            self.logger.error("Not connected to relay")
            return False
            
        self.logger.info(f"\n=== Setting ALL Relays {'ON' if state else 'OFF'} ===")
        
        success = True
        for relay in [1, 2]:
            if not self.set_relay(relay, state):
                success = False
                break
            time.sleep(0.1)  # Small delay between relay commands
            
        return success
    
    def cleanup(self):
        """Safe cleanup of relay connection"""
        if self.connected:
            try:
                self.logger.info("\nCleaning up...")
                # Turn all relays off
                for relay in [1, 2]:
                    self.set_relay(relay, False)
                    time.sleep(0.1)
                if self.protocol:
                    self.protocol.close()
                self.logger.info("✓ Relay connection closed")
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")
                import traceback
                self.logger.debug(f"Traceback: {traceback.format_exc()}")

def main():
    """Test the relay controller"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=== NOYITO USB Relay Test ===")
    
    try:
        # Initialize controller
        controller = RelayController()
        
        # Connect to relay
        if not controller.connect():
            logger.error("Failed to connect to relay!")
            return
        
        # Test sequence
        logger.info("\nStarting test sequence...")
        
        # Test individual relays
        logger.info("\nTesting individual relays...")
        
        # Relay 1
        controller.set_relay(1, True)   # ON
        time.sleep(1)
        controller.set_relay(1, False)  # OFF
        time.sleep(1)
        
        # Relay 2
        controller.set_relay(2, True)   # ON
        time.sleep(1)
        controller.set_relay(2, False)  # OFF
        time.sleep(1)
        
        # Test both relays
        logger.info("\nTesting both relays...")
        controller.set_all_relays(True)   # All ON
        time.sleep(1)
        controller.set_all_relays(False)  # All OFF
        
        logger.info("\nTest sequence complete!")
        
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test error: {e}")
        import traceback
        logger.debug(f"Traceback: {traceback.format_exc()}")
    finally:
        # Cleanup
        logger.info("\nCleaning up...")
        if 'controller' in locals():
            controller.cleanup()

if __name__ == "__main__":
    main() 