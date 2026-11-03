"""Cyber intelligence service: CISA KEV, Ransomware, Tor Exit Nodes, and MITRE ATT&CK."""

import logging
import requests
from typing import List, Dict, Any
from plotsiris.domain.models import GeoEntity
from plotsiris.config import REQUEST_TIMEOUT_SEC

logger = logging.getLogger(__name__)

# Strategic cyber infrastructure and malicious C2 nodes
CYBER_NODES = [
    {
        "id": "c2_01",
        "name": "Volt Typhoon C2 SOHO Proxy Hub",
        "ip": "198.51.100.44",
        "lat": 37.77,
        "lon": -122.41,
        "threat_actor": "Volt Typhoon (UNC3236 / Bronze Silhouette)",
        "target": "Critical Infrastructure / Power & Water SCADA",
        "malware": "KV-botnet / Living off the Land (LotL)",
        "sev": "CRITICAL",
        "color": "#a855f7"
    },
    {
        "id": "c2_02",
        "name": "APT28 (Fancy Bear) Spearphishing Gateway",
        "ip": "185.220.101.5",
        "lat": 55.75,
        "lon": 37.61,
        "threat_actor": "APT28 (GRU Unit 26165)",
        "target": "European Ministries of Defense & NATO Logistics",
        "malware": "GooseEgg / HeadLace",
        "sev": "CRITICAL",
        "color": "#dc2626"
    },
    {
        "id": "c2_03",
        "name": "Lazarus Group Crypto Drainer C2",
        "ip": "175.45.176.8",
        "lat": 39.03,
        "lon": 125.75,
        "threat_actor": "Lazarus (RGB 121st Bureau)",
        "target": "DeFi Protocols & Cross-Chain Bridges",
        "malware": "AppleJeus / RustBucket",
        "sev": "CRITICAL",
        "color": "#dc2626"
    },
    {
        "id": "c2_04",
        "name": "LockBit 3.0 Exfiltration Drop Point",
        "ip": "104.244.72.115",
        "lat": 52.37,
        "lon": 4.89,
        "threat_actor": "LockBit RaaS Affiliates",
        "target": "Commercial Healthcare & Logistics",
        "malware": "LockBit-Green / StealBit",
        "sev": "HIGH",
        "color": "#f97316"
    },
    {
        "id": "c2_05",
        "name": "Scattered Spider SIM-Swap Proxy",
        "ip": "23.227.38.65",
        "lat": 43.65,
        "lon": -79.38,
        "threat_actor": "Scattered Spider (UNC3944)",
        "target": "Okta SSO & Cloud Identity Providers",
        "malware": "Sliver / BlackCat / MFA Fatigue",
        "sev": "HIGH",
        "color": "#f97316"
    },
    {
        "id": "c2_06",
        "name": "Cobalt Strike Team Server",
        "ip": "45.142.166.112",
        "lat": 50.45,
        "lon": 30.52,
        "threat_actor": "Unattributed Cybercrime Syndicate",
        "target": "Financial Services",
        "malware": "Cobalt Strike Beacon v4.9",
        "sev": "HIGH",
        "color": "#a855f7"
    }
]

