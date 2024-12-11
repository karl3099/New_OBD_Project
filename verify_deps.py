#!/usr/bin/env python3
"""
Dependency Verification Tool

Verifies all required dependencies for the NOYITO USB Relay project.
Specifically handles M-series Mac requirements.
"""

import sys
import os
import logging
import platform
import subprocess
from typing import List, Dict

class DependencyVerifier:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.missing_packages = []
        self.hardware_issues = []
        self.system_issues = []
        
        # Required Python packages
        self.required_packages = {
            "pyserial": "pyserial>=3.5",
            "psutil": "psutil>=5.9.0",
            "python-dateutil": "python-dateutil>=2.8.2"
        }
        
        # Required system packages
        if platform.system() == "Darwin":  # macOS
            self.brew_packages = ["libusb"]  # No longer need hidapi
        else:
            self.brew_packages = []
            
    def check_python_packages(self):
        """Check required Python packages"""
        self.logger.info("Checking Python packages...")
        
        import pkg_resources
        installed = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        
        for package, requirement in self.required_packages.items():
            try:
                pkg_resources.require(requirement)
                self.logger.info(f"✓ {package} {installed.get(package, 'unknown version')}")
            except Exception as e:
                self.missing_packages.append(requirement)
                self.logger.warning(f"✗ {package} not found: {e}")
                
    def check_system_packages(self):
        """Check required system packages"""
        self.logger.info("\nChecking system packages...")
        
        if platform.system() == "Darwin":
            try:
                # Check if Homebrew is installed
                subprocess.run(["brew", "--version"], capture_output=True, check=True)
                
                # Check each required package
                for package in self.brew_packages:
                    result = subprocess.run(["brew", "list", package], capture_output=True)
                    if result.returncode == 0:
                        self.logger.info(f"✓ {package}")
                    else:
                        self.system_issues.append(f"Missing Homebrew package: {package}")
                        self.logger.warning(f"✗ {package} not installed")
            except Exception as e:
                self.system_issues.append("Homebrew not found")
                self.logger.warning(f"✗ Homebrew not found: {e}")
                
    def check_hardware_support(self):
        """Check hardware support"""
        self.logger.info("\nChecking hardware support...")
        
        # Check serial ports
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            self.logger.info(f"Found {len(ports)} serial ports")
            
            # Look for CH340 device
            ch340_ports = list(serial.tools.list_ports.grep("CH340"))
            if ch340_ports:
                self.logger.info("✓ Found CH340 USB-Serial device")
                for port in ch340_ports:
                    self.logger.info(f"  Port: {port.device}")
                    self.logger.info(f"  Description: {port.description}")
                    self.logger.info(f"  Hardware ID: {port.hwid}")
            else:
                self.hardware_issues.append("No CH340 USB-Serial device found")
                self.logger.warning("✗ No CH340 USB-Serial device found")
                
        except Exception as e:
            self.hardware_issues.append(f"Serial port error: {e}")
            self.logger.warning(f"✗ Error checking serial ports: {e}")
            
    def check_permissions(self):
        """Check required permissions"""
        self.logger.info("\nChecking permissions...")
        
        if platform.system() == "Darwin":
            # Check USB device access
            try:
                subprocess.run(["system_profiler", "SPUSBDataType"], capture_output=True, check=True)
                self.logger.info("✓ Has USB device access")
            except Exception as e:
                self.system_issues.append("No USB device access")
                self.logger.warning(f"✗ No USB device access: {e}")
                
            # Check serial port access
            try:
                for dev in os.listdir("/dev"):
                    if dev.startswith("tty.") or dev.startswith("cu."):
                        path = os.path.join("/dev", dev)
                        if os.access(path, os.R_OK | os.W_OK):
                            self.logger.info(f"✓ Has access to {path}")
                        else:
                            self.system_issues.append(f"No access to {path}")
                            self.logger.warning(f"✗ No access to {path}")
            except Exception as e:
                self.system_issues.append("Error checking serial port permissions")
                self.logger.warning(f"✗ Error checking serial port permissions: {e}")
                
    def verify_all(self) -> bool:
        """Run all verification checks"""
        self.check_python_packages()
        self.check_system_packages()
        self.check_hardware_support()
        self.check_permissions()
        
        # Report results
        self.logger.info("\n=== Verification Results ===")
        
        if self.missing_packages:
            self.logger.warning("\nMissing Python packages:")
            for pkg in self.missing_packages:
                self.logger.warning(f"  - {pkg}")
                
        if self.system_issues:
            self.logger.warning("\nSystem issues:")
            for issue in self.system_issues:
                self.logger.warning(f"  - {issue}")
                
        if self.hardware_issues:
            self.logger.warning("\nHardware issues:")
            for issue in self.hardware_issues:
                self.logger.warning(f"  - {issue}")
                
        if not any([self.missing_packages, self.system_issues, self.hardware_issues]):
            self.logger.info("\n✓ All checks passed!")
            return True
        else:
            self.logger.error("\n✗ Some checks failed")
            return False
            
    def fix_issues(self):
        """Try to fix any issues found"""
        self.logger.info("\n=== Attempting to fix issues ===")
        
        # Install missing Python packages
        if self.missing_packages:
            self.logger.info("\nInstalling missing Python packages...")
            for package in self.missing_packages:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
                    self.logger.info(f"✓ Installed {package}")
                except Exception as e:
                    self.logger.error(f"✗ Failed to install {package}: {e}")
                    
        # Install system packages
        if platform.system() == "Darwin" and self.system_issues:
            if "Homebrew not found" in self.system_issues:
                self.logger.error("Please install Homebrew first: https://brew.sh")
            else:
                for package in self.brew_packages:
                    try:
                        subprocess.run(["brew", "install", package], check=True)
                        self.logger.info(f"✓ Installed {package}")
                    except Exception as e:
                        self.logger.error(f"✗ Failed to install {package}: {e}")
                        
        # Fix permissions
        if platform.system() == "Darwin" and any("access" in issue.lower() for issue in self.system_issues):
            self.logger.info("\nTo fix permission issues:")
            self.logger.info("1. Open System Preferences → Security & Privacy → Privacy")
            self.logger.info("2. Select 'Full Disk Access'")
            self.logger.info("3. Click the lock to make changes")
            self.logger.info("4. Add Terminal or your IDE")
            self.logger.info("\nFor serial port access:")
            self.logger.info("sudo chmod 666 /dev/tty.*")

def main():
    """Main verification function"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=== Dependency Verifier ===")
    
    verifier = DependencyVerifier()
    
    try:
        if not verifier.verify_all():
            logger.info("\nWould you like to attempt to fix these issues? (y/n)")
            if input().lower() == 'y':
                verifier.fix_issues()
                
    except KeyboardInterrupt:
        logger.info("\nVerification interrupted by user")
    except Exception as e:
        logger.error(f"\nVerification error: {e}")
        import traceback
        logger.debug(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main() 