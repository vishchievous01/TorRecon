# 🕵️‍♂️ TorRecon – Tor-Rotating Recon Toolkit

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![Tor](https://img.shields.io/badge/Tor-Network-purple?logo=tor-project)
![Linux](https://img.shields.io/badge/Linux-Ubuntu-orange?logo=linux)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

---

**TorRecon** is a reconnaissance orchestration toolkit that routes all scanning traffic
through the **Tor network** and automatically rotates **Tor exit IPs** between actions.

It is designed for **OSINT**, **bug bounty reconnaissance**, and **stealthy scanning**
where IP-based rate limiting and blocking are a concern.


---

## ✨ Features

- 🔒 **Tor-routed reconnaissance**  
  All HTTP and TCP traffic is routed through Tor’s SOCKS5 proxy (`127.0.0.1:9050`).

- 🔄 **Automatic IP rotation**  
  Uses Tor’s control port and the `stem` library to request new Tor circuits (`NEWNYM`).

- 🎯 **Single-target and campaign modes**
  - Single target: port scans or subdomain enumeration
  - Campaign mode: multiple targets, rotating IP per target

- 🧰 **Powered by proven tools**
  - `nmap` – port and service detection
  - `subfinder` – subdomain enumeration
  - `httpx` – HTTP probing (via proxychains)

- 🖥️ **CLI-first and scriptable**  
  Easy to automate and extend.

---

## 🧠 How It Works

1. **Tor runs locally** with:
   - SOCKS proxy: `127.0.0.1:9050`
   - Control port: `127.0.0.1:9051`

2. **TorRecon**:
   - Connects to Tor’s control port using `stem.Controller`
   - Authenticates and sends `Signal.NEWNYM` to rotate circuits
   - Fetches the current Tor exit IP via `https://icanhazip.com`
   - Executes recon tools through `proxychains`

3. In **campaign mode**, this cycle repeats for each target so every target
   sees a different Tor exit IP.

---

## 🧱 Tech Stack

- Python 3.12+
- Tor
- stem
- proxychains
- nmap
- subfinder
- httpx

---

## Documentation

For full setup and usage details, see [docs.md](docs.md).

## 📦 Requirements

### System

- Ubuntu (tested in VirtualBox)
- Tor service
- proxychains
- nmap
- Go (for subfinder and httpx)

### Python Packages

- `stem`
- `requests`
- `fake-useragent`
- `PySocks`

---

## ⚙️ Setup

### 1️⃣ Tor Configuration

```bash
sudo apt update
sudo apt install tor
sudo nano /etc/tor/torrc
```
Add:
```bash
SocksPort 127.0.0.1:9050
ControlPort 127.0.0.1:9051
CookieAuthentication 1
```
Restart and verify:
```bash
sudo systemctl restart tor
sudo systemctl status tor
sudo ss -tlnp | grep -E '9050|9051'
```
### 2️⃣ proxychains Configuration
```bash
sudo apt install proxychains
sudo nano /etc/proxychains.conf
```
 Add:
```bash
[ProxyList]
socks5  127.0.0.1 9050
```
### 3️⃣ Recon Tools
```bash
sudo apt install nmap golang-go
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest

echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
source ~/.bashrc
```
Verify:
```bash
subfinder -version
httpx -version
nmap --version
```

### 4️⃣ Python Virtual Environment

```bash
python3 -m venv ~/tor-rotator-env
source ~/tor-rotator-env/bin/activate
pip install --upgrade pip
pip install stem requests fake-useragent pysocks
```
### 📁 Project Layout
```bash
TorRecon/
├── tor_recon.py
└── README.md
└── LICENSE
```
### 🚀 Usage
Activate the virtual environment:
```bash
cd ~/TorRecon
source ~/tor-rotator-env/bin/activate
```
Run TorRecon (root required for Tor control authentication):
```bash
sudo ~/tor-rotator-env/bin/python tor_recon.py ...
```

### 🎯 Examples
🔍 Single Target – Port Scan
```bash
sudo ~/tor-rotator-env/bin/python tor_recon.py 45.33.32.156 --ports
```

### 🌐 Single Target – Subdomain Enumeration
```bash
sudo ~/tor-rotator-env/bin/python tor_recon.py hackerone.com --subs > subs.txt
cat subs.txt | proxychains httpx -silent -title -status-code
```

### 📦 Campaign Mode – Multiple Targets
Ports
```bash
sudo ~/tor-rotator-env/bin/python tor_recon.py --campaign 45.33.32.156 93.184.216.34 --ports
```
Subdomains
```bash
sudo ~/tor-rotator-env/bin/python tor_recon.py --campaign hackerone.com bugcrowd.com --subs
```

### 🧪 Example Bug Bounty Workflow
```bash
sudo ~/tor-rotator-env/bin/python tor_recon.py \
  --campaign hackerone.com bugcrowd.com \
  --subs > subs_all.txt

cat subs_all.txt | proxychains httpx -silent -title -status-code > live_hosts.txt

```
### 🏗️ Design Choices
- **proxychains for routing:**
Keeps tools unchanged while routing traffic through Tor

- **Root execution:**
Avoids weakening Tor control authentication

- **Orchestrator, not a framework:**
TorRecon focuses on IP rotation and workflow control

### 🛣️ Roadmap
- Nuclei integration for vulnerability scanning

- JSON / CSV output modes

- Config-driven campaigns (YAML / JSON)

- Country-specific Tor exit nodes

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
