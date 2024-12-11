#!/usr/bin/env python3
"""
CH340 Driver Installation Helper for Mac
Downloads and installs the official WCH CH340 driver
"""

import os
import sys
import subprocess
import logging
import tempfile
import shutil
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

def check_system():
    """Check if system is compatible"""
    logger.info("Checking system compatibility...")
    
    # Check if running on Mac
    if sys.platform != 'darwin':
        raise RuntimeError("This script is for macOS only")
    
    # Check architecture
    arch = subprocess.check_output(['uname', '-m']).decode().strip()
    logger.info(f"Architecture: {arch}")
    
    # Check macOS version
    os_ver = subprocess.check_output(['sw_vers', '-productVersion']).decode().strip()
    logger.info(f"macOS version: {os_ver}")
    
    return True

def download_manual():
    """Provide manual download instructions"""
    logger.info("\nPlease download the driver manually:")
    logger.info("1. Visit: https://www.wch.cn/downloads/CH341SER_MAC_ZIP.html")
    logger.info("2. Click the download button")
    logger.info("3. Save the file as 'CH341SER_MAC.ZIP'")
    logger.info("4. Move the file to the current directory")
    
    while not os.path.exists('CH341SER_MAC.ZIP'):
        input("\nPress Enter after downloading the file...")
    
    return os.path.abspath('CH341SER_MAC.ZIP')

def extract_driver(zip_path, temp_dir):
    """Extract driver package"""
    logger.info("\nExtracting driver package...")
    
    try:
        extract_dir = os.path.join(temp_dir, 'driver')
        os.makedirs(extract_dir, exist_ok=True)
        
        # Extract zip file
        shutil.unpack_archive(zip_path, extract_dir)
        logger.info("✓ Extraction complete")
        
        # Find .pkg file
        for root, _, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.pkg'):
                    return os.path.join(root, file)
        
        raise RuntimeError("Could not find driver package")
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise

def install_driver(pkg_path):
    """Install driver package"""
    logger.info("\nInstalling driver...")
    logger.info("This will require administrator privileges")
    
    try:
        # First, unload any existing driver
        subprocess.run(['sudo', 'kextunload', '-b', 'com.wch.ch34xseria'], 
                      capture_output=True, check=False)
        
        # Install new driver
        cmd = ['sudo', 'installer', '-pkg', pkg_path, '-target', '/']
        subprocess.run(cmd, check=True)
        
        # Load the new driver
        subprocess.run(['sudo', 'kextload', '-b', 'com.wch.ch34xseria'], 
                      capture_output=True, check=False)
        
        logger.info("✓ Installation complete")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Installation failed: {e}")
        return False

def verify_installation():
    """Verify driver installation"""
    logger.info("\nVerifying installation...")
    
    try:
        # Check kext
        kexts = subprocess.check_output(['kextstat']).decode()
        if 'ch34x' in kexts.lower():
            logger.info("✓ Driver loaded successfully")
            return True
        
        # Check device nodes
        devices = subprocess.check_output(['ls', '/dev/tty.*'], 
                                       stderr=subprocess.DEVNULL).decode()
        if any('wchusbserial' in dev.lower() for dev in devices.split()):
            logger.info("✓ CH340 device nodes found")
            return True
        
        logger.warning("! Driver installed but not loaded")
        logger.info("Please approve the driver in System Settings → Privacy & Security")
        return False
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False

def setup_permissions():
    """Setup correct permissions for serial device"""
    logger.info("\nSetting up permissions...")
    
    try:
        # Get current user
        user = subprocess.check_output(['whoami']).decode().strip()
        
        # Add user to dialout group (if it exists)
        subprocess.run(['sudo', 'dseditgroup', '-o', 'edit', '-a', user, '-t', 'user', 'dialout'], 
                      check=False)
        
        # Set permissions on potential device nodes
        subprocess.run(['sudo', 'chmod', '666', '/dev/tty.*'], check=False)
        
        logger.info("✓ Permissions setup complete")
        return True
    except Exception as e:
        logger.error(f"Permission setup failed: {e}")
        return False

def main():
    """Main installation routine"""
    logger.info("=== CH340 Driver Installation ===")
    
    try:
        # Check system compatibility
        check_system()
        
        # Get driver file
        zip_path = download_manual()
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract package
            pkg_path = extract_driver(zip_path, temp_dir)
            
            # Install driver
            if not install_driver(pkg_path):
                raise RuntimeError("Driver installation failed")
            
            # Setup permissions
            setup_permissions()
            
            # Verify installation
            verify_installation()
        
        logger.info("\n✓ CH340 driver installation complete!")
        logger.info("\nImportant steps:")
        logger.info("1. Open System Settings → Privacy & Security")
        logger.info("2. Look for message about blocked kernel extension")
        logger.info("3. Click 'Allow' to approve the CH340 driver")
        logger.info("4. Restart your computer for the changes to take effect")
        
    except KeyboardInterrupt:
        logger.info("\nInstallation interrupted by user")
    except Exception as e:
        logger.error(f"\nInstallation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 