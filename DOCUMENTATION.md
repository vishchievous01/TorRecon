🕵️ TorRecon Documentation

---

1. Overview

TorRecon is a command-line reconnaissance framework that orchestrates common recon tools through the Tor network, with an emphasis on OPSEC, explainability, and structured output.

Unlike traditional recon scripts, TorRecon is designed to explicitly control traffic routing, treat active scans as best-effort, and remain stable even when tools fail under Tor conditions.

Designed for

OSINT & reconnaissance research

Bug bounty reconnaissance (authorized scope only)

Learning Tor, SOCKS routing, and OPSEC trade-offs

SOC / blue-team understanding of Tor-based activity

Lab environments and controlled testing

2. Core Design Principles

Explicit Tor routing (no hidden LD hacks)

OPSEC-aware scan profiles

Best-effort active scanning

Graceful failure handling

Explainable behavior

Structured JSON output

TorRecon prioritizes understanding and control over raw scan speed.

3. Architecture
3.1 Components
Tor

Runs locally and provides:

SOCKS5 proxy → 127.0.0.1:9050

Control port → 127.0.0.1:9051

Circuit rotation via NEWNYM

Python (TorRecon)

Controls Tor via Stem

Routes HTTP traffic via requests + SOCKS

Executes system tools via torsocks

Manages OPSEC profiles

Generates structured JSON output

System Tools

nmap → best-effort port scanning

subfinder → subdomain enumeration

(Designed to be extended with httpx, nuclei, etc.)

3.2 Why NOT proxychains?

Earlier versions used proxychains.
TorRecon intentionally removed it.

Why?

proxychains	torsocks
LD_PRELOAD hack	Tor-aware wrapper
Opaque DNS behavior	Correct DNS handling
Hard to debug	Explicit routing
Breaks in containers	Stable
Tool-dependent	Predictable

Design rule:
The code that makes decisions must control the network path.

TorRecon now follows this rule strictly.

4. Installation
4.1 System Requirements

Ubuntu / Kali (tested on Ubuntu 24.04, Kali Linux)

Tor installed and running

### Single target recon

---

Internet access (Tor-routed)

Install system packages:

sudo apt update
sudo apt install -y tor torsocks nmap python3 python3-venv

4.2 Tor Configuration

Edit Tor config:

sudo nano /etc/tor/torrc


Ensure these lines exist:

SocksPort 127.0.0.1:9050
ControlPort 127.0.0.1:9051
CookieAuthentication 1
CookieAuthFileGroupReadable 1


Restart Tor:

sudo systemctl restart tor
sudo systemctl status tor


Verify ports:

ss -tlnp | grep -E '9050|9051'

4.3 Permissions (Important)

Allow your user to access the Tor control cookie:

sudo usermod -aG debian-tor $USER


Log out and log back in.

This avoids running TorRecon as root.

4.4 Python Environment (Required)

Create and activate a virtual environment:

cd ~
python3 -m venv torrecon-venv
source torrecon-venv/bin/activate


Install Python dependencies:

pip install --upgrade pip
pip install requests[socks] stem

4.5 Optional Recon Tools

Install subfinder (optional):

go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
source ~/.bashrc

5. Usage

Always activate the virtual environment:

source ~/torrecon-venv/bin/activate
cd ~/TorRecon

5.1 Explain Mode (Recommended)
python tor_recon.py scanme.nmap.org --ports --explain


Explain mode prints:

Selected OPSEC profile

Routing behavior

Scan limitations over Tor

Why failures may occur

This is intentional transparency, not an error.

5.2 Single Target – Port Scan
python tor_recon.py scanme.nmap.org --ports


Behavior:

Traffic routed via Tor

OPSEC-safe Nmap flags

Best-effort scan

Results saved to JSON

5.3 Single Target – Subdomain Enumeration
python tor_recon.py hackerone.com --subs

5.4 Campaign Mode (Multiple Targets)
python tor_recon.py --campaign scanme.nmap.org example.com --ports


Loops through targets

Uses same OPSEC profile

Optionally rotates circuits (profile-dependent)

6. Output Format

TorRecon always produces structured JSON output.

Example:

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


Key points:

Failures are recorded, not hidden

Active scans are attempted, not assumed successful

Output is SIEM-ready

7. OPSEC Profiles

TorRecon uses OPSEC-aware scan profiles.

Stealth (default)

Low rate

TCP connect scan

No aggressive timing

Designed for Tor stability

Profiles define:

Tool behavior

Scan intensity

Circuit rotation policy

8. Known Limitations (Important)
Port scanning over Tor

Tor exits are rate-limited

CDNs (Cloudflare, Google) often block Tor

Nmap’s socket engine may crash under Tor

This is expected behavior.

TorRecon treats active scanning as best-effort intelligence, not guaranteed results.

9. Design Philosophy (Why TorRecon Exists)

TorRecon is not a “faster Nmap”.

It is a learning-focused, OPSEC-aware recon framework designed to expose the realities of Tor-based reconnaissance.

This includes:

Latency

Blocking

Failure

Trade-offs

All of which are logged, explained, and preserved.

10. Future Enhancements

Planned / suggested ideas:

Passive DNS & TLS certificate harvesting

HTTP header & favicon analysis

Noise-budget based recon

Tor exit reliability scoring

HTML / Markdown reports

Nuclei (Tor-safe templates only)

11. Legal & Ethical Use

TorRecon is intended only for:

Lab environments

Authorized bug bounty programs

Explicitly permitted testing

You must:

Respect program rules

Respect Tor network usage

Avoid high-volume scanning

Follow local laws

12. Author Notes

TorRecon was built as a hands-on learning project to understand:

Tor routing and control

OPSEC trade-offs

Recon tooling design

Failure-tolerant security automation

It intentionally favors clarity and correctness over speed.
