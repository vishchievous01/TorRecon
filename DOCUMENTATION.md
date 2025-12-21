TorRecon Documentation
1. Overview
TorRecon is a command-line reconnaissance toolkit that runs common recon tools (nmap, subfinder, httpx) through the Tor network and rotates Tor exit IPs between actions.
It is designed for:

OSINT and bug bounty reconnaissance

Stealthy scanning where IP-based rate limiting and blocking are a concern

Lab experiments with Tor, proxychains, and automation

Core ideas:

Route traffic through Tor’s SOCKS5 proxy (127.0.0.1:9050)

Control Tor via the control port (127.0.0.1:9051) using stem

Send NEWNYM to rotate circuits and exit IPs

Orchestrate external tools (nmap, subfinder, httpx) via proxychains

2. Architecture
2.1 Components
Tor
Runs locally and provides:

SOCKS5 proxy on 127.0.0.1:9050

Control port on 127.0.0.1:9051

proxychains
Wraps CLI tools and transparently routes their traffic through the Tor SOCKS proxy.

Python / TorRecon script

Uses stem to talk to the Tor control port and send NEWNYM.

Uses requests with SOCKS proxy to fetch the current Tor IP.

Uses subprocess to launch tools under proxychains.

Recon tools

nmap for port and service discovery.

subfinder for subdomain enumeration.

httpx for HTTP probing of hosts/subdomains.

2.2 Data Flow
User calls tor_recon.py with arguments.

Script optionally rotates Tor IP using stem → Signal.NEWNYM.

Script calls https://icanhazip.com through SOCKS proxy to log the active Tor IP.

Script executes the recon command via proxychains, so traffic goes Tor → Internet.

Results are printed to stdout and can be redirected to files for later analysis.​

3. Installation
3.1 System Prerequisites
Ubuntu (tested on 24.04 in a VirtualBox VM)

sudo privileges

Install base packages:

bash
sudo apt update
sudo apt install -y tor proxychains nmap golang-go python3 python3-venv
3.2 Tor Configuration
Edit Tor config:

bash
sudo nano /etc/tor/torrc
Ensure the following lines exist (add if missing):

text
SocksPort 127.0.0.1:9050
ControlPort 127.0.0.1:9051
CookieAuthentication 1
Restart Tor and verify:

bash
sudo systemctl restart tor
sudo systemctl status tor
sudo ss -tlnp | grep -E '9050|9051'
You should see Tor listening on 127.0.0.1:9050 (SOCKS) and 127.0.0.1:9051 (control).

3.3 proxychains Configuration
bash
sudo nano /etc/proxychains.conf
At the bottom under [ProxyList], set:

text
[ProxyList]
socks5  127.0.0.1 9050
Now any proxychains <command> is routed through Tor.

3.4 Recon Tools (subfinder, httpx, nmap)
nmap is already installed above. Install Go-based tools:

bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
Add Go bin directory to PATH:

bash
echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
source ~/.bashrc
Check:

bash
subfinder -version
httpx -version
nmap --version
3.5 Python Environment
Create a dedicated virtual environment for TorRecon:

bash
cd ~
python3 -m venv tor-rotator-env
source tor-rotator-env/bin/activate
Install dependencies:

bash
pip install --upgrade pip
pip install stem requests fake-useragent pysocks
Create project folder and place the script:

bash
mkdir -p ~/TorRecon
cd ~/TorRecon
# Save tor_recon.py here
chmod +x tor_recon.py
4. Script Interface
4.1 Command-line Arguments
tor_recon.py supports:

target (positional, optional in campaign mode)

--ports
Run a port scan using nmap -sV -T4 -4 <target>.

--subs
Run subdomain enumeration using subfinder -d <target> -silent.

--campaign <t1> <t2> ...
Run the chosen mode (--ports / --subs) for multiple targets, rotating Tor IP between targets.​

The script expects Tor and proxychains to be correctly configured and uses the Tor control port via stem.

5. Usage
5.1 General Notes
Run from the project directory:

bash
cd ~/TorRecon
Activate the virtualenv when working interactively:

bash
source ~/tor-rotator-env/bin/activate
Use the venv Python with sudo for operations that talk to the Tor control port (because of cookie permissions):

bash
sudo ~/tor-rotator-env/bin/python tor_recon.py ...
5.2 Single-Target Port Scan
Example: scan 45.33.32.156 (scanme.nmap.org IP) through Tor:

bash
sudo ~/tor-rotator-env/bin/python tor_recon.py 45.33.32.156 --ports
Behavior:

Fetches current Tor IP from https://icanhazip.com over SOCKS.

Logs [TorIP] $ nmap -sV -T4 -4 45.33.32.156.

Runs nmap via proxychains, so all traffic is Tor-routed.​

5.3 Single-Target Subdomain Enumeration
Example: enumerate subdomains for hackerone.com via Tor:

