#!/usr/bin/env python3
"""
CH340 Driver Installer for Mac
Downloads and installs the official CH340 driver
"""

import os
import sys
import subprocess
import tempfile
import shutil
import requests
from pathlib import Path

def check_system():
    """Check system compatibility"""
    print("Checking system...")
    
    if sys.platform != 'darwin':
        print("Error: This script is for macOS only")
        return False
    
    print(f"Architecture: {subprocess.check_output(['uname', '-m']).decode().strip()}")
    print(f"macOS version: {subprocess.check_output(['sw_vers', '-productVersion']).decode().strip()}")
    return True

def download_driver(temp_dir):
    """Download CH340 driver"""
    print("\nDownloading CH340 driver...")
    
    # Direct download URL for Mac driver
    url = "http://www.wch.cn/downloads/file/178.html"
    
    try:
        # Download driver
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()
        
        # Save to temporary file
        zip_path = os.path.join(temp_dir, "CH34xVCPDriver.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        print("✓ Download complete")
        return zip_path
    except Exception as e:
        print(f"Error downloading driver: {e}")
        print("\nPlease download manually:")
        print("1. Visit: http://www.wch.cn/downloads/CH341SER_MAC_ZIP.html")
        print("2. Click the download button")
        print("3. Save the file as 'CH34xVCPDriver.zip'")
        print("4. Move the file to the current directory")
        
        # Wait for manual download
        while True:
            if os.path.exists('CH34xVCPDriver.zip'):
                return os.path.abspath('CH34xVCPDriver.zip')
            input("Press Enter after downloading the file (or Ctrl+C to cancel)...")

def install_driver(pkg_path):
    """Install driver package"""
    print("\nInstalling driver...")
    print("This will require administrator privileges")
    
    try:
        # Unload existing driver if present
        subprocess.run(['sudo', 'kextunload', '-b', 'com.wch.ch34xseria'], 
                      capture_output=True, check=False)
        
        # Install new driver
        subprocess.run(['sudo', 'installer', '-pkg', pkg_path, '-target', '/'], 
                      check=True)
        
        # Load new driver
        subprocess.run(['sudo', 'kextload', '-b', 'com.wch.ch34xseria'], 
                      capture_output=True, check=False)
        
        print("✓ Installation complete")
        return True
    except Exception as e:
        print(f"Error installing driver: {e}")
        return False

def setup_permissions():
    """Setup correct permissions"""
    print("\nSetting up permissions...")
    
    try:
        # Get current user
        user = subprocess.check_output(['whoami']).decode().strip()
        
        # Set permissions on USB devices
        subprocess.run(['sudo', 'chmod', '666', '/dev/tty.*'], check=False)
        
        print("✓ Permissions setup complete")
        return True
    except Exception as e:
        print(f"Error setting permissions: {e}")
        return False

def main():
    """Main installation routine"""
    print("=== CH340 Driver Installation ===")
    
    try:
        # Check system
        if not check_system():
            return
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download driver
            zip_path = download_driver(temp_dir)
            
            # Extract package
            print("\nExtracting driver package...")
            extract_dir = os.path.join(temp_dir, 'driver')
            os.makedirs(extract_dir, exist_ok=True)
            shutil.unpack_archive(zip_path, extract_dir)
            
            # Find installer package
            pkg_file = None
            for root, _, files in os.walk(extract_dir):
                for file in files:
                    if file.endswith('.pkg'):
                        pkg_file = os.path.join(root, file)
                        break
            
            if not pkg_file:
                print("Error: Could not find installer package")
                return
            
            # Install driver
            if not install_driver(pkg_file):
                return
            
            # Setup permissions
            setup_permissions()
        
        print("\n✓ CH340 driver installation complete!")
        print("\nImportant steps:")
        print("1. Open System Settings → Privacy & Security")
        print("2. Look for message about blocked kernel extension")
        print("3. Click 'Allow' to approve the CH340 driver")
        print("4. Restart your computer")
        
    except KeyboardInterrupt:
        print("\nInstallation interrupted")
    except Exception as e:
        print(f"\nInstallation failed: {e}")

if __name__ == "__main__":
    main() 