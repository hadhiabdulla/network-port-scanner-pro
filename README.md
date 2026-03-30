# CyberScan Pro: Modern Network Port Scanner GUI

CyberScan Pro is a high-performance, multi-threaded TCP port scanner featuring a professional, cybersecurity-grade dark theme. Built with Python and Tkinter, it provides a seamless user experience for network discovery and security auditing.

## 🚀 Features

- **Modern UI**: Sleek dark-themed interface designed for cybersecurity professionals.
- **Multi-threaded Scanning**: High-speed scanning using Python's `threading` and `Semaphore` for concurrent execution.
- **Real-time Progress**: Visual progress bar and status updates during the scan.
- **Service Detection**: Automatically identifies common services (SSH, FTP, HTTP, etc.) based on well-known port numbers.
- **Advanced Controls**: Intuitive "Initiate" and "Stop" controls for managing scan sessions.
- **Cross-Platform**: Runs on Windows, Linux, and macOS.

## 🛠️ Prerequisites

- **Python 3.x**
- **Tkinter** (Usually included with Python; on Linux, install via `sudo apt-get install python3-tk`)

## 📥 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hadhiabdulla/network-port-scanner-pro.git
   cd network-port-scanner-pro
   ```

2. Run the application:
   ```bash
   python scanner_pro.py
   ```

## 🖥️ Usage

1. **Target Host**: Enter the IP address or hostname (e.g., `127.0.0.1` or `scanme.nmap.org`).
2. **Port Range**: Define the starting and ending ports (default is 1-1024).
3. **Initiate Scan**: Click the "INITIATE SCAN" button to start.
4. **Monitor Results**: View open ports and identified services in the real-time console.

## 🛡️ Legal Disclaimer

This tool is intended for **educational and ethical testing purposes only**. Scanning networks without explicit permission is illegal and unethical. Use it responsibly on your own machines or authorized targets.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
