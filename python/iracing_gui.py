# iracing_gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import time
from typing import Dict, Callable

class IracingDataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("iRacing Data Dashboard Control")
        self.root.geometry("800x600")
        
        # Queue for thread-safe communication
        self.message_queue = queue.Queue()
        
        # Callbacks to be set from the main application
        self.callbacks = {
            "start_server": None,
            "stop_server": None,
            "update_interval": None,
            "get_config": None
        }
        
        # Current server status
        self.server_running = False
        self.public_url = ""
        
        self.create_widgets()
        self.start_message_checker()
    
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
        
        notebook.add(control_frame, text="Controls")
        notebook.add(interval_frame, text="Intervals")
        notebook.add(log_frame, text="Logs")
        
        # === Control Tab ===
        self.create_control_tab(control_frame)
        
        # === Intervals Tab ===
        self.create_intervals_tab(interval_frame)
        
        # === Log Tab ===
        self.create_log_tab(log_frame)
    
    def create_control_tab(self, parent):
        control_frame = ttk.LabelFrame(parent, text="Server Control")
        control_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Server controls
        self.server_btn = ttk.Button(control_frame, text="Start Server", 
                                     command=self.toggle_server)
        self.server_btn.pack(pady=10)
        
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
    
    def server_started(self, url):
        self.server_running = True
        self.public_url = url
        self.server_btn.config(text="Stop Server", state=tk.NORMAL)
        self.status_label.config(text="Server running")
        
        # Update URL field
        self.url_text.config(state=tk.NORMAL)
        self.url_text.delete(1.0, tk.END)
        self.url_text.insert(tk.END, url)
        self.url_text.config(state=tk.DISABLED)
        self.copy_btn.config(state=tk.NORMAL)
        
        self.log(f"Server started at: {url}")
    
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
                elif message_type == "error":
                    self.log(f"Error: {data}")
                    self.server_btn.config(text="Start Server", state=tk.NORMAL)
                elif message_type == "log":
                    self.log(data)
        except Exception as e:
            print(f"Error in message checker: {e}")
        
        # Schedule next check
        self.root.after(100, self.start_message_checker)
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()