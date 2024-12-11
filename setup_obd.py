import sys
import os
import subprocess
import platform
import time

def check_python_version():
    print("\nChecking Python version...")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        raise SystemError("Python 3.6 or higher is required")

def run_command(command, check=True, shell=False):
    """Run command and return output"""
    try:
        result = subprocess.run(
            command,
            check=check,
            shell=shell,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(command)}")
        print(f"Error: {e.stderr}")
        return None

def check_macos_dependencies():
    print("\nChecking macOS dependencies...")
    
    # Check if Homebrew is installed
    if not run_command(["which", "brew"]):
        print("Homebrew not found. Installing Homebrew...")
        install_script = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        print("Please run this command in your terminal to install Homebrew:")
        print(install_script)
        return False
    
    print("Homebrew is installed")
    
    # Update Homebrew
    print("\nUpdating Homebrew...")
    run_command(["brew", "update"])
    
    # Required Homebrew packages
    brew_packages = [
        "libusb",
        "hidapi",
        "python@3.9"  # Ensure consistent Python version
    ]
    
    for package in brew_packages:
        print(f"\nChecking {package}...")
        if not run_command(["brew", "list", package], check=False):
            print(f"Installing {package}...")
            if not run_command(["brew", "install", package]):
                print(f"Failed to install {package}")
                return False
        else:
            print(f"{package} is already installed")
    
    return True

def check_python_packages():
    print("\nChecking Python packages...")
    
    # Upgrade pip first
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    required_packages = {
        "pyserial": "pyserial>=3.5",
        "python-OBD": "git+https://github.com/brendan-w/python-OBD.git#egg=obd",
        "pyusb": "pyusb>=1.2.1",
        "hidapi": "hidapi>=0.14.0"
    }
    
    for package, install_spec in required_packages.items():
        print(f"\nInstalling {package}...")
        try:
            run_command([sys.executable, "-m", "pip", "install", "--upgrade", install_spec])
        except Exception as e:
            print(f"Failed to install {package}: {e}")
            return False
    
    return True

def check_usb_devices():
    print("\nChecking USB devices...")
    
    # Check USB devices using system_profiler
    usb_info = run_command(["system_profiler", "SPUSBDataType"])
    print("\nAvailable USB devices:")
    print(usb_info)
    
    return True

def check_serial_ports():
    print("\nChecking serial ports...")
    
    # List all potential serial ports
    serial_ports = run_command(["ls", "/dev/tty.*"])
    print("\nAvailable serial ports:")
    print(serial_ports)
    
    return True

def check_obd_connection():
    print("\nChecking OBD adapter connection...")
    try:
        import obd
        
        # Try to detect the adapter
        ports = obd.scan_serial()
        if not ports:
            print("No OBD adapters found. Available ports:")
            print(run_command(["ls", "/dev/tty.*"]))
            return False
        
        print(f"Found OBD ports: {ports}")
        
        # Try to connect
        connection = obd.OBD()
        if not connection.is_connected():
            print("\nOBD adapter not found. Please check:")
            print("1. Adapter is properly plugged in")
            print("2. Adapter appears in System Information → USB")
            print("3. Adapter creates a serial port in /dev/tty.*")
            print("4. Vehicle ignition is on")
            return False
        
        print("\nOBD adapter connected successfully!")
        print(f"Protocol: {connection.protocol_name()}")
        print("Port:", connection.port_name())
        print("Status:", connection.status())
        return True
        
    except Exception as e:
        print(f"Error checking OBD connection: {e}")
        return False

def main():
    print("=== macOS OBD Setup and Requirements Check ===")
    
    if platform.system() != "Darwin":
        print("This script is for macOS only!")
        return
    
    try:
        check_python_version()
        
        if not check_macos_dependencies():
            print("\nFailed to install macOS dependencies")
            return
            
        if not check_python_packages():
            print("\nFailed to install Python packages")
            return
        
        check_usb_devices()
        check_serial_ports()
        
        print("\nAll requirements installed successfully!")
        
        print("\nTesting OBD connection...")
        if check_obd_connection():
            print("\nSetup completed successfully!")
        else:
            print("\nSetup completed but OBD connection failed.")
            print("You can still proceed with the software, but please check your OBD adapter connection.")
        
    except Exception as e:
        print(f"\nSetup failed: {e}")
        return

if __name__ == "__main__":
    main() 