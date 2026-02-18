#!/usr/bin/env python3

import subprocess
import argparse
import time
import os
import json
from datetime import datetime, timezone

import requests
from stem.control import Controller
from stem import Signal


OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


SCAN_PROFILES = {
    "stealth": {
        "nmap": [
            "-sT",
            "-Pn",
            "--max-rate", "10",
            "--max-retries", "2",
            "--host-timeout", "3m",
            "--unprivileged"
        ],
        "rotate_ip": False,
        "description": "Low noise, Tor-safe scanning (best-effort)"
    }
}


proxies = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}


def rotate_ip():
    """Request a new Tor circuit"""
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
        time.sleep(5)
    except Exception:
        pass


def get_ip():
    """Get current Tor exit IP safely"""
    try:
        r = requests.get(
            "https://icanhazip.com",
            proxies=proxies,
            timeout=15
        )
        return r.text.strip()
    except Exception:
        return "unknown"


def run_cmd(cmd):
    ip = get_ip()
    print(f"[{ip}] $ {' '.join(cmd)}")

    result = subprocess.run(
        ["torsocks"] + cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )

    return result.stdout.strip()


parser = argparse.ArgumentParser(description="TorRecon - Tor-based Recon Toolkit")

parser.add_argument("target", nargs="?", help="Target domain or IP")
parser.add_argument("--ports", action="store_true", help="Run port scan module")
parser.add_argument("--subs", action="store_true", help="Run subdomain enumeration")
parser.add_argument("--campaign", nargs="+", help="Multiple targets (campaign mode)")

parser.add_argument(
    "--profile",
    choices=SCAN_PROFILES.keys(),
    default="stealth",
    help="OPSEC scan profile"
)

parser.add_argument(
    "--explain",
    action="store_true",
    help="Explain scan behavior and OPSEC decisions"
)

args = parser.parse_args()
profile = SCAN_PROFILES[args.profile]


if args.explain:
    print("\n[+] Explain Mode Enabled")
    print(f"Profile        : {args.profile}")
    print(f"Description    : {profile['description']}")
    print("Routing        : Tor (SOCKS5 + torsocks)")
    print("Scan Strategy  : Best-effort, OPSEC-aware")
    print("Note           : Active scans may fail due to Tor exit restrictions\n")


result = {
    "profile": args.profile,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "results": []
}


def save_results(name, data):
    filepath = os.path.join(OUTPUT_DIR, f"{name}_{args.profile}.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Results saved to {filepath}")


if args.campaign:
    print("=== CAMPAIGN MODE: Tor-based multi-target recon ===")

    for target in args.campaign:
        nmap_cmd = ["nmap"] + profile["nmap"] + ["-4", target]
        run_cmd(nmap_cmd)

        result["results"].append({
            "target": target,
            "module": "ports",
            "command": " ".join(nmap_cmd),
            "tor_exit_ip": get_ip(),
            "status": "attempted"
        })

        if profile["rotate_ip"]:
            rotate_ip()

    save_results("campaign", result)


elif args.ports and args.target:
    nmap_cmd = ["nmap"] + profile["nmap"] + ["-4", args.target]
    run_cmd(nmap_cmd)

    result["target"] = args.target
    result["tor_exit_ip"] = get_ip()
    result["results"].append({
        "module": "ports",
        "command": " ".join(nmap_cmd),
        "status": "attempted"
    })

    save_results(args.target, result)


elif args.subs and args.target:

    output = run_cmd(["subfinder", "-d", args.target, "-silent"])

    if not output:
        subdomains = []
    else:
        subdomains = output.splitlines()

    result["target"] = args.target
    result["tor_exit_ip"] = get_ip()

    result["results"].append({
        "module": "subdomains",
        "tool": "subfinder",
        "count": len(subdomains),
        "data": subdomains,
        "status": "completed" if subdomains else "no_results"
    })

    save_results(args.target, result)



else:
    print("Usage:")
    print("  python tor_recon.py <target> --ports [--profile stealth]")
    print("  python tor_recon.py <target> --subs")
    print("  python tor_recon.py --campaign t1 t2 t3")
