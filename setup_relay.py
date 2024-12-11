#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    print("\nChecking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    print(f"Python version {version.major}.{version.minor}.{version.micro} - OK")

def check_pip():
    """Check if pip is installed and up to date"""
    print("\nChecking pip installation...")
    try:
        import pip
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        print("pip is installed and up to date")
    except:
        print("Error: pip is not installed or cannot be upgraded")
        sys.exit(1)

def install_system_dependencies():
    """Install system-level dependencies"""
    system = platform.system().lower()
    print(f"\nInstalling system dependencies for {system}...")
    
    try:
        if system == 'darwin':  # macOS
            if not shutil.which('brew'):
                print("Installing Homebrew...")
                subprocess.check_call(['/bin/bash', '-c', 
                    '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'])
            
            print("Installing hidapi via Homebrew...")
            subprocess.check_call(['brew', 'install', 'hidapi'])
            
        elif system == 'linux':
            # Check for different package managers
            if shutil.which('apt-get'):  # Debian/Ubuntu
                subprocess.check_call(['sudo', 'apt-get', 'update'])
                subprocess.check_call(['sudo', 'apt-get', 'install', '-y',
                    'libhidapi-dev', 'python3-dev', 'build-essential'])
            elif shutil.which('dnf'):  # Fedora
                subprocess.check_call(['sudo', 'dnf', 'install', '-y',
                    'hidapi-devel', 'python3-devel', 'gcc'])
            elif shutil.which('pacman'):  # Arch
                subprocess.check_call(['sudo', 'pacman', '-Sy',
                    'hidapi', 'python-pip'])
            else:
                print("Warning: Unsupported Linux distribution")
                print("Please install hidapi and development tools manually")
        
        elif system == 'windows':
            print("Note: On Windows, required DLLs will be installed with pip packages")
        
        else:
            print(f"Warning: Unsupported operating system: {system}")
            print("Please install hidapi manually")
            
    except subprocess.CalledProcessError as e:
        print(f"Error installing system dependencies: {e}")
        sys.exit(1)

def setup_udev_rules():
    """Setup udev rules on Linux"""
    if platform.system().lower() == 'linux':
        print("\nSetting up udev rules...")
        rule = 'SUBSYSTEM=="hidraw", ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="05df", MODE="0666"'
        rule_path = '/etc/udev/rules.d/50-usb-relay.rules'
        
        try:
            with open('50-usb-relay.rules', 'w') as f:
                f.write(rule)
            
            subprocess.check_call(['sudo', 'mv', '50-usb-relay.rules', rule_path])
            subprocess.check_call(['sudo', 'udevadm', 'control', '--reload-rules'])
            subprocess.check_call(['sudo', 'udevadm', 'trigger'])
            print("udev rules installed successfully")
        except Exception as e:
            print(f"Error setting up udev rules: {e}")
            print("You may need to run with sudo or set up rules manually")

def install_python_requirements():
    """Install Python package requirements"""
    print("\nInstalling Python requirements...")
    try:
        # First install build dependencies
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade',
            'wheel', 'setuptools'])
        
        # Then install project requirements
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Python requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Python requirements: {e}")
        sys.exit(1)

def verify_installation():
    """Verify the installation"""
    print("\nVerifying installation...")
    try:
        # Try importing key modules
        import hid
        
        # List HID devices
        print("\nDetected HID devices:")
        for device in hid.enumerate():
            print(f"\nVID:PID: {device['vendor_id']:04x}:{device['product_id']:04x}")
            print(f"Manufacturer: {device.get('manufacturer_string', 'N/A')}")
            print(f"Product: {device.get('product_string', 'N/A')}")
            
            # Check if it's our relay
            if device['vendor_id'] == 0x16c0 and device['product_id'] == 0x05df:
                print("*** NOYITO USB Relay detected! ***")
        
        print("\nInstallation verification complete!")
        return True
    except Exception as e:
        print(f"Verification failed: {e}")
        return False

def main():
    """Main setup process"""
    print("=== USB HID Relay Setup ===")
    
    check_python_version()
    check_pip()
    install_system_dependencies()
    setup_udev_rules()
    install_python_requirements()
    
    if verify_installation():
        print("\nSetup completed successfully!")
        print("\nYou can now run the relay test with:")
        print("python3 simple_test.py")
    else:
        print("\nSetup completed with some issues.")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main() 