bash
sudo ~/tor-rotator-env/bin/python tor_recon.py hackerone.com --subs > subs.txt
Follow-up HTTP probing:

bash
cat subs.txt | proxychains httpx -silent -title -status-code > live_hosts.txt
subs.txt = discovered subdomains

live_hosts.txt = responding hosts with status codes and titles

5.4 Campaign Mode – Port Scans
Run port scans against multiple IPs/domains, rotating Tor IP between each:

bash
sudo ~/tor-rotator-env/bin/python tor_recon.py --campaign 45.33.32.156 93.184.216.34 --ports
For each target:

Get current Tor IP.

Run nmap -sV -T4 -4 <target> via proxychains.

Rotate IP for the next target.​

5.5 Campaign Mode – Subdomain Enumeration
Run subdomain enumeration for multiple domains:

bash
sudo ~/tor-rotator-env/bin/python tor_recon.py --campaign hackerone.com bugcrowd.com --subs > subs_all.txt
Now probe all these subdomains:

bash
cat subs_all.txt | proxychains httpx -silent -title -status-code > live_hosts.txt
5.6 Example Bug Bounty Workflow
Subdomains for multiple programs:

bash
sudo ~/tor-rotator-env/bin/python tor_recon.py --campaign hackerone.com bugcrowd.com --subs > subs_all.txt
HTTP probe subdomains:

bash
cat subs_all.txt | proxychains httpx -silent -title -status-code > live_hosts.txt
Manually review live_hosts.txt or feed it to other tools.

6. Internal Functions
Below is a conceptual breakdown of key functions in tor_recon.py (names may vary slightly depending on your implementation).

6.1 proxies
python
proxies = {
    'http': 'socks5://127.0.0.1:9050',
    'https': 'socks5://127.0.0.1:9050',
}
Used by requests to send traffic through Tor.

6.2 rotate_ip()
python
from stem.control import Controller
from stem import Signal
import time

def rotate_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
    time.sleep(5)
Connects to control port (9051).

Authenticates using Tor’s cookie (requires root).

Sends Signal.NEWNYM to get a new circuit.

Sleeps to let Tor establish a new route.

6.3 get_ip()
python
import requests

def get_ip():
    resp = requests.get('https://icanhazip.com', proxies=proxies, timeout=10)
    return resp.text.strip()
Returns the current Tor exit IP as seen by external services.​

6.4 run_cmd(cmd)
python
import subprocess

def run_cmd(cmd):
    ip = get_ip()
    print(f"[{ip}] $ {' '.join(cmd)}")
    subprocess.run(['proxychains'] + cmd)
Logs the Tor IP and the command being run.

Executes the command through proxychains, ensuring Tor routing.

6.5 Argument Parsing
python
import argparse

parser = argparse.ArgumentParser(description='Tor Recon Toolkit')
parser.add_argument('target', nargs='?')
parser.add_argument('--ports', action='store_true')
parser.add_argument('--subs', action='store_true')
parser.add_argument('--campaign', nargs='+')
args = parser.parse_args()
Logic (simplified):

If --campaign + --ports: loop over targets → rotate_ip() → run_cmd(['nmap', ...])

If --campaign + --subs: loop over targets → run_cmd(['subfinder', ...])

If --ports + target: single nmap run

If --subs + target: single subfinder run

7. Design Considerations
7.1 Why proxychains?
Most tools (nmap, subfinder, httpx) are not Tor-aware.

proxychains lets them run unmodified while routing through Tor SOCKS.

7.2 Why use root for the Python script?
Tor’s control auth cookie is root-owned by default.

Running the controller script as root allows reading /run/tor/control.authcookie without weakening Tor’s authentication configuration.

This is acceptable for a lab / VM setting; for production, a dedicated user/tor config could be created.

7.3 Limitations
Tor adds latency; scans are much slower than direct scans.

Nmap through Tor should be limited to low-intensity scans; no aggressive flooding.

Some targets or CDNs may block Tor exit nodes.

8. Future Enhancements
Ideas for extending TorRecon:

Nuclei integration:
Route nuclei scans through Tor for stealthy vulnerability detection.

Output formats:
JSON/CSV outputs from Nmap parsing or httpx to plug directly into analysis pipelines or SIEMs.

Config files:
YAML/JSON-based campaigns with lists of targets, modes, and tools.

Exit node preferences:
Use Tor ExitNodes / StrictNodes to favor specific countries or regions for exit IPs.

9. Legal and Ethical Use
TorRecon is intended for:

Lab environments

Personal learning and research

Authorized testing under clear scope (e.g., bug bounty programs, internal pentests)

You must:

Only scan and enumerate assets you have explicit permission to test.

Follow local laws and program rules.

Respect Tor network usage and not abuse it for high-volume scanning.

10. Contact / Author Notes
The project was created by a SOC analyst and full-stack developer as a practical experiment in:

Tor-based IP rotation

Stealthy reconnaissance workflows

Combining Python automation with standard security tools and proxychains.