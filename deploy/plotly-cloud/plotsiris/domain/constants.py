"""Constants, presets, and seed definitions for Plotsiris."""

from typing import Dict, Any, List

# Map view presets with center and zoom
REGION_PRESETS = {
    "global": {"name": "Global", "lat": 20.0, "lon": 10.0, "zoom": 1.5},
    "europe": {"name": "Europe", "lat": 50.0, "lon": 15.0, "zoom": 3.8},
    "middle_east": {"name": "Middle East", "lat": 29.5, "lon": 44.0, "zoom": 4.5},
    "east_asia": {"name": "East Asia", "lat": 32.0, "lon": 125.0, "zoom": 4.0},
    "americas": {"name": "Americas", "lat": 38.0, "lon": -95.0, "zoom": 3.2},
    "ukraine": {"name": "Ukraine", "lat": 48.5, "lon": 36.0, "zoom": 5.8},
    "africa": {"name": "Africa", "lat": 5.0, "lon": 22.0, "zoom": 3.0},
    "se_asia": {"name": "SE Asia", "lat": 5.0, "lon": 110.0, "zoom": 4.0},
    "red_sea": {"name": "Red Sea & Hormuz", "lat": 20.0, "lon": 48.0, "zoom": 5.0},
    "arctic": {"name": "Arctic", "lat": 75.0, "lon": 10.0, "zoom": 2.5},
    "india": {"name": "India / Indo-Pacific", "lat": 21.0, "lon": 82.0, "zoom": 4.2},
    "sudan": {"name": "Sudan / Sahel", "lat": 14.0, "lon": 30.0, "zoom": 5.2},
}

