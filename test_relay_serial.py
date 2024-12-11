#!/usr/bin/env python3
"""
NOYITO USB Relay Test Script

Interactive test script for NOYITO 2-channel USB relay using serial protocol.
Supports M-series Mac with CH340 USB-to-Serial chip.
"""

import sys
import time
import logging
from serial_protocol import RelayProtocol

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def interactive_test():
    """Interactive relay testing"""
    logger.info("=== NOYITO USB Relay Test ===")
    
    try:
        with RelayProtocol() as relay:
            # Query initial status
            logger.info("\nQuerying initial status...")
            status = relay.query_status()
            logger.info(f"Current states: Relay1={'ON' if status[0] else 'OFF'}, Relay2={'ON' if status[1] else 'OFF'}")
            
            # Interactive menu
            logger.info("\nCommands:")
            logger.info("1: Toggle Relay 1")
            logger.info("2: Toggle Relay 2")
            logger.info("a: Toggle All Relays")
            logger.info("s: Show Status")
            logger.info("q: Quit")
            
            relay1_state = status[0]
            relay2_state = status[1]
            
            while True:
                try:
                    cmd = input("\nEnter command (1/2/a/s/q): ").lower()
                    
                    if cmd == 'q':
                        break
                    elif cmd == 's':
                        status = relay.query_status()
                        logger.info(f"Current states: Relay1={'ON' if status[0] else 'OFF'}, Relay2={'ON' if status[1] else 'OFF'}")
                    elif cmd == '1':
                        relay1_state = not relay1_state
                        if relay.set_relay(1, relay1_state):
                            logger.info(f"✓ Set Relay 1 {'ON' if relay1_state else 'OFF'}")
                            status = relay.query_status()
                            if status[0] != relay1_state:
                                logger.error("✗ Relay state verification failed!")
                        else:
                            logger.error("✗ Failed to set relay!")
                    elif cmd == '2':
                        relay2_state = not relay2_state
                        if relay.set_relay(2, relay2_state):
                            logger.info(f"✓ Set Relay 2 {'ON' if relay2_state else 'OFF'}")
                            status = relay.query_status()
                            if status[1] != relay2_state:
                                logger.error("✗ Relay state verification failed!")
                        else:
                            logger.error("✗ Failed to set relay!")
                    elif cmd == 'a':
                        relay1_state = relay2_state = not relay1_state
                        success = True
                        
                        # Set both relays
                        for relay_num in [1, 2]:
                            if not relay.set_relay(relay_num, relay1_state):
                                success = False
                                logger.error(f"✗ Failed to set relay {relay_num}!")
                                break
                            time.sleep(0.1)
                        
                        if success:
                            logger.info(f"✓ Set all relays {'ON' if relay1_state else 'OFF'}")
                            status = relay.query_status()
                            if status != (relay1_state, relay2_state):
                                logger.error("✗ Relay state verification failed!")
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
        logger.info("\nCleaning up...")
        try:
            # Turn all relays off for safety
            relay.set_relay(1, False)
            time.sleep(0.1)
            relay.set_relay(2, False)
        except:
            pass

if __name__ == "__main__":
    interactive_test() 