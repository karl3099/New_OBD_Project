import logging
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('battery_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

import json
import time
from datetime import datetime
import obd
import signal
from dataclasses import dataclass
from typing import Optional, List, Dict
import math
import os
from hidapi import hid

logger = logging.getLogger(__name__)

@dataclass
class CycleData:
    start_time: float
    start_voltage: float
    start_current: float
    measurements: List[Dict]
    cycle_type: str  # 'charge' or 'discharge'

def connect_obd(port: str = None, baudrate: int = None) -> Optional[obd.OBD]:
    """Connect to OBD-II adapter"""
    try:
        logger.info("Connecting to OBD-II adapter...")
        connection = obd.OBD(portstr=port, baudrate=baudrate)
        
        if not connection.is_connected():
            raise RuntimeError("Failed to connect to OBD-II adapter")
            
        logger.info("Successfully connected to OBD-II adapter")
        return connection
        
    except Exception as e:
        logger.error(f"Error connecting to OBD-II adapter: {e}")
        return None 