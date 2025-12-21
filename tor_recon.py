#!/usr/bin/env python3
import subprocess, argparse, time
from stem.control import Controller
from stem import Signal
import requests

proxies = {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}

def rotate_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
    time.sleep(5)

def get_ip():
    return requests.get('https://icanhazip.com', proxies=proxies).text.strip()

def run_cmd(cmd):
    ip = get_ip()
    print(f"[{ip}] $ {' '.join(cmd)}")
    subprocess.run(['proxychains'] + cmd)

parser = argparse.ArgumentParser(description='Tor Recon Toolkit')
parser.add_argument('target', nargs='?')  # Make optional for campaign
parser.add_argument('--ports', action='store_true')
parser.add_argument('--subs', action='store_true')
parser.add_argument('--campaign', nargs='+')  # NEW: Multi-target
args = parser.parse_args()

if args.campaign:
    print("=== CAMPAIGN MODE: Multi-target via rotating Tor IPs ===")
    for target in args.campaign:
        run_cmd(['nmap', '-sV', '-T4', '-4', target])
        rotate_ip()  # New IP per target!
elif args.ports and args.target:
    run_cmd(['nmap', '-sV', '-T4', '-4', args.target])
elif args.subs and args.target:
    run_cmd(['subfinder', '-d', args.target, '-silent'])
else:
    print("Usage: tor_recon.py <target> [--ports|--subs] or --campaign target1 target2")
