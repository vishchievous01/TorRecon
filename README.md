# 🕵️‍♂️ TorRecon
### OPSEC-Aware Tor Reconnaissance Toolkit

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![Tor](https://img.shields.io/badge/Tor-Network-purple?logo=tor-project)
![Linux](https://img.shields.io/badge/Linux-Ubuntu%20%7C%20Kali-orange?logo=linux)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

**TorRecon** is an OPSEC-aware reconnaissance framework that routes reconnaissance traffic through the **Tor network**, applies **risk-based scan profiles**, and produces **structured JSON output**.

It is built to operate reliably in Tor-constrained environments, prioritizing correctness, transparency, and failure-tolerant design over raw scan speed.

---

## Features

- 🔒 **Explicit Tor Routing**
  - HTTP traffic via `requests[socks]`
  - System tools via `torsocks`
  - No proxychains or LD_PRELOAD hacks

- 🎯 **OPSEC Scan Profiles**
  - Risk-aware scan behavior
  - Tor-safe defaults
  - Easily extensible profiles

- 🧠 **Explain Mode**
  - Transparent reasoning for scan behavior
  - Clear visibility into OPSEC decisions

- 🔁 **Campaign Mode**
  - Multi-target reconnaissance
  - Optional Tor circuit rotation

- 📦 **Structured Output**
  - Automatic JSON results
  - SIEM / SOC friendly
  - Failures recorded, not hidden

- 🧰 **Tool Orchestration**
  - `nmap` (best-effort port scanning)
  - `subfinder` (subdomain enumeration)
  - Designed for extension (`httpx`, `nuclei`, etc.)

---

## Architecture
```bash
User
└── TorRecon (Python)
├── requests + SOCKS5h → Tor
├── torsocks → System tools
├── stem (ControlPort) → Tor circuit control
└── JSON Output
```

---

## Requirements

### System
- Linux (Ubuntu / Kali recommended)
- Tor
- torsocks
- nmap
- Python 3.12+

```bash
sudo apt update
sudo apt install -y tor torsocks nmap python3 python3-venv
```

**Tor Configuration**

- Edit Tor configuration:

`sudo nano /etc/tor/torrc`


- Ensure the following:

```bash 
SocksPort 127.0.0.1:9050
ControlPort 127.0.0.1:9051
CookieAuthentication 1
CookieAuthFileGroupReadable 1
```


- Restart Tor:

`sudo systemctl restart tor`


- Allow user access to the control cookie:

`sudo usermod -aG debian-tor $USER`


- Log out and log back in.

**Python Setup**

Create and activate a virtual environment:

```bash
python3 -m venv torrecon-venv
source torrecon-venv/bin/activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install requests[socks] stem
```

**Usage**

Activate the environment and run TorRecon:

```bash
source torrecon-venv/bin/activate
cd TorRecon
```

Explain Mode
```bash
python tor_recon.py scanme.nmap.org --ports --explain
```

Single Target – Port Scan
```bash
python tor_recon.py scanme.nmap.org --ports
```

Single Target – Subdomain Enumeration
```bash
python tor_recon.py hackerone.com --subs
```

Campaign Mode
```bash
python tor_recon.py --campaign scanme.nmap.org example.com --ports
```

**Output**

All runs generate JSON output in the `output/` directory.

```bash
{
  "profile": "stealth",
  "timestamp": "2026-01-21T16:20:42+00:00",
  "target": "scanme.nmap.org",
  "tor_exit_ip": "109.70.100.12",
  "results": [
    {
      "module": "ports",
      "command": "nmap -sT -Pn --max-rate 10 ...",
      "status": "attempted"
    }
  ]
}

```
**OPSEC Notes**

- Active scanning over Tor is best-effort

- Tor exits are rate-limited and frequently blocked

- Some failures are expected and intentionally logged

### 🛣️ Roadmap
- Passive DNS & TLS certificate harvesting

- HTTP header & favicon analysis

- Noise-budget based recon

- Tor exit reliability scoring

- HTML / Markdown reporting

- Tor-safe Nuclei integration

### ⚠️ Disclaimer
This tool is intended for educational use, research, and authorized security testing only.

**
Do not run it against systems without explicit permission.**
You are responsible for complying with local laws, provider terms,
and bug bounty program scopes.

---

## 📄 License

This project is licensed under the **MIT License**.

You are free to:
- Use, modify, and distribute the software
- Use it for commercial and non-commercial purposes

Under the condition that the original copyright notice
and this permission notice are included.

See the [LICENSE](LICENSE) file for full details.

---

## 🤝 Contributing

Contributions are welcome!

### How to contribute

1. Fork the repository
2. Create a new branch:
   ```bash
   git checkout -b feature/my-feature
   ```

### 👤 Author

Built by a SOC analyst / full-stack developer who enjoys combining
Python automation, Tor, and classic security tools
to create practical reconnaissance workflows.
