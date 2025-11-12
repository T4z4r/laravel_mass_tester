import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import re
import json
import requests
from pathlib import Path
from urllib.parse import urljoin
import threading
import time

class LaravelMassTester:
    def __init__(self, root):
        self.root = root
        self.root.title("Laravel Mass Assignment Tester (Safe Mode)")
        self.root.geometry("900x700")
        self.session = requests.Session()
        self.online_mode = False
        self.setup_ui()

    def setup_ui(self):
        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Local Tab
        self.local_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.local_tab, text="Local Project Scan")

        # Online Tab
        self.online_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.online_tab, text="Online Endpoint Test (Manual)")

        self.setup_local_tab()
        self.setup_online_tab()

    def setup_local_tab(self):
        frame = self.local_tab

        # Path
        path_frame = tk.Frame(frame)
        path_frame.pack(pady=10, fill=tk.X, padx=20)

        self.local_path = tk.StringVar()
        tk.Label(path_frame, text="Laravel Project:").pack(side=tk.LEFT)
        tk.Entry(path_frame, textvariable=self.local_path, width=50).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        tk.Button(path_frame, text="Browse", command=self.browse_local).pack(side=tk.RIGHT)

        tk.Button(frame, text="Scan Models", command=self.scan_local, bg="#2196F3", fg="white").pack(pady=10)

        self.local_results = scrolledtext.ScrolledText(frame, height=25, state='disabled')
        self.local_results.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    def setup_online_tab(self):
        frame = self.online_tab

        # Warning
        tk.Label(frame, text="ONLINE TESTING IS MANUAL & REQUIRES CONFIRMATION", fg="red", font=("Helvetica", 10, "bold")).pack(pady=5)

        # URL
        url_frame = tk.Frame(frame)
        url_frame.pack(pady=5, fill=tk.X, padx=20)
        tk.Label(url_frame, text="Base URL:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar(value="http://localhost:8000/")
        tk.Entry(url_frame, textvariable=self.url_var, width=50).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Endpoint
        ep_frame = tk.Frame(frame)
        ep_frame.pack(pady=5, fill=tk.X, padx=20)
        tk.Label(ep_frame, text="Endpoint (e.g. api/users):").pack(side=tk.LEFT)
        self.endpoint_var = tk.StringVar()
        tk.Entry(ep_frame, textvariable=self.endpoint_var, width=40).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Method
        tk.Label(ep_frame, text="Method:").pack(side=tk.LEFT, padx=(10,0))
        self.method_var = tk.StringVar(value="POST")
        tk.OptionMenu(ep_frame, self.method_var, "POST", "PATCH", "PUT").pack(side=tk.LEFT)

        # Payload
        tk.Label(frame, text="Test Payload (JSON):").pack(anchor=tk.W, padx=20, pady=(10,0))
        self.payload_text = tk.Text(frame, height=8)
        self.payload_text.pack(pady=5, padx=20, fill=tk.X)
        self.payload_text.insert(tk.END, '{\n  "name": "Test User",\n  "email": "test@example.com",\n  "is_admin": 1\n}')

        # Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Send Single Test", command=self.send_test, bg="#FF5722", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear Log", command=self.clear_online_log).pack(side=tk.LEFT, padx=5)

        self.online_log = scrolledtext.ScrolledText(frame, height=15, state='disabled', bg="#333", fg="#0f0")
        self.online_log.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    def browse_local(self):
        folder = filedialog.askdirectory()
        if folder:
            self.local_path.set(folder)

    def log_local(self, text):
        self.local_results.config(state='normal')
        self.local_results.insert(tk.END, text + "\n")
        self.local_results.see(tk.END)
        self.local_results.config(state='disabled')

    def log_online(self, text, color="#0f0"):
        self.online_log.config(state='normal')
        self.online_log.insert(tk.END, text + "\n", color)
        self.online_log.tag_config(color, foreground=color)
        self.online_log.see(tk.END)
        self.online_log.config(state='disabled')

    def clear_online_log(self):
        self.online_log.config(state='normal')
        self.online_log.delete(1.0, tk.END)
        self.online_log.config(state='disabled')

    def scan_local(self):
        path = self.local_path.get().strip()
        if not path or not os.path.isdir(path):
            messagebox.showerror("Error", "Select a valid Laravel folder")
            return

        self.local_results.config(state='normal')
        self.local_results.delete(1.0, tk.END)
        self.local_results.config(state='disabled')

        self.log_local(f"Scanning: {path}")

        models_path = Path(path) / "app" / "Models"
        if not models_path.exists():
            models_path = Path(path) / "app"

        models = [f for f in models_path.rglob("*.php") if "Model" in f.name or "extends Model" in f.read_text(errors='ignore')]

        for model_file in models:
            self.analyze_model(model_file)

        self.log_local("\nScan complete. Use Online tab for safe endpoint testing.")

    def analyze_model(self, file_path):
        content = file_path.read_text(errors='ignore')
        name = file_path.stem

        fillable = re.search(r'\$fillable\s*=\s*\[([^\]]+)\]', content)
        guarded = re.search(r'\$guarded\s*=\s*\[([^\]]+)\]', content)

        if fillable:
            fields = re.findall(r"'([^']+)'|\"([^\"]+)\"", fillable.group(1))
            fields = [f for sub in fields for f in sub if f]
            self.log_local(f"SAFE {name}: $fillable = [{', '.join(fields[:5])}{'' if len(fields)<=5 else '...'}]")
        elif guarded and '*' in guarded.group(1):
            self.log_local(f"SAFE {name}: $guarded = ['*']")
        else:
            self.log_local(f"RISK {name}: NO MASS ASSIGNMENT PROTECTION!")

    def send_test(self):
        if not messagebox.askyesno("Confirm", "Send test payload to live server?\n\nThis will make a real HTTP request."):
            return

        url = urljoin(self.url_var.get().rstrip("/") + "/", self.endpoint_var.get())
        method = self.method_var.get()
        try:
            payload = json.loads(self.payload_text.get(1.0, tk.END))
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON: {e}")
            return

        def send():
            self.log_online(f"\n[{time.strftime('%H:%M:%S')}] → {method} {url}", "#fff")
            self.log_online(f"Payload: {json.dumps(payload, indent=2)}", "#aaa")

            try:
                response = self.session.request(method, url, json=payload, timeout=10)
                self.log_online(f"Response {response.status_code}: {response.text[:200]}", 
                                "#0f0" if response.status_code < 400 else "#f00")
            except Exception as e:
                self.log_online(f"Error: {e}", "#f00")

        threading.Thread(target=send, daemon=True).start()

# Run
if __name__ == "__main__":
    root = tk.Tk()
    app = LaravelMassTester(root)
    root.mainloop()