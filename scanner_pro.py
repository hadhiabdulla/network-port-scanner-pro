import socket
import threading
import time
import queue
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ---------------------------
# Modern Professional Colors
# ---------------------------
BG_MAIN = "#0f172a"      # Deep Navy/Slate
BG_PANEL = "#1e293b"     # Lighter Slate
ACCENT = "#38bdf8"       # Cyber Blue
TEXT_PRIMARY = "#f1f5f9" # Off-white
TEXT_SECONDARY = "#94a3b8"
SUCCESS = "#22c55e"
ERROR = "#ef4444"

COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS',
    3306: 'MySQL', 3389: 'RDP', 5900: 'VNC', 8080: 'HTTP-Alt'
}

class PortScanner:
    def __init__(self, target, start_port, end_port, timeout=0.5, max_workers=500):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.timeout = timeout
        self.max_workers = max_workers
        self._stop_event = threading.Event()
        self.total_ports = max(0, end_port - start_port + 1)
        self.scanned_count = 0
        self.open_ports = []
        self._lock = threading.Lock()
        self.result_queue = queue.Queue()

    def stop(self):
        self._stop_event.set()

    def _scan_port(self, port):
        if self._stop_event.is_set(): return
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            result = s.connect_ex((self.target, port))
            if result == 0:
                service = COMMON_PORTS.get(port, 'Unknown')
                with self._lock:
                    self.open_ports.append((port, service))
                self.result_queue.put(('open', port, service))
            s.close()
        except: pass
        finally:
            with self._lock:
                self.scanned_count += 1
            self.result_queue.put(('progress', self.scanned_count, self.total_ports))

    def run(self):
        sem = threading.Semaphore(self.max_workers)
        threads = []
        for port in range(self.start_port, self.end_port + 1):
            if self._stop_event.is_set(): break
            sem.acquire()
            t = threading.Thread(target=self._worker_wrapper, args=(sem, port), daemon=True)
            threads.append(t)
            t.start()
        for t in threads: t.join()
        self.result_queue.put(('done', None, None))

    def _worker_wrapper(self, sem, port):
        try: self._scan_port(port)
        finally: sem.release()

class ScannerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CyberScan Pro - Advanced Network Port Scanner")
        self.geometry("900x650")
        self.configure(bg=BG_MAIN)
        self._apply_styles()
        self._build_ui()
        self.scanner = None
        self.start_time = None

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=BG_MAIN)
        style.configure("Panel.TFrame", background=BG_PANEL)
        style.configure("TLabel", background=BG_MAIN, foreground=TEXT_PRIMARY, font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=BG_PANEL, foreground=TEXT_PRIMARY)
        style.configure("Header.TLabel", font=("Segoe UI Semibold", 18), foreground=ACCENT)
        style.configure("Accent.TButton", background=ACCENT, foreground=BG_MAIN, font=("Segoe UI Bold", 10), padding=10)
        style.configure("Stop.TButton", background=ERROR, foreground=TEXT_PRIMARY, font=("Segoe UI Bold", 10), padding=10)
        style.configure("Cyber.Horizontal.TProgressbar", thickness=15, troughcolor=BG_PANEL, background=ACCENT, bordercolor=BG_PANEL)

    def _build_ui(self):
        # Header
        header = ttk.Label(self, text="NETWORK PORT SCANNER PRO", style="Header.TLabel")
        header.pack(pady=20)

        # Main Layout
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=30, pady=10)

        # Settings Panel
        settings_frm = ttk.Frame(container, style="Panel.TFrame")
        settings_frm.pack(fill="x", pady=10)
        
        # Target
        ttk.Label(settings_frm, text="Target Host:", style="Panel.TLabel").grid(row=0, column=0, padx=15, pady=15, sticky="w")
        self.ent_target = tk.Entry(settings_frm, bg=BG_MAIN, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, border=0, font=("Consolas", 12), width=30)
        self.ent_target.grid(row=0, column=1, padx=5, pady=15)
        self.ent_target.insert(0, "127.0.0.1")

        # Range
        ttk.Label(settings_frm, text="Port Range:", style="Panel.TLabel").grid(row=0, column=2, padx=15, pady=15, sticky="w")
        self.ent_start = tk.Entry(settings_frm, bg=BG_MAIN, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, border=0, font=("Consolas", 12), width=8)
        self.ent_start.grid(row=0, column=3, padx=5, pady=15)
        self.ent_start.insert(0, "1")
        ttk.Label(settings_frm, text="-", style="Panel.TLabel").grid(row=0, column=4)
        self.ent_end = tk.Entry(settings_frm, bg=BG_MAIN, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, border=0, font=("Consolas", 12), width=8)
        self.ent_end.grid(row=0, column=5, padx=5, pady=15)
        self.ent_end.insert(0, "1024")

        # Control Buttons
        btn_frm = ttk.Frame(container)
        btn_frm.pack(fill="x", pady=10)
        self.btn_start = ttk.Button(btn_frm, text="INITIATE SCAN", style="Accent.TButton", command=self.start_scan)
        self.btn_start.pack(side="left", padx=5)
        self.btn_stop = ttk.Button(btn_frm, text="STOP SCAN", style="Stop.TButton", state="disabled", command=self.stop_scan)
        self.btn_stop.pack(side="left", padx=5)

        # Status & Progress
        status_frm = ttk.Frame(container)
        status_frm.pack(fill="x", pady=5)
        self.var_status = tk.StringVar(value="READY")
        ttk.Label(status_frm, textvariable=self.var_status, font=("Segoe UI Bold", 9)).pack(side="left")
        self.var_timer = tk.StringVar(value="0.00s")
        ttk.Label(status_frm, textvariable=self.var_timer, font=("Consolas", 10), foreground=ACCENT).pack(side="right")
        
        self.progress = ttk.Progressbar(container, style="Cyber.Horizontal.TProgressbar", mode="determinate")
        self.progress.pack(fill="x", pady=10)

        # Results Console
        console_frm = ttk.Frame(container, style="Panel.TFrame")
        console_frm.pack(fill="both", expand=True, pady=10)
        self.txt_results = tk.Text(console_frm, bg="#020617", fg=SUCCESS, font=("Consolas", 11), border=0, padx=15, pady=15)
        self.txt_results.pack(fill="both", expand=True, side="left")
        
        scroll = ttk.Scrollbar(console_frm, command=self.txt_results.yview)
        scroll.pack(side="right", fill="y")
        self.txt_results.config(yscrollcommand=scroll.set)

    def append_log(self, msg, color=None):
        self.txt_results.insert(tk.END, msg + "
")
        self.txt_results.see(tk.END)

    def start_scan(self):
        target = self.ent_target.get().strip()
        try:
            start_p = int(self.ent_start.get())
            end_p = int(self.ent_end.get())
        except:
            messagebox.showerror("Error", "Invalid port numbers")
            return

        self.txt_results.delete("1.0", tk.END)
        self.append_log(f"[*] Initializing scan on {target}...")
        self.append_log(f"[*] Range: {start_p} to {end_p}")
        
        self.scanner = PortScanner(target, start_p, end_p)
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.start_time = time.time()
        self.update_timer()
        
        threading.Thread(target=self.scanner.run, daemon=True).start()
        self.after(50, self.poll_results)

    def stop_scan(self):
        if self.scanner: self.scanner.stop()
        self.var_status.set("ABORTING...")

    def update_timer(self):
        if self.start_time:
            self.var_timer.set(f"{time.time() - self.start_time:.2f}s")
            self.after(100, self.update_timer)

    def poll_results(self):
        if not self.scanner: return
        try:
            while True:
                msg, a, b = self.scanner.result_queue.get_nowait()
                if msg == 'open':
                    self.append_log(f"[+] FOUND OPEN PORT: {a} ({b})")
                elif msg == 'progress':
                    self.progress.config(maximum=b, value=a)
                    self.var_status.set(f"SCANNING: {a}/{b}")
                elif msg == 'done':
                    self.append_log(f"
[!] SCAN COMPLETE. {len(self.scanner.open_ports)} open ports found.")
                    self.btn_start.config(state="normal")
                    self.btn_stop.config(state="disabled")
                    self.start_time = None
                    return
        except queue.Empty:
            self.after(50, self.poll_results)

if __name__ == "__main__":
    app = ScannerGUI()
    app.mainloop()
