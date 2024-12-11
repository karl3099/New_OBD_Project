# USB Relay Control Project

A Python-based control system for NOYITO USB relay modules, supporting both Mac and Windows platforms.

## Features

- HID and Serial protocol support
- Cross-platform compatibility (Mac/Windows)
- Interactive command-line interface
- Automatic device detection
- Clean shutdown handling
- Comprehensive error handling

## Requirements

- Python 3.8+
- hidapi
- pyserial
- pyusb (Windows only)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/karl3099/New_OBD_Project.git
cd New_OBD_Project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install system requirements:

### Mac
- Install CH340 driver (included in `install_ch340_mac.py`)
```bash
python3 install_ch340_mac.py
```

### Windows
- Install USB drivers from manufacturer's website

## Usage

### Simple HID Control
```bash
python3 src/relay_hid_simple.py
```

### Cross-Platform Control
```bash
python3 src/relay_unified.py
```

### Serial Protocol Control
```bash
python3 src/relay_serial_test.py
```

## Project Structure

```
.
├── README.md
├── requirements.txt
├── config.json
├── docs/
│   ├── NOYITO_USB_RELAY_REFERENCE.md
│   └── mac_m_series_rules.txt
├── scripts/
│   ├── install_ch340_mac.py
│   └── detect_usb.py
└── src/
    ├── relay_hid_simple.py
    ├── relay_unified.py
    └── relay_serial_test.py
```

## Documentation

- [NOYITO USB Relay Reference](docs/NOYITO_USB_RELAY_REFERENCE.md)
- [Mac M-Series Development Rules](docs/mac_m_series_rules.txt)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- NOYITO for the USB relay hardware
- hidapi developers
- pyserial developers 