# ratelimiting-detector

A lightweight CLI tool to profile HTTP rate limiting behavior on a target domain — measures request threshold, ban duration, and response patterns.

> [!WARNING]
> **For authorized testing only.** Only use this tool on domains you own or have explicit permission to test.

## ⚠️ Warnings

- **Legal:** Running this tool against domains you don't own or have explicit written permission to test may violate computer crime laws in your jurisdiction (e.g. UU ITE di Indonesia). Always get authorization first.
- **WAF Triggering:** Burst requests may trigger Web Application Firewall (WAF) rules, which can flag your IP as malicious — separate from the rate limiter itself.
- **IP Ban:** Your IP may get banned temporarily or **permanently** depending on the target server's security policy. Some systems escalate ban duration on repeated offenses (progressive banning).
- **CDN-level blocks:** If the target uses Cloudflare, AWS Shield, or similar CDN/DDoS protection, your IP may get blocked at the network edge level — harder to recover from than a simple rate limit ban.
- **No anonymity guarantee:** Even with custom User-Agent headers, your real IP is still exposed unless routed through a proxy. Use responsibly in controlled environments.

---

## Features

- Burst-based rate limit threshold detection
- Automatic ban duration measurement with exponential backoff
- Per-request tracking (sequence number, status, latency, timestamps)
- Chronological result analysis via `sent_at` sorting

---

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

---

## Installation

```bash
git clone https://github.com/yourname/ratelimiting-detector
cd ratelimiting-detector
uv sync
```

---

## Usage

```bash
uv run app/main.py -d example.com
uv run app/main.py -d https://example.com --timeout 5.0
```

### Arguments

| Flag | Description | Default |
|------|-------------|---------|
| `-d`, `--domain` | Target domain (with or without scheme) | required |
| `--timeout` | Request timeout in seconds | `3.0` |

---

## Example Output

```
[C] Starting burst attack...
[C] Batch done, total sent: 5
[C] Batch done, total sent: 10
[C] Batch done, total sent: 15

========================================
  Requests before rate limit : 15
  First non-200 status       : 429
  First non-200 at seq       : 15
  Total requests fired       : 20
========================================

[C] Waiting for release since 2026-05-08 21:52:43
[-] Still banned... (next check in 3.0s)
  Ban duration: 8.39s
```

---

## Configuration

Edit `ScanConfig` defaults in `scanner.py`:

```python
@dataclass
class ScanConfig:
    domain: str   = None
    timeout: float  = 3.0
    burst_size: int = 5     # requests per batch
```

Lower `burst_size` (e.g. `1`) for more precise threshold detection after an initial estimate.

---

## Project Structure

```
.
├── app/
│   ├── main.py       # CLI entrypoint & argument parsing
│   └── scanner.py    # Detector, ScanConfig, RequestResult
├── pyproject.toml
└── uv.lock
```

---

## License

See [LICENSE](./LICENSE).
