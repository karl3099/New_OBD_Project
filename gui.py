# Configure logging first
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import subprocess
import signal
import psutil

logger = logging.getLogger(__name__)

class ConfigGUI:
    def __init__(self, root):
        try:
            self.root = root
            self.root.title("Hybrid Battery Monitor Configuration")
            self.root.geometry("800x800")
            
            # Create notebook for tabs
            self.notebook = ttk.Notebook(root)
            self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
            
            # Control Panel Frame (above notebook)
            self.control_frame = ttk.LabelFrame(root, text="Monitor Controls", padding="10")
            self.control_frame.pack(fill='x', padx=10, pady=5, before=self.notebook)
            
            # Load configuration
            self.load_config()
            
            # Add control buttons
            self.setup_control_buttons()
            
            # Configuration tab
            self.config_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.config_frame, text='Configuration')
            
        except Exception as e:
            logger.error(f"Error initializing GUI: {e}")
            messagebox.showerror("Error", f"Failed to initialize application: {e}")
            raise
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
            raise

    def setup_control_buttons(self):
        # Create frames for better organization
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(fill='x', expand=True)
        
        # Status indicator
        self.status_label = ttk.Label(button_frame, text="Status: Stopped", font=('Helvetica', 10, 'bold'))
        self.status_label.pack(side='left', padx=10)
        
        # Control buttons
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_monitoring)
        self.start_button.pack(side='right', padx=5)
        
        self.pause_button = ttk.Button(button_frame, text="Pause", command=self.pause_monitoring, state='disabled')
        self.pause_button.pack(side='right', padx=5)
        
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_monitoring)
        self.reset_button.pack(side='right', padx=5)

    def update_button_states(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            state = config.get('monitoring_state', 'stopped')
            pid = config.get('monitoring_pid')
            
            # Update status label
            status_text = f"Status: {state.capitalize()}"
            if pid:
                try:
                    process = psutil.Process(pid)
                    if not process.is_running() or process.status() == psutil.STATUS_ZOMBIE:
                        status_text += " (Process Dead)"
                        # Auto-cleanup dead process
                        config['monitoring_state'] = 'stopped'
                        config['monitoring_pid'] = None
                        with open('config.json', 'w') as f:
                            json.dump(config, f, indent=4)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutError):
                    status_text += " (Process Not Found)"
                    # Auto-cleanup missing process
                    config['monitoring_state'] = 'stopped'
                    config['monitoring_pid'] = None
                    with open('config.json', 'w') as f:
                        json.dump(config, f, indent=4)
            self.status_label.config(text=status_text)
            
            # Update button states based on actual process state
            if state == 'running' and (not pid or not self._is_process_running(pid)):
                state = 'stopped'  # Override state if process is not actually running
            
            if state == 'running':
                self.start_button.config(text="Stop", command=self.stop_monitoring)
                self.pause_button.config(state='normal')
                self.reset_button.config(state='disabled')
            elif state == 'paused':
                self.start_button.config(text="Stop", command=self.stop_monitoring)
                self.pause_button.config(text="Resume", command=self.resume_monitoring, state='normal')
                self.reset_button.config(state='disabled')
            else:  # stopped
                self.start_button.config(text="Start", command=self.start_monitoring)
                self.pause_button.config(text="Pause", command=self.pause_monitoring, state='disabled')
                self.reset_button.config(state='normal')
        
        except Exception as e:
            logger.error(f"Error updating button states: {e}")
            # Don't show error dialog to avoid spamming user
            # Just log the error and try to recover
            self.start_button.config(text="Start", command=self.start_monitoring)
            self.pause_button.config(state='disabled')
            self.reset_button.config(state='normal')
        
        # Schedule next update
        self.root.after(1000, self.update_button_states)

    def _is_process_running(self, pid):
        """Helper method to check if a process is running"""
        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutError):
            return False

    def start_monitoring(self):
        try:
            # Start the monitoring script
            process = subprocess.Popen(['python', 'main.py'])
            
            # Update config with process state
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            config['monitoring_state'] = 'running'
            config['monitoring_pid'] = process.pid
            
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error starting monitoring: {e}")

    def stop_monitoring(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            pid = config.get('monitoring_pid')
            if pid:
                try:
                    process = psutil.Process(pid)
                    if process.is_running():
                        process.terminate()  # Try graceful termination first
                        try:
                            process.wait(timeout=3)  # Wait up to 3 seconds
                        except psutil.TimeoutExpired:
                            process.kill()  # Force kill if not terminated
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutError):
                    pass  # Process already terminated or inaccessible
            
            config['monitoring_state'] = 'stopped'
            config['monitoring_pid'] = None
            
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            
            logger.info("Monitoring stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
            messagebox.showerror("Error", f"Error stopping monitoring: {e}")

    def pause_monitoring(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            pid = config.get('monitoring_pid')
            if pid and self._is_process_running(pid):
                try:
                    os.kill(pid, signal.SIGSTOP)  # Pause process
                    config['monitoring_state'] = 'paused'
                    logger.info("Monitoring paused successfully")
                except ProcessLookupError:
                    logger.error("Process not found when trying to pause")
                    messagebox.showerror("Error", "Process not found when trying to pause")
                    return
            else:
                logger.error("No running process found to pause")
                messagebox.showerror("Error", "No running process found to pause")
                return
            
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            
        except Exception as e:
            logger.error(f"Error pausing monitoring: {e}")
            messagebox.showerror("Error", f"Error pausing monitoring: {e}")

    def resume_monitoring(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            pid = config.get('monitoring_pid')
            if pid and self._is_process_running(pid):
                try:
                    os.kill(pid, signal.SIGCONT)  # Resume process
                    config['monitoring_state'] = 'running'
                    logger.info("Monitoring resumed successfully")
                except ProcessLookupError:
                    logger.error("Process not found when trying to resume")
                    messagebox.showerror("Error", "Process not found when trying to resume")
                    return
            else:
                logger.error("No paused process found to resume")
                messagebox.showerror("Error", "No paused process found to resume")
                return
            
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            
        except Exception as e:
            logger.error(f"Error resuming monitoring: {e}")
            messagebox.showerror("Error", f"Error resuming monitoring: {e}")

    def reset_monitoring(self):
        try:
            # Reset cycle data
            cycle_data = {
                'charge_cycles': [],
                'discharge_cycles': []
            }
            with open(self.config['cycle_data_file'], 'w') as f:
                json.dump(cycle_data, f, indent=4)
            
            # Refresh the history view
            self.refresh_capacity_history()
            
            messagebox.showinfo("Success", "Monitoring data has been reset")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error resetting monitoring data: {e}")

    def setup_config_tab(self):
        # Create main frame
        main_frame = ttk.Frame(self.config_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create scrollable frame
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create input fields
        self.vars = {}
        
        # Temperature Settings
        self.create_section("Temperature Settings", [
            ("Maximum Temperature (°C)", "max_temp"),
            ("Temperature Delay (s)", "temp_delay")
        ])
        
        # Voltage Settings
        self.create_section("Voltage Settings", [
            ("Maximum Pack Voltage (V)", "max_voltage"),
            ("Minimum Pack Voltage (V)", "min_voltage"),
            ("Maximum Voltage Difference (V)", "max_voltage_diff"),
            ("Voltage Delay (s)", "voltage_delay"),
            ("Voltage Difference Delay (s)", "voltage_diff_delay")
        ])
        
        # Current Settings
        current_frame = ttk.LabelFrame(self.scrollable_frame, text="Current Settings", padding="5")
        current_frame.grid(row=len(self.vars), column=0, columnspan=2, sticky="ew", pady=10, padx=5)
        
        # Standard current settings
        row = 0
        for label, key in [
            ("Maximum Current (A)", "max_current"),
            ("Current Delay (s)", "current_delay"),
            ("Minimum Current Threshold (A)", "min_current_threshold"),
            ("Cycle End Current Threshold (A)", "cycle_end_current_threshold")
        ]:
            ttk.Label(current_frame, text=label).grid(row=row, column=0, padx=5, pady=2, sticky="w")
            var = tk.StringVar(value=str(self.config.get(key, "")))
            entry = ttk.Entry(current_frame, textvariable=var)
            entry.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
            self.vars[key] = var
            row += 1
            
        # Discharge resistor settings
        ttk.Separator(current_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")
        row += 1
        
        # Discharge resistor toggle and value
        resistor_frame = ttk.Frame(current_frame)
        resistor_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.vars["use_discharge_resistor"] = tk.BooleanVar(value=self.config.get("use_discharge_resistor", True))
        ttk.Checkbutton(resistor_frame, text="Use Discharge Resistor", 
                       variable=self.vars["use_discharge_resistor"]).pack(side="left", padx=5)
        
        ttk.Label(resistor_frame, text="Resistance (Ω):").pack(side="left", padx=5)
        self.vars["discharge_resistor_ohms"] = tk.StringVar(value=str(self.config.get("discharge_resistor_ohms", "250")))
        ttk.Entry(resistor_frame, textvariable=self.vars["discharge_resistor_ohms"], width=10).pack(side="left", padx=5)
        
        # Constant current charging settings
        row += 1
        ttk.Separator(current_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")
        row += 1
        
        # Constant current toggle and value
        cc_frame = ttk.Frame(current_frame)
        cc_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.vars["use_constant_current"] = tk.BooleanVar(value=self.config.get("use_constant_current", False))
        ttk.Checkbutton(cc_frame, text="Use Constant Current Charging", 
                       variable=self.vars["use_constant_current"]).pack(side="left", padx=5)
        
        ttk.Label(cc_frame, text="Current (A):").pack(side="left", padx=5)
        self.vars["constant_current_amps"] = tk.StringVar(value=str(self.config.get("constant_current_amps", "10.0")))
        ttk.Entry(cc_frame, textvariable=self.vars["constant_current_amps"], width=10).pack(side="left", padx=5)
        
        # Hardware Settings
        self.create_section("Hardware Settings", [
            ("OBD Port", "obd_port"),
            ("Relay Vendor ID", "relay_vendor_id"),
            ("Relay Product ID", "relay_product_id"),
            ("Monitoring Interval (s)", "monitoring_interval")
        ])

        # Add save button
        ttk.Button(self.scrollable_frame, text="Save Configuration", 
                  command=self.save_config).grid(row=100, column=0, columnspan=2, pady=20)

        # Pack scrollable components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_section(self, title, fields):
        section_frame = ttk.LabelFrame(self.scrollable_frame, text=title, padding="5")
        section_frame.grid(row=len(self.vars), column=0, columnspan=2, sticky="ew", pady=10, padx=5)
        
        for i, (label, key) in enumerate(fields):
            ttk.Label(section_frame, text=label).grid(row=i, column=0, padx=5, pady=2, sticky="w")
            var = tk.StringVar(value=str(self.config.get(key, "")))
            entry = ttk.Entry(section_frame, textvariable=var)
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            self.vars[key] = var

    def setup_history_tab(self):
        # Create frames for charge and discharge history
        charge_frame = ttk.LabelFrame(self.history_frame, text="Charge Cycles", padding="10")
        charge_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        discharge_frame = ttk.LabelFrame(self.history_frame, text="Discharge Cycles", padding="10")
        discharge_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create treeviews
        self.charge_tree = self.create_cycle_treeview(charge_frame)
        self.discharge_tree = self.create_cycle_treeview(discharge_frame)
        
        # Load initial data
        self.refresh_capacity_history()

    def create_cycle_treeview(self, parent):
        columns = ('timestamp', 'capacity', 'duration', 'start_v', 'end_v', 'start_i', 'end_i', 'mode')
        tree = ttk.Treeview(parent, columns=columns, show='headings')
        
        # Define headings
        tree.heading('timestamp', text='Time')
        tree.heading('capacity', text='Capacity (Ah)')
        tree.heading('duration', text='Duration (h)')
        tree.heading('start_v', text='Start V')
        tree.heading('end_v', text='End V')
        tree.heading('start_i', text='Start A')
        tree.heading('end_i', text='End A')
        tree.heading('mode', text='Mode')
        
        # Define columns
        tree.column('timestamp', width=150)
        tree.column('capacity', width=100)
        tree.column('duration', width=100)
        tree.column('start_v', width=80)
        tree.column('end_v', width=80)
        tree.column('start_i', width=80)
        tree.column('end_i', width=80)
        tree.column('mode', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return tree

    def refresh_capacity_history(self):
        try:
            with open(self.config['cycle_data_file'], 'r') as file:
                history = json.load(file)
                
            # Clear existing items
            self.charge_tree.delete(*self.charge_tree.get_children())
            self.discharge_tree.delete(*self.discharge_tree.get_children())
            
            # Add charge cycles
            for cycle in reversed(history.get('charge_cycles', [])):
                mode = "Constant Current" if cycle.get('constant_current', False) else "Normal"
                self.charge_tree.insert('', 'end', values=(
                    cycle['timestamp'],
                    f"{cycle['capacity_ah']:.2f}",
                    f"{cycle['duration_hours']:.2f}",
                    f"{cycle['start_voltage']:.1f}",
                    f"{cycle['end_voltage']:.1f}",
                    f"{cycle['start_current']:.1f}",
                    f"{cycle['end_current']:.1f}",
                    mode
                ))
            
            # Add discharge cycles
            for cycle in reversed(history.get('discharge_cycles', [])):
                mode = "Resistor" if cycle.get('using_resistor', False) else "Vehicle"
                self.discharge_tree.insert('', 'end', values=(
                    cycle['timestamp'],
                    f"{cycle['capacity_ah']:.2f}",
                    f"{cycle['duration_hours']:.2f}",
                    f"{cycle['start_voltage']:.1f}",
                    f"{cycle['end_voltage']:.1f}",
                    f"{cycle['start_current']:.1f}",
                    f"{cycle['end_current']:.1f}",
                    mode
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing capacity history: {e}")
        
        # Schedule next refresh
        self.root.after(30000, self.refresh_capacity_history)

    def save_config(self):
        try:
            # Convert values to appropriate types
            config = {}
            for key, var in self.vars.items():
                if isinstance(var, tk.BooleanVar):
                    config[key] = var.get()
                elif key in ['obd_port', 'relay_vendor_id', 'relay_product_id']:
                    config[key] = var.get()
                elif key in ['constant_current_amps']:
                    config[key] = float(var.get())
                else:
                    config[key] = int(var.get())
            
            with open('config.json', 'w') as file:
                json.dump(config, file, indent=4)
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values where required!")

def main():
    root = tk.Tk()
    app = ConfigGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 