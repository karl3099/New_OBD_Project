import obd

def print_command_info(cmd):
    print(f"Name: {cmd.name}")
    print(f"Command: {cmd.command}")
    print(f"Description: {cmd.desc}")
    print(f"Return Value: {cmd.returnValue}")
    print("-" * 50)

print("OBD package version:", obd.__version__)
print(f"\nTotal available OBD commands: {len(obd.commands)}\n")
print("Available OBD Commands and PIDs:")
print("-" * 50)

# Print common commands first
common_commands = [
    obd.commands.SPEED,              # Vehicle Speed
    obd.commands.RPM,               # Engine RPM
    obd.commands.FUEL_LEVEL,        # Fuel Level
    obd.commands.THROTTLE_POS,      # Throttle Position
    obd.commands.ENGINE_LOAD,       # Engine Load
    obd.commands.COOLANT_TEMP,      # Coolant Temperature
    obd.commands.INTAKE_TEMP,       # Intake Temperature
    obd.commands.VOLTAGE,           # Battery Voltage
    obd.commands.TIMING_ADVANCE,    # Timing Advance
    obd.commands.MAF,               # Mass Air Flow
    obd.commands.O2_SENSORS,        # O2 Sensors
    obd.commands.FUEL_STATUS,       # Fuel System Status
]

print("\nCommonly Used Commands:")
for cmd in common_commands:
    if cmd:  # Some commands might be None if not supported
        print_command_info(cmd)

print("\nTesting OBD connection...")
try:
    connection = obd.OBD()
    print("Connection status:", connection.status())
    print("Protocol:", connection.protocol_name())
    
    if connection.is_connected():
        print("\nSupported Commands on Connected Vehicle:")
        for cmd in connection.supported_commands:
            print_command_info(cmd)
except Exception as e:
    print("Error:", e) 