# Supported map layer definitions
LAYER_DEFINITIONS = {
    "aviation": {
        "id": "aviation",
        "name": "Live Aviation (ADS-B)",
        "category": "mobility",
        "icon": "bi bi-airplane-fill",
        "color": "#38bdf8",
        "default": True,
        "description": "Live civil, commercial and military aircraft radar tracking."
    },
    "maritime": {
        "id": "maritime",
        "name": "Live Maritime (AIS)",
        "category": "mobility",
        "icon": "bi bi-water",
        "color": "#0ea5e9",
        "default": True,
        "description": "Commercial cargo, tanker, passenger, and naval vessels with heading vectors."
    },
    "cables": {
        "id": "cables",
        "name": "Submarine Data Cables",
        "category": "infrastructure",
        "icon": "bi bi-diagram-3-fill",
        "color": "#818cf8",
        "default": True,
        "description": "Transoceanic fiber-optic submarine telecommunication cables and landing stations."
    },
    "chokepoints": {
        "id": "chokepoints",
        "name": "Maritime Strategic Chokepoints",
        "category": "infrastructure",
        "icon": "bi bi-shield-exclamation",
        "color": "#f59e0b",
        "default": True,
        "description": "Critical geopolitical maritime straits, canals, and trade vulnerabilities."
    },
    "cctv": {
        "id": "cctv",
        "name": "Surveillance CCTV Feeds",
        "category": "surveillance",
        "icon": "bi bi-camera-video-fill",
        "color": "#10b981",
        "default": True,
        "description": "Worldwide government highway cameras & open surveillance streams."
    },
    "earthquakes": {
        "id": "earthquakes",
        "name": "Seismic Activity (USGS)",
        "category": "hazards",
        "icon": "bi bi-activity",
        "color": "#ef4444",
        "default": True,
        "description": "Recent 24-hour global earthquakes, depth and magnitude."
    },
    "fires": {
        "id": "fires",
        "name": "Active Wildfires (FIRMS)",
        "category": "hazards",
        "icon": "bi bi-fire",
        "color": "#f97316",
        "default": True,
        "description": "NASA FIRMS thermal anomalies and wildfire hotspot detections."
    },
    "weather": {
        "id": "weather",
        "name": "Severe Weather Alerts",
        "category": "hazards",
        "icon": "bi bi-cloud-lightning-rain-fill",
        "color": "#06b6d4",
        "default": True,
        "description": "Tropical storms, extreme weather warnings, and meteorological alerts."
    },
    "conflict": {
        "id": "conflict",
        "name": "Conflict Zones & Frontlines",
        "category": "geopolitics",
        "icon": "bi bi-crosshair",
        "color": "#dc2626",
        "default": True,
        "description": "Active conflict theatres, territorial control lines, and tactical incidents."
    },
    "nuclear": {
        "id": "nuclear",
        "name": "Nuclear & Energy Facilities",
        "category": "infrastructure",
        "icon": "bi bi-radioactive",
        "color": "#eab308",
        "default": True,
        "description": "Nuclear power stations, research reactors, and strategic grid hubs."
    },
    "cyber": {
        "id": "cyber",
        "name": "Cyber Threats & KEV",
        "category": "cyber",
        "icon": "bi bi-bug-fill",
        "color": "#a855f7",
        "default": True,
        "description": "CISA KEV active vulnerabilities, Tor exit nodes, and malicious infrastructure."
    },
    "satellites": {
        "id": "satellites",
        "name": "Satellites & Orbit Tracks",
        "category": "space",
        "icon": "bi bi-broadcast-pin",
        "color": "#ec4899",
        "default": True,
        "description": "ISS, reconnaissance satellites, GPS constellations, and orbital tracks."
    },
    "recon": {
        "id": "recon",
        "name": "OSINT Recon Findings",
        "category": "recon",
        "icon": "bi bi-geo-alt-fill",
        "color": "#00e5ff",
        "default": True,
        "description": "Target IP/domain reconnaissance pins with verdict assessment color-coding."
    },
    "eonet": {
        "id": "eonet",
        "name": "NASA EONET Events",
        "category": "hazards",
        "icon": "bi bi-globe-americas",
        "color": "#f97316",
        "default": True,
        "description": "NASA Earth Observatory live natural events: volcanoes, storms, and sea ice anomalies."
    },
    "reliefweb": {
        "id": "reliefweb",
        "name": "UN OCHA Disasters",
        "category": "geopolitics",
        "icon": "bi bi-exclamation-octagon-fill",
        "color": "#dc2626",
        "default": True,
        "description": "United Nations OCHA global humanitarian crises, conflicts, and disaster situations."
    },
    "botnets": {
        "id": "botnets",
        "name": "Feodo C2 Botnets",
        "category": "cyber",
        "icon": "bi bi-shield-slash-fill",
        "color": "#b91c1c",
        "default": True,
        "description": "Abuse.ch Feodo Tracker active banking trojan and botnet C2 infrastructure."
    }
}

