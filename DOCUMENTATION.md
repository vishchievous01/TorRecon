# TorRecon Documentation

TorRecon is an automated reconnaissance toolkit focused on OSINT and enumeration while preserving user privacy via the Tor network.

---

## Features

- Automated target enumeration (domains, subdomains, IPs).
- Integration with popular OSINT and reconnaissance tools.
- Tor-based routing to help anonymize requests.
- Structured output for further analysis and reporting.

---

## Architecture

| Component     | Description                                      |
|--------------|--------------------------------------------------|
| CLI Module   | Entry point for running scans and subcommands.   |
| Core Engine  | Orchestrates recon workflows and tool chaining.  |
| Output Layer | Handles saving, formatting, and exporting data.  |

---

## Prerequisites

- Python 3.10 or later.
- Git.
- Tor service installed and running on the host.
- Recommended OS: Linux (tested on Ubuntu/Kali).

---

## Installation
```bash
git clone https://github.com/<your-username>/TorRecon.git
cd TorRecon
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Configuration

Create and adjust a configuration file before running scans:

```bash
cp config.example.yaml config.yaml
```

Key options:

- `targets`: List of domain or IP targets.
- `tor_proxy`: Address and port of the Tor SOCKS proxy.
- `modules`: Modules to enable or disable for each run.

---

## Usage

Basic usage:

```bash
python main.py --target example.com
```

Common options:

- `--target`: Single target (domain or IP).
- `--targets-file`: File containing a newline-separated target list.
- `--output`: Directory where results are stored.
- `--no-tor`: Run without Tor routing (for local lab/testing only).

---

## Example workflows

### Single target recon

```bash
python main.py --target example.com --output results/example
```

### Batch recon from file

```bash
python main.py --targets-file targets.txt --output results/batch
```

---

## Output format

TorRecon produces structured output under the chosen output directory:

- `summary.json`: High-level findings.
- `raw/`: Raw tool outputs.
- `logs/`: Runtime logs for troubleshooting.

---

## Troubleshooting

- Ensure Tor service is running:
```bash
systemctl status tor
```
- If requests fail, verify the `tor_proxy` configuration.
- Run with verbose logging:

```bash
python main.py --target example.com --verbose
```

---

## Roadmap

- Add more OSINT integrations.
- Enhance reporting formats (HTML/Markdown exports).
- Improve module-level configuration granularity.

---

## Contributing

Contributions are welcome. To propose changes:

1. Fork the repository.
2. Create a feature branch.
3. Open a pull request with a clear description and example usage.

---

## License

This project is licensed under the terms described in [`LICENSE`](LICENSE).

