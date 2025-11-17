# iracing_gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
from typing import Dict, Callable

class IracingDataGUI:
    def __init__(self, root, callbacks: Dict[str, Callable]):
        self.root = root
        self.root.title("iRemoteEngineer - Data Provider")
        self.root.geometry("600x500")
        
        # Queue for thread-safe communication
        self.message_queue = queue.Queue()
        
        # Callbacks to be set from the main application
        self.callbacks = callbacks
        
        # Current server status
        self.server_running = False
        self.public_url = ""
        self.test_mode_running = False
        
        self.create_widgets()
        self.start_message_checker()

    def toggle_test_mode(self):
        if not self.test_mode_running:
            if self.callbacks["start_test_mode"]:
                self.test_mode_btn.config(text="Starting Test...", state=tk.DISABLED)
                self.log("Starting test mode...")
                # Start in a separate thread to avoid blocking GUI
                threading.Thread(target=self.start_test_mode_thread, daemon=True).start()
        else:
            if self.callbacks["stop_test_mode"]:
                self.callbacks["stop_test_mode"]()
                self.test_mode_running = False
                self.test_mode_btn.config(text="Start Test Mode")
                self.log("Test mode stopped")

    def start_test_mode_thread(self):
        try:
            result = self.callbacks["start_test_mode"]()
            self.message_queue.put(("test_mode_started", result))
        except Exception as e:
            self.message_queue.put(("error", str(e)))

    def _convert_url(self, url: str) -> str:
        """Convert the URL to a WebSocket URL"""
        if url.startswith("http://"):
            url = url.replace("http://", "ws://")
        elif url.startswith("https://"):
            url = url.replace("https://", "wss://")
        return url + "/ws"

    def test_mode_started(self, url):
        if url:
            self.test_mode_running = True
            self.test_mode_btn.config(text="Stop Test Mode", state=tk.NORMAL)
            self.log("Test mode started")

            self.public_url = self._convert_url(url)
            self.status_label.config(text="Test server running")
            
            # Update URL field
            self.url_text.config(state=tk.NORMAL)
            self.url_text.delete(1.0, tk.END)
            self.url_text.insert(tk.END, self.public_url)
            self.url_text.config(state=tk.DISABLED)
            self.copy_btn.config(state=tk.NORMAL)
            
            self.log(f"Test server started at: {url}")
        else:
            self.log(f"Failed to start a test server")

    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """Set callback functions from main application"""
        self.callbacks = callbacks
    
    def create_widgets(self):
        # Create a notebook with tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        control_frame = ttk.Frame(notebook)
        interval_frame = ttk.Frame(notebook)
        log_frame = ttk.Frame(notebook)
        settings_frame = ttk.Frame(notebook)  # New settings tab
        
        notebook.add(control_frame, text="Controls")
        notebook.add(interval_frame, text="Intervals")
        notebook.add(settings_frame, text="Settings")  # Add settings tab
        notebook.add(log_frame, text="Logs")
        
        # === Control Tab ===
        self.create_control_tab(control_frame)
        
        # === Intervals Tab ===
        self.create_intervals_tab(interval_frame)
        
        # === Settings Tab ===
        self.create_settings_tab(settings_frame)  # Create settings tab
        
        # === Log Tab ===
        self.create_log_tab(log_frame)
    
    def create_control_tab(self, parent):
        control_frame = ttk.LabelFrame(parent, text="Server Control")
        control_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Server controls
        server_buttons_frame = ttk.Frame(control_frame)
        server_buttons_frame.pack(pady=10)
        
        self.server_btn = ttk.Button(server_buttons_frame, text="Start Server", 
                                    command=self.toggle_server)
        self.server_btn.pack(side=tk.LEFT, padx=5)
        
        # Add test mode button
        self.test_mode_btn = ttk.Button(server_buttons_frame, text="Start Test Mode", 
                                    command=self.toggle_test_mode)
        self.test_mode_btn.pack(side=tk.LEFT, padx=5)
        
        # Server status
        status_frame = ttk.LabelFrame(control_frame, text="Server Status")
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="Server not running")
        self.status_label.pack(pady=5)
        
        # Public URL frame
        url_frame = ttk.LabelFrame(control_frame, text="Public URL")
        url_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.url_text = tk.Text(url_frame, height=2, width=50)
        self.url_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.url_text.config(state=tk.DISABLED)
        
        self.copy_btn = ttk.Button(url_frame, text="Copy", command=self.copy_url)
        self.copy_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        self.copy_btn.config(state=tk.DISABLED)
    
    def create_intervals_tab(self, parent):
        # Get current configuration
        self.interval_vars = {}
        self.interval_entries = {}
        
        # We'll populate this once we have the config
        self.intervals_frame = ttk.Frame(parent)
        self.intervals_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(self.intervals_frame, text="Loading configuration...").pack(pady=20)
    
    def create_settings_tab(self, parent):
        """Create the settings tab with authentication token field"""
        settings_frame = ttk.Frame(parent)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Advanced settings section
        advanced_frame = ttk.LabelFrame(settings_frame, text="Advanced Settings")
        advanced_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Port settings
        port_frame = ttk.Frame(advanced_frame)
        port_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(port_frame, text="Exposed Port:").pack(side=tk.LEFT, padx=5)
        
        # Variable to store the port
        self.port_var = tk.StringVar()
        
        # Load existing port if available
        if self.callbacks["get_port"]:
            current_port = self.callbacks["get_port"]()
            if current_port:
                self.port_var.set(str(current_port))
            else:
                self.port_var.set("8000")  # Default port
        else:
            self.port_var.set("8000")  # Default port
        
        # Port entry
        self.port_entry = ttk.Entry(port_frame, textvariable=self.port_var, width=10)
        self.port_entry.pack(side=tk.LEFT, padx=5)
        
        # Save port button
        self.save_port_btn = ttk.Button(
            port_frame, 
            text="Apply", 
            command=self.save_port
        )
        self.save_port_btn.pack(side=tk.LEFT, padx=5)
        
        # Add help text for port
        port_help_text = "Configure the port used for the server. Changes require server restart."
        ttk.Label(advanced_frame, text=port_help_text, wraplength=400, foreground="gray").pack(
            anchor=tk.W, padx=5, pady=5
        )
    
    def save_port(self):
        """Save the exposed port setting"""
        port_str = self.port_var.get().strip()
        
        if not port_str:
            messagebox.showwarning("Empty Port", "Please enter a port number.")
            return
            
        try:
            port = int(port_str)
            if port < 1024 or port > 65535:
                messagebox.showwarning("Invalid Port", "Port must be between 1024 and 65535.")
                return
                
            if self.callbacks["set_port"]:
                success = self.callbacks["set_port"](port)
                if success:
                    self.log(f"Port updated to {port}")
                    messagebox.showinfo("Success", f"Port updated to {port}. Restart server to apply changes.")
                else:
                    self.log("Failed to update port")
                    messagebox.showerror("Error", "Failed to update port.")
        except ValueError:
            messagebox.showwarning("Invalid Port", "Port must be a valid number.")

    def toggle_token_visibility(self):
        """Toggle between showing and hiding the authentication token"""
        if self.show_token.get():
            self.token_entry.config(show="")
        else:
            self.token_entry.config(show="*")
    
    def save_auth_token(self):
        """Save the authentication token"""
        token = self.token_var.get().strip()
        if not token:
            messagebox.showwarning("Empty Token", "Please enter an authentication token.")
            return
        
        if self.callbacks["set_auth_token"]:
            success = self.callbacks["set_auth_token"](token)
            if success:
                self.log("Authentication token saved successfully")
                messagebox.showinfo("Success", "Authentication token saved successfully.")
            else:
                self.log("Failed to save authentication token")
                messagebox.showerror("Error", "Failed to save authentication token.")
    
    def clear_auth_token(self):
        """Clear the authentication token"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the authentication token?"):
            self.token_var.set("")
            if self.callbacks["set_auth_token"]:
                self.callbacks["set_auth_token"]("")
                self.log("Authentication token cleared")
    
    def populate_intervals_tab(self):
        # Clear existing widgets
        for widget in self.intervals_frame.winfo_children():
            widget.destroy()
        
        # Get current configuration
        if self.callbacks["get_config"]:
            config = self.callbacks["get_config"]()
            
            # Main loop interval
            main_frame = ttk.LabelFrame(self.intervals_frame, text="Main Loop Interval")
            main_frame.pack(fill=tk.X, padx=10, pady=10)
            
            self.main_loop_var = tk.StringVar(value=str(config.loop_interval))
            ttk.Label(main_frame, text="Loop Interval (s):").pack(side=tk.LEFT, padx=5)
            main_entry = ttk.Entry(main_frame, textvariable=self.main_loop_var, width=10)
            main_entry.pack(side=tk.LEFT, padx=5)
            
            ttk.Button(main_frame, text="Update", 
                      command=lambda: self.update_interval("loop", self.main_loop_var.get())).pack(side=tk.LEFT, padx=5)
            
            # Task intervals
            tasks_frame = ttk.LabelFrame(self.intervals_frame, text="Task Intervals")
            tasks_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create grid for task intervals
            ttk.Label(tasks_frame, text="Task Name").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Label(tasks_frame, text="Interval (s)").grid(row=0, column=1, padx=5, pady=5)
            ttk.Label(tasks_frame, text="Action").grid(row=0, column=2, padx=5, pady=5)
            
            row = 1
            for task_name, interval in config.task_intervals.items():
                ttk.Label(tasks_frame, text=task_name).grid(row=row, column=0, padx=5, pady=2, sticky=tk.W)
                
                var = tk.StringVar(value=str(interval))
                self.interval_vars[task_name] = var
                
                entry = ttk.Entry(tasks_frame, textvariable=var, width=10)
                entry.grid(row=row, column=1, padx=5, pady=2)
                self.interval_entries[task_name] = entry
                
                update_btn = ttk.Button(tasks_frame, text="Update", 
                                       command=lambda tn=task_name, v=var: self.update_interval(tn, v.get()))
                update_btn.grid(row=row, column=2, padx=5, pady=2)
                
                row += 1
    
    def create_log_tab(self, parent):
        self.log_text = scrolledtext.ScrolledText(parent, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.log_text.config(state=tk.DISABLED)
        
        # Control buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Clear Log", command=self.clear_log).pack(side=tk.RIGHT)
    
    def toggle_server(self):
        if not self.server_running:
            if self.callbacks["start_server"]:
                self.server_btn.config(text="Starting...", state=tk.DISABLED)
                self.log("Starting server...")
                # Start in a separate thread to avoid blocking GUI
                threading.Thread(target=self.start_server_thread, daemon=True).start()
        else:
            if self.callbacks["stop_server"]:
                self.callbacks["stop_server"]()
                self.server_running = False
                self.server_btn.config(text="Start Server")
                self.status_label.config(text="Server not running")
                self.url_text.config(state=tk.NORMAL)
                self.url_text.delete(1.0, tk.END)
                self.url_text.config(state=tk.DISABLED)
                self.copy_btn.config(state=tk.DISABLED)
                self.log("Server stopped")
    
    def start_server_thread(self):
        try:
            result = self.callbacks["start_server"]()
            self.message_queue.put(("server_started", result))
        except Exception as e:
            self.message_queue.put(("error", str(e)))
    
    def update_interval(self, task_name, interval_str):
        try:
            interval = float(interval_str)
            if interval <= 0:
                self.log(f"Error: Interval must be positive for {task_name}")
                return
                
            if self.callbacks["update_interval"]:
                success = self.callbacks["update_interval"](task_name, interval)
                if success:
                    self.log(f"Updated {task_name} interval to {interval} seconds")
                else:
                    self.log(f"Failed to update {task_name} interval")
        except ValueError:
            self.log(f"Error: Invalid interval value for {task_name}")
    
    def copy_url(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.public_url)
        self.log("URL copied to clipboard")
    
    def server_started(self, url: str):
        if url:
            self.server_running = True
            self.public_url = self._convert_url(url)
            self.server_btn.config(text="Stop Server", state=tk.NORMAL)
            self.status_label.config(text="Server running")
            
            # Update URL field
            self.url_text.config(state=tk.NORMAL)
            self.url_text.delete(1.0, tk.END)
            self.url_text.insert(tk.END, self.public_url)
            self.url_text.config(state=tk.DISABLED)
            self.copy_btn.config(state=tk.NORMAL)
            
            self.log(f"Server started at: {url}")
        else:
            self.log(f"Failed to start a server")
    
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        full_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, full_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def start_message_checker(self):
        """Check for messages from other threads"""
        try:
            while not self.message_queue.empty():
                message_type, data = self.message_queue.get_nowait()
                
                if message_type == "server_started":
                    self.server_started(data)
                elif message_type == "test_mode_started":
                    self.test_mode_started(data)
                elif message_type == "error":
                    self.log(f"Error: {data}")
                    self.server_btn.config(text="Start Server", state=tk.NORMAL)
                    self.test_mode_btn.config(text="Start Test Mode", state=tk.NORMAL)
                elif message_type == "log":
                    self.log(data)
        except Exception as e:
            print(f"Error in message checker: {e}")
        
        # Schedule next check
        self.root.after(100, self.start_message_checker)
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()