# Major Global Maritime Chokepoints
MARITIME_CHOKEPOINTS = [
    {
        "id": "choke_suez",
        "name": "Suez Canal",
        "country": "Egypt",
        "lat": 30.5852,
        "lon": 32.2654,
        "daily_volume": "12% of global trade / 30% of container traffic",
        "risk_level": "ELEVATED",
        "description": "Critical waterway linking Mediterranean Sea to Red Sea and Indian Ocean."
    },
    {
        "id": "choke_bab_el_mandeb",
        "name": "Bab el-Mandeb Strait",
        "country": "Yemen / Djibouti",
        "lat": 12.5833,
        "lon": 43.3333,
        "daily_volume": "6.2M barrels of oil/day",
        "risk_level": "CRITICAL",
        "description": "Southern gateway to Red Sea; vulnerable to regional anti-ship missile attacks."
    },
    {
        "id": "choke_hormuz",
        "name": "Strait of Hormuz",
        "country": "Iran / Oman",
        "lat": 26.5667,
        "lon": 56.2500,
        "daily_volume": "21M barrels of oil/day (21% of petroleum consumption)",
        "risk_level": "HIGH",
        "description": "The world's most critical petroleum transit chokepoint."
    },
    {
        "id": "choke_malacca",
        "name": "Strait of Malacca",
        "country": "Singapore / Malaysia / Indonesia",
        "lat": 2.5000,
        "lon": 101.5000,
        "daily_volume": "16M barrels/day; 84,000 vessels/year",
        "risk_level": "LOW",
        "description": "Main shipping channel between Indian Ocean and Pacific Ocean."
    },
    {
        "id": "choke_panama",
        "name": "Panama Canal",
        "country": "Panama",
        "lat": 9.0800,
        "lon": -79.6800,
        "daily_volume": "5% of global maritime commerce",
        "risk_level": "ELEVATED",
        "description": "Interoceanic lock-based canal linking Atlantic and Pacific Oceans."
    },
    {
        "id": "choke_gibraltar",
        "name": "Strait of Gibraltar",
        "country": "Spain / Morocco / UK",
        "lat": 35.9667,
        "lon": -5.6000,
        "daily_volume": "71,000 vessels annually",
        "risk_level": "LOW",
        "description": "Strategic maritime strait connecting Atlantic Ocean to Mediterranean Sea."
    },
    {
        "id": "choke_bosporus",
        "name": "Turkish Straits (Bosporus & Dardanelles)",
        "country": "Turkey",
        "lat": 41.1167,
        "lon": 29.0833,
        "daily_volume": "3M barrels/day; 48,000 ships/year",
        "risk_level": "HIGH",
        "description": "Sole maritime outlet for Black Sea nations; Montreux Convention regulated."
    },
    {
        "id": "choke_danish",
        "name": "Danish Straits",
        "country": "Denmark / Sweden",
        "lat": 55.6000,
        "lon": 11.0000,
        "daily_volume": "3.2M barrels/day oil transit",
        "risk_level": "ELEVATED",
        "description": "Series of channels connecting Baltic Sea to North Sea."
    }
]

# Strategic Submarine Cables (Representative Major Transoceanic Arteries)
STRATEGIC_SUBSEA_CABLES = [
    {
        "id": "cable_transatlantic_apollo",
        "name": "Apollo Subsea Cable (US - UK - FR)",
        "lats": [40.71, 41.5, 45.0, 49.5, 50.1, 49.2],
        "lons": [-74.0, -65.0, -40.0, -15.0, -5.2, -0.5],
        "capacity": "25 Tbps",
        "color": "#818cf8"
    },
    {
        "id": "cable_sea_me_we_5",
        "name": "SEA-ME-WE 5 (FR - IT - EG - SA - IN - SG)",
        "lats": [43.3, 38.0, 31.2, 27.5, 21.5, 18.9, 5.9, 1.3],
        "lons": [5.3, 13.0, 30.0, 35.0, 38.5, 72.8, 80.2, 103.8],
        "capacity": "24 Tbps",
        "color": "#38bdf8"
    },
    {
        "id": "cable_transpacific_fafe",
        "name": "Faster Trans-Pacific (US - JP - TW)",
        "lats": [37.8, 42.0, 48.0, 45.0, 35.7, 25.0],
        "lons": [-122.4, -145.0, -170.0, 160.0, 140.8, 121.5],
        "capacity": "60 Tbps",
        "color": "#34d399"
    },
    {
        "id": "cable_2africa",
        "name": "2Africa Ring (UK - PT - ZA - KE - EG)",
        "lats": [50.5, 38.7, 14.7, -4.3, -33.9, -4.0, 11.5, 27.8, 31.0],
        "lons": [-4.5, -9.1, -17.4, 11.8, 18.4, 39.6, 43.1, 34.0, 32.5],
        "capacity": "180 Tbps",
        "color": "#f472b6"
    }
]

