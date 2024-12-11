# NOYITO 5V 2-Channel Micro USB Relay Module

## Hardware Specifications

### Features
1. Onboard high-performance microcontrollers chip
2. Onboard CH340 USB control chip
3. Onboard power LED and relay status LED
4. Onboard 2-way 5V relays
   - Contact ratings: 10A/250VAC, 10A/30VDC
   - Relay life: 10 million operations
5. Protection features:
   - Overcurrent protection
   - Relay diode freewheeling protection

### Physical Specifications
- Board dimensions: 50mm × 40mm

### Interface Description
Relay 1:
- COM1: Common terminal
- NC1: Normally Closed terminal
- NO1: Normally Open terminal

Relay 2:
- COM2: Common terminal
- NC2: Normally Closed terminal
- NO2: Normally Open terminal

## Software Requirements

### System Requirements
1. Operating System:
   - Windows: Windows 7 or later
   - macOS: macOS 10.12 or later
   - Linux: Most modern distributions

2. Required Drivers:
   - CH340 USB to Serial driver
   - Installation varies by OS (see driver installation section)

3. Python Requirements:
   ```
   pyserial>=3.5
   ```

### Communication Protocol

#### Basic Parameters
- Communication type: Serial over USB
- Baud rate: 9600 BPS
- Data bits: 8
- Parity: None
- Stop bits: 1

#### Command Format
Each command consists of 4 bytes:
1. Start Flag (1 byte): 0xA0
2. Switch Address (1 byte): 0x01 or 0x02
3. Operation (1 byte): 0x00 (OFF) or 0x01 (ON)
4. Checksum (1 byte): Sum of bytes 1-3 & 0xFF

#### Command Reference

##### Control Commands
| Operation | Hex Command | Description |
|-----------|------------|-------------|
| Relay 1 ON  | A0 01 01 A2 | Turn on first relay |
| Relay 1 OFF | A0 01 00 A1 | Turn off first relay |
| Relay 2 ON  | A0 02 01 A3 | Turn on second relay |
| Relay 2 OFF | A0 02 00 A2 | Turn off second relay |

##### Status Query
Command: 0xFF (single byte)

Response Format:
```
CH1:ON \r\n
CH2:ON \r\n
CH3:OFF\r\n
CH4:OFF\r\n
```
Note: Each channel returns 10 bytes of information

#### Checksum Calculation
```python
def calculate_checksum(data: List[int]) -> int:
    """Calculate command checksum"""
    return sum(data) & 0xFF
```

## Driver Installation

### Windows
1. Download CH340 driver from manufacturer website
2. Run setup executable
3. Verify in Device Manager under "Ports (COM & LPT)"

### macOS
1. Download CH340 driver for macOS
2. Install .pkg file
3. Approve in System Preferences → Security & Privacy
4. Restart computer
5. Verify in System Report under USB

### Linux
Most modern Linux distributions include the CH340 driver (ch341).
To verify:
```bash
lsmod | grep ch341
```

If not present, install:
```bash
sudo modprobe ch341
```

## Usage Examples

### Python Example
```python
import serial

# Open serial port
ser = serial.Serial(
    port='/dev/ttyUSB0',  # or 'COM3' on Windows
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE
)

# Turn on Relay 1
command = bytes([0xA0, 0x01, 0x01, 0xA2])
ser.write(command)

# Query Status
ser.write(bytes([0xFF]))
status = ser.read_until(b'\n').decode('ascii')
print(f"Status: {status}")
```

### Serial Terminal Example
Using any serial terminal (e.g., SSCOM32, minicom, screen):
1. Connect at 9600 baud
2. Send hex commands:
   - `A0 01 01 A2` - Relay 1 ON
   - `A0 01 00 A1` - Relay 1 OFF
   - `FF` - Query status

## Troubleshooting

### Common Issues
1. Device not recognized
   - Verify CH340 driver installation
   - Check USB cable
   - Try different USB port

2. Communication errors
   - Verify baud rate is 9600
   - Check command format and checksum
   - Ensure correct port permissions

3. Relay not responding
   - Verify power LED is on
   - Check USB connection
   - Test with status query command

### LED Indicators
- Power LED: Indicates USB power
- Relay LEDs: Show current relay states

## Safety Considerations

1. Electrical Safety
   - Do not exceed relay ratings (10A/250VAC, 10A/30VDC)
   - Ensure proper grounding
   - Use appropriate wire gauge

2. Operating Environment
   - Keep away from moisture
   - Avoid extreme temperatures
   - Maintain adequate ventilation

3. Protection Features
   - Built-in overcurrent protection
   - Diode protection for relay coils
   - Isolation between USB and relay circuits
``` 