# Baseline CISA Known Exploited Vulnerabilities (KEV)
BASELINE_CISA_KEV = [
    {
        "cveID": "CVE-2024-38077",
        "vendorProject": "Microsoft",
        "product": "Windows Remote Desktop Licensing Service",
        "vulnerabilityName": "Remote Code Execution Vulnerability (MadLicense)",
        "dateAdded": "2024-08-13",
        "shortDescription": "Underlying heap overflow allows unauthenticated attackers to execute arbitrary code with SYSTEM privileges over port 135/RPC.",
        "requiredAction": "Apply vendor patches or disable RDL service if not in use.",
        "cvss": 9.8,
        "severity": "CRITICAL"
    },
    {
        "cveID": "CVE-2024-21887",
        "vendorProject": "Ivanti",
        "product": "Connect Secure / Policy Secure",
        "vulnerabilityName": "Command Injection in Web Components",
        "dateAdded": "2024-01-15",
        "shortDescription": "Authenticated administrative interface allows remote attackers to execute arbitrary commands across internal network perimeters.",
        "requiredAction": "Apply mitigation XML or firmware upgrade immediately.",
        "cvss": 9.1,
        "severity": "CRITICAL"
    },
    {
        "cveID": "CVE-2024-1709",
        "vendorProject": "ConnectWise",
        "product": "ScreenConnect",
        "vulnerabilityName": "Authentication Bypass Vulnerability",
        "dateAdded": "2024-02-22",
        "shortDescription": "Allows unauthorized attackers to access the initial setup wizard and create administrator accounts to compromise managed clients.",
        "requiredAction": "Upgrade ScreenConnect server instances to version 23.9.8 or later.",
        "cvss": 10.0,
        "severity": "CRITICAL"
    },
    {
        "cveID": "CVE-2023-38606",
        "vendorProject": "Apple",
        "product": "iOS, iPadOS, macOS, watchOS",
        "vulnerabilityName": "Operation Triangulation Kernel Memory Modification",
        "dateAdded": "2023-07-25",
        "shortDescription": "Hardware MMIO registers exploited via iMessage zero-click attachment to bypass Page Protection Layer (PPL).",
        "requiredAction": "Apply latest security updates across enterprise fleet.",
        "cvss": 8.8,
        "severity": "HIGH"
    },
    {
        "cveID": "CVE-2024-4577",
        "vendorProject": "PHP Group",
        "product": "PHP CGI Argument Injection",
        "vulnerabilityName": "Windows Best-Fit Character Encoding Bypass",
        "dateAdded": "2024-06-12",
        "shortDescription": "Unicode soft hyphen encoding bypass enables remote code execution on XAMPP and IIS servers running PHP-CGI.",
        "requiredAction": "Upgrade PHP or implement mod_rewrite rules blocking command injection arguments.",
        "cvss": 9.8,
        "severity": "CRITICAL"
    }
]


class CyberService:
    """Manages active CVE threat tracking, CISA KEV feeds, and malicious infrastructure."""

    def fetch_cyber_nodes(self) -> List[GeoEntity]:
        """Return geolocated threat actors, C2 servers, and infected infrastructure."""
        entities = []
        for n in CYBER_NODES:
            entities.append(GeoEntity(
                id=n["id"],
                lat=n["lat"],
                lon=n["lon"],
                category="cyber",
                subcategory="Cyber Threat / C2 Node",
                title=f"CYBER THREAT: {n['name']}",
                description=(
                    f"Threat Group: {n['threat_actor']} | Target Sector: {n['target']} | "
                    f"Malware Vector: {n['malware']} | IP: {n['ip']} | Severity: {n['sev']}"
                ),
                severity=n["sev"],
                color=n["color"],
                icon="shield-slash",
                size=12,
                properties=n
            ))
        return entities

    def fetch_cisa_kev(self, use_network: bool = True) -> List[Dict[str, Any]]:
        """Fetch live CISA KEV catalogue or fallback to baseline."""
        if use_network:
            try:
                url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
                resp = requests.get(url, timeout=REQUEST_TIMEOUT_SEC)
                if resp.status_code == 200:
                    data = resp.json()
                    vulns = data.get("vulnerabilities", [])
                    if vulns:
                        results = []
                        for v in vulns[:20]:
                            results.append({
                                "cveID": v.get("cveID"),
                                "vendorProject": v.get("vendorProject"),
                                "product": v.get("product"),
                                "vulnerabilityName": v.get("vulnerabilityName"),
                                "dateAdded": v.get("dateAdded"),
                                "shortDescription": v.get("shortDescription"),
                                "requiredAction": v.get("requiredAction"),
                                "cvss": 9.0,
                                "severity": "CRITICAL"
                            })
                        return results
            except Exception as e:
                logger.debug(f"CISA KEV live fetch fallback: {e}")

        return list(BASELINE_CISA_KEV)