# Curated CCTV and Live Camera Registry (Real Live DOT & Municipal Feeds + Optical Fallbacks)
CCTV_REGISTRY = [
    {
        "id": "cam_uk_piccadilly",
        "name": "London Piccadilly Circus (TfL Live)",
        "country": "United Kingdom",
        "region": "London",
        "lat": 51.5096,
        "lon": -0.13484,
        "stream_url": "https://s3-eu-west-1.amazonaws.com/jamcams.tfl.gov.uk/00001.07450.mp4",
        "snapshot_url": "https://s3-eu-west-1.amazonaws.com/jamcams.tfl.gov.uk/00001.07450.jpg",
        "thumbnail_url": "https://s3-eu-west-1.amazonaws.com/jamcams.tfl.gov.uk/00001.07450.jpg",
        "feed_type": "video",
        "status": "ONLINE",
        "provider": "Transport for London (TfL JamCam)"
    },
    {
        "id": "cam_us_ca_01",
        "name": "San Francisco Bay Bridge / I-80 (Caltrans Live)",
        "country": "United States",
        "region": "California",
        "lat": 37.7983,
        "lon": -122.3778,
        "stream_url": "/assets/cctv_sf_bay.mp4",
        "snapshot_url": "https://cwwp2.dot.ca.gov/data/d4/cctv/image/tvd32i80baybridgesastowereast/tvd32i80baybridgesastowereast.jpg",
        "thumbnail_url": "https://cwwp2.dot.ca.gov/data/d4/cctv/image/tvd32i80baybridgesastowereast/tvd32i80baybridgesastowereast.jpg",
        "feed_type": "live_snapshot",
        "status": "ONLINE",
        "provider": "Caltrans District 4 CWWP2"
    },
    {
        "id": "cam_uk_westminster",
        "name": "London Westminster Bridge Rd (TfL Live)",
        "country": "United Kingdom",
        "region": "London",
        "lat": 51.4987,
        "lon": -0.11242,
        "stream_url": "https://s3-eu-west-1.amazonaws.com/jamcams.tfl.gov.uk/00001.06510.mp4",
        "snapshot_url": "https://s3-eu-west-1.amazonaws.com/jamcams.tfl.gov.uk/00001.06510.jpg",
        "thumbnail_url": "https://s3-eu-west-1.amazonaws.com/jamcams.tfl.gov.uk/00001.06510.jpg",
        "feed_type": "video",
        "status": "ONLINE",
        "provider": "Transport for London (TfL JamCam)"
    },
    {
        "id": "cam_sg_01",
        "name": "Singapore Woodlands / MCE (LTA 1080p Live)",
        "country": "Singapore",
        "region": "Central",
        "lat": 1.2789,
        "lon": 103.8536,
        "stream_url": "/assets/cctv_highway.mp4",
        "snapshot_url": "https://api.data.gov.sg/v1/transport/traffic-images",
        "thumbnail_url": "/assets/surveillance_stream.gif",
        "feed_type": "live_snapshot",
        "live_api": "sg_lta",
        "status": "ONLINE",
        "provider": "Singapore Land Transport Authority (LTA)"
    },
    {
        "id": "cam_hk_01",
        "name": "Hong Kong Wan Chai Harbour Tunnel (TD Live)",
        "country": "Hong Kong",
        "region": "Wan Chai",
        "lat": 22.2819,
        "lon": 114.1812,
        "stream_url": "/assets/cctv_highway.mp4",
        "snapshot_url": "https://tdcctv.data.one.gov.hk/H429F.JPG",
        "thumbnail_url": "https://tdcctv.data.one.gov.hk/H429F.JPG",
        "feed_type": "live_snapshot",
        "status": "ONLINE",
        "provider": "HK Transport Department"
    },
    {
        "id": "cam_hk_02",
        "name": "Hong Kong Kowloon Cross-Harbour (TD Live)",
        "country": "Hong Kong",
        "region": "Kowloon",
        "lat": 22.3016,
        "lon": 114.1803,
        "stream_url": "/assets/cctv_highway.mp4",
        "snapshot_url": "https://tdcctv.data.one.gov.hk/K107F.JPG",
        "thumbnail_url": "https://tdcctv.data.one.gov.hk/K107F.JPG",
        "feed_type": "live_snapshot",
        "status": "ONLINE",
        "provider": "HK Transport Department"
    },
    {
        "id": "cam_us_tx_01",
        "name": "Austin Congress Ave & 6th St (Mobility Live)",
        "country": "United States",
        "region": "Texas",
        "lat": 30.2672,
        "lon": -97.7431,
        "stream_url": "/assets/cctv_highway.mp4",
        "snapshot_url": "https://cctv.austinmobility.io/image/28.jpg",
        "thumbnail_url": "https://cctv.austinmobility.io/image/28.jpg",
        "feed_type": "live_snapshot",
        "status": "ONLINE",
        "provider": "Austin Transportation & Public Works"
    },
    {
        "id": "cam_uk_tfl_01",
        "name": "London Tower Bridge / Trafalgar (TfL Live)",
        "country": "United Kingdom",
        "region": "London",
        "lat": 51.5055,
        "lon": -0.0754,
        "stream_url": "https://s3-eu-west-1.amazonaws.com/jamcams.tfl.gov.uk/00001.03651.mp4",
        "snapshot_url": "https://s3-eu-west-1.amazonaws.com/jamcams.tfl.gov.uk/00001.03651.jpg",
        "thumbnail_url": "https://s3-eu-west-1.amazonaws.com/jamcams.tfl.gov.uk/00001.03651.jpg",
        "feed_type": "video",
        "status": "ONLINE",
        "provider": "Transport for London (TfL JamCam)"
    },
    {
        "id": "cam_us_ny_01",
        "name": "Times Square 46th St & Broadway",
        "country": "United States",
        "region": "New York",
        "lat": 40.7580,
        "lon": -73.9855,
        "stream_url": "/assets/cctv_sf_bay.mp4",
        "snapshot_url": "/assets/surveillance_stream.gif",
        "thumbnail_url": "/assets/surveillance_stream.gif",
        "feed_type": "video",
        "status": "ONLINE",
        "provider": "EarthCam / NYC DOT"
    },
    {
        "id": "cam_tw_01",
        "name": "Taipei Freeway 1 - Yuanshan Interchange",
        "country": "Taiwan",
        "region": "Taipei",
        "lat": 25.0760,
        "lon": 121.5280,
        "stream_url": "/assets/cctv_highway.mp4",
        "snapshot_url": "/assets/surveillance_stream.gif",
        "thumbnail_url": "/assets/surveillance_stream.gif",
        "feed_type": "video",
        "status": "ONLINE",
        "provider": "Taiwan THB Traffic Bureau"
    }
]

