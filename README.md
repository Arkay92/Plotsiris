# ⬡ PLOTSIRIS — Open Source Intelligence & Reconnaissance Integrated System

An open-source, real-time global **OSINT (Open Source Intelligence) and situational reconnaissance command center** written entirely in **Python, Plotly, and Dash**.

Plotsiris is a complete Python reimplementation of [carbon-evolution/osiris](https://github.com/carbon-evolution/osiris), migrating the WebGL/React/Next.js architecture into a unified, high-performance Python data stack powered by **Plotly MapLibre / Mapbox**, **Dash Bootstrap Components**, **NetworkX**, and **Google Gemini 2.5 Flash**.

---

## 📖 Overview

Plotsiris transforms your workstation or cloud container into a **military-grade situational awareness command center**. By fusing **40+ global open intelligence streams** into a single GPU-accelerated cartographic display, it delivers near real-time operational visibility across:

- ✈️ **Live Aviation**: Civil, commercial, transport, and military reconnaissance ADS-B state vectors (OpenSky / airplanes.live) with route lines, altitude, speed, and heading indicators.
- 🚢 **Live Maritime**: AIS vessel tracking (cargo, VLCC supertankers, container liners, naval task forces, destroyers), strategic maritime chokepoints (Suez, Bab el-Mandeb, Hormuz, Malacca, Panama, Gibraltar, Bosporus), and transoceanic submarine fiber-optic cables.
- 📹 **Worldwide Surveillance**: Government highway cameras and open surveillance feeds (Taiwan THB, Caltrans California, London TfL, Singapore LTA, Ireland TII, Germany Autobahn) with a live camera viewer modal.
- 🌍 **Natural Hazards & Climate**: Real-time seismic monitoring (USGS 24h earthquakes), thermal wildfire hotspots (NASA FIRMS / MODIS), and severe tropical storms / cyclone tracks.
- ⚡ **Kinetic Conflicts & Geopolitics**: Contested war frontlines (Ukraine Pokrovsk/Kursk sectors, Red Sea anti-shipping zone, Sudan Darfur, Myanmar, Sahel) and global nuclear power facilities / enrichment sites.
- 🛡️ **Cyber Threat Intelligence**: CISA Known Exploited Vulnerabilities (KEV) live catalog, Tor exit nodes, Spamhaus DROP blocks, and MITRE ATT&CK enterprise threat actors (Volt Typhoon, APT28, Lazarus, LockBit, Scattered Spider).
- 🛰️ **Space Domain & Space Weather**: NOAA SWPC Planetary Kp index, solar flare telemetry, and satellite orbits (ISS, Sentinel-1 SAR radar, USA-245 Key Hole optical recon, Starlink).
- 📊 **Financial Markets & Geopolitics**: Defense primes (Lockheed Martin, RTX, Northrop Grumman, General Dynamics, Palantir, Boeing), energy (Brent, WTI), commodities (Gold, Silver, Gas), crypto (BTC, ETH), and sovereign risk ratings.
- 🔍 **20-Tool OSINT Reconnaissance Suite**: Full in-dashboard reconnaissance suite with instant **Verdict-Coloured Map Pinning** (red = malicious, amber = warning, cyan = clean).
- 🧠 **AI Intelligence Analyst**: Built-in intelligence analyst powered by **Gemini 2.5 Flash** (or offline tactical heuristic engine) with a one-click **Operational SITREP Briefing Generator**.
- 🔗 **Force-Directed Entity Intelligence Graph**: Interactive network graph connecting threat groups, malware vectors, CVEs, target sectors, and command-and-control servers.

---

## 🛠️ The 20-Tool OSINT Reconnaissance Toolkit

Plotsiris includes a full-featured reconnaissance suite built directly into the UI:

| # | Tool | Engine / Source | Capabilities |
|---|---|---|---|
| 1 | **DNS ENUM** | Google DNS-over-HTTPS (DoH) | Resolves A, AAAA, MX, NS, TXT, CNAME records |
| 2 | **WHOIS / RDAP** | ARIN / ICANN RDAP | Registration lifecycle, entities & OFAC sanctions check |
| 3 | **PORT SCAN** | Non-blocking TCP sockets | Rapid audit on 18 critical administrative/service ports |
| 4 | **SHODAN IoT** | Shodan InternetDB | Open ports, vulnerabilities (CVEs), tags, and CPEs |
| 5 | **BGP / ASN** | RIPEstat / PeeringDB | Announcing BGP prefix, ASN, and routing block details |
| 6 | **HTTP HEADERS** | Requests / Header inspect | Security audit: HSTS, CSP, X-Frame-Options, CORS |
| 7 | **SSL / TLS** | Python SSL socket wrap | Certificate issuer, expiry, SANs, cipher, and TLS version |
| 8 | **SUBDOMAINS** | Certificate Transparency | Discovers subdomains via crt.sh and DNS enumeration |
| 9 | **CERTS** | crt.sh | Public Certificate Transparency log interrogation |
| 10 | **TECH DETECT** | Web signature audit | Identifies web servers, frameworks, CDNs, and CMS platforms |
| 11 | **MAC VENDOR** | MacVendors / IEEE OUI | Hardware manufacturer identification from MAC address |
| 12 | **PHONE INTEL** | E.164 Numbering plan | Country code validation, international formatting, line type |
| 13 | **IP GEOLOCATE** | GeoIP Services | Resolves country, city, ISP, ASN, and coordinates |
| 14 | **CVE / VULN** | CISA KEV & NVD | Scored vulnerability intelligence and remediation steps |
| 15 | **URLHAUS** | abuse.ch URLhaus | Malware payload and Trojan distribution cross-reference |
| 16 | **DNS THREAT** | Spamhaus DROP / DNSBL | Malicious network blocklists and exit node checking |
| 17 | **DATA BREACH** | Exposure databases | Compromised credential and breach catalog analysis |
| 18 | **GITHUB RECON** | GitHub API | User and organization public repository and activity profiling |
| 19 | **IP SWEEP** | CIDR Subnet Sweeper | Subnet discovery and active network host enumeration |
| 20 | **ISMALICIOUS** | Unified Threat Index | Consolidated multi-source cyber threat score (0-100) |

> 📌 **Pin to Map Feature**: Any OSINT result with geographic coordinates can be pinned directly onto the live operational map with a single click!

---

## 🎨 Dual Themes: Ghost Protocol & Core Intelligence

Plotsiris supports live theme switching at the click of a button:
- **Ghost Protocol (Dark)**: Military SIGINT HUD aesthetic with deep obsidian background (`#0a0e14`), glowing neon accents (cyan `#00e5ff`, emerald `#10b981`, amber `#f59e0b`, crimson `#ef4444`), and high-contrast MapLibre dark tiles (`carto-darkmatter`).
- **Core Intelligence (Light)**: Cartographic light theme with clean surfaces (`#f8fafc`), crisp slate text (`#0f172a`), tactical blue accents (`#0284c7`), and Carto Positron basemaps (`carto-positron`).

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- `pip` package manager

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/carbon-evolution/plotsiris.git
cd Plotsiris

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
python main.py
```
Open your browser to `http://127.0.0.1:8050` (or `http://localhost:8050`).

---

## ☁️ Cloud Deployment (Plotly Cloud / Dash Enterprise / Docker)

Plotsiris is architected for zero-friction cloud deployment.

### Preparing the Cloud Package
Run the automated deployment packager:
```bash
python scripts/prepare_cloud.py
```
This builds a completely self-contained deployment folder at:
```
deploy/plotly-cloud/
├── app.py              # WSGI entrypoint with explicit Dash app & server
├── main.py             # CLI runner
├── requirements.txt    # Production dependencies
├── README.md           # Deployment overview
├── assets/             # CSS stylesheets and fonts
└── plotsiris/          # Full package source code
```

### Deploying to Plotly Cloud / Dash Enterprise
1. Upload the contents of `deploy/plotly-cloud/` to Plotly Cloud or Dash Enterprise.
2. Set the application entry point to `app.py` (`app:server`).
3. Set the Python version to `3.11`.
4. Plotly Cloud will automatically install dependencies from `requirements.txt` and serve the dashboard with Gunicorn.

### Deploying with Docker
Build and run the production container:
```bash
docker build -t plotsiris:latest .
docker run -p 8050:8050 plotsiris:latest
```

---

## 🧪 Testing

Plotsiris includes a comprehensive test suite covering domain serialization, intelligence services, OSINT reconnaissance engines, map generation, and Dash application startup:

```bash
python -m pytest -v
```

---

## 🔒 Security & Privacy
Plotsiris follows a keyless-first, fail-soft architecture:
- All external API keys (`GEMINI_API_KEY`, `NVD_API_KEY`, `URLHAUS_KEY`) are completely optional.
- If offline or keys are absent, intelligent baseline datasets and heuristic analytical models activate automatically.
- No confidential data or API keys are ever committed to version control.

---

## 📄 License
Released under the [MIT License](LICENSE).