# Curated 20 OSINT Tools List for the Reconnaissance Suite
# Strictly separated into Passive Intelligence Gathering vs. Active Reconnaissance
OSINT_TOOLS = [
    {"id": "dns", "name": "DNS ENUM", "icon": "bi-globe", "category": "passive", "desc": "Resolve A, AAAA, MX, NS, TXT via Google DoH", "placeholder": "e.g. google.com or 8.8.8.8"},
    {"id": "whois", "name": "WHOIS / RDAP", "icon": "bi-person-badge", "category": "passive", "desc": "Domain registrar, registrant info & OFAC sanctions check", "placeholder": "e.g. microsoft.com"},
    {"id": "portscan", "name": "PORT SCAN", "icon": "bi-door-open", "category": "active", "desc": "Active TCP connection audit (Authorisation Required under CMA 1990)", "placeholder": "e.g. scanme.nmap.org or 1.1.1.1"},
    {"id": "shodan", "name": "SHODAN IoT", "icon": "bi-hdd-network", "category": "passive", "desc": "Query Shodan InternetDB cached open ports & CVEs", "placeholder": "e.g. 1.1.1.1 or 8.8.4.4"},
    {"id": "bgp", "name": "BGP / ASN", "icon": "bi-diagram-2", "category": "passive", "desc": "RIPEstat BGP prefix routing, ASN, and announcing peer info", "placeholder": "e.g. 8.8.8.8 or AS15169"},
    {"id": "headers", "name": "HTTP HEADERS", "icon": "bi-shield-check", "category": "passive", "desc": "Audit HSTS, CSP, X-Frame, CORS & security flags", "placeholder": "e.g. https://github.com"},
    {"id": "ssl", "name": "SSL / TLS", "icon": "bi-lock", "category": "passive", "desc": "Inspect X.509 certificate expiry, issuer, cipher strength", "placeholder": "e.g. cloudflare.com:443"},
    {"id": "subdomains", "name": "SUBDOMAINS", "icon": "bi-folder2-open", "category": "passive", "desc": "Enumerate subdomains via Certificate Transparency (crt.sh)", "placeholder": "e.g. nasa.gov"},
    {"id": "certs", "name": "CERTS (crt.sh)", "icon": "bi-patch-check", "category": "passive", "desc": "Query public Certificate Transparency log databases", "placeholder": "e.g. tesla.com"},
    {"id": "tech", "name": "TECH DETECT", "icon": "bi-cpu", "category": "passive", "desc": "Fingerprint backend stack, web server, and CMS engines", "placeholder": "e.g. https://wordpress.org"},
    {"id": "mac", "name": "MAC VENDOR", "icon": "bi-ethernet", "category": "passive", "desc": "Lookup hardware vendor OUI from MAC address", "placeholder": "e.g. 00:1A:2B:3C:4D:5E"},
    {"id": "phone", "name": "PHONE INTEL", "icon": "bi-telephone", "category": "passive", "desc": "Analyze telephone numbers, E.164, carrier line type", "placeholder": "e.g. +14155552671"},
    {"id": "ip_geo", "name": "IP GEOLOCATE", "icon": "bi-pin-map", "category": "passive", "desc": "Pinpoint country, city, ISP, ASN, and coordinates", "placeholder": "e.g. 142.250.190.46"},
    {"id": "cve_lookup", "name": "CVE / VULN", "icon": "bi-bug", "category": "passive", "desc": "Lookup CISA KEV and NVD vulnerability scoring", "placeholder": "e.g. CVE-2024-38077 or Log4j"},
    {"id": "urlhaus", "name": "URLHAUS", "icon": "bi-virus", "category": "passive", "desc": "Check abuse.ch malware distribution repository", "placeholder": "e.g. suspicious-site.xyz"},
    {"id": "dns_threat", "name": "DNS THREAT", "icon": "bi-exclamation-octagon", "category": "passive", "desc": "Cross-reference Spamhaus DNSBL and reputation lists", "placeholder": "e.g. 185.220.101.5"},
    {"id": "leaks", "name": "DATA BREACH", "icon": "bi-envelope-exclamation", "category": "passive", "desc": "Check public exposure catalogs for compromised records", "placeholder": "e.g. target@example.com"},
    {"id": "github", "name": "GITHUB RECON", "icon": "bi-github", "category": "passive", "desc": "Profile public repositories, contributors, key exposure", "placeholder": "e.g. octocat"},
    {"id": "subnet", "name": "IP SWEEP", "icon": "bi-broadcast", "category": "active", "desc": "CIDR prefix sweep and device discovery (Authorisation Required)", "placeholder": "e.g. 192.168.1.0/24"},
    {"id": "ismalicious", "name": "ISMALICIOUS", "icon": "bi-shield-slash", "category": "passive", "desc": "Multi-source consolidated cyber threat rating", "placeholder": "e.g. badguy.top"}
]

# Tools requiring explicit operator confirmation under CMA 1990
ACTIVE_OSINT_TOOLS = {"portscan", "subnet"}

# Authorized test hosts for active verification
APPROVED_DEMO_TARGETS = {
    "scanme.nmap.org",   # Official Nmap Project authorized scanner host
    "1.1.1.1",           # Cloudflare public resolver
    "8.8.8.8",           # Google public resolver
    "127.0.0.1",         # Loopback
    "localhost"
}
