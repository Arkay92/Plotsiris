"""Resilient HTTP client helper for open and public intelligence feeds."""

from __future__ import annotations

import logging
from typing import Optional, Dict
import requests
import urllib3

# Suppress insecure request warnings when SSL fallback is triggered in enterprise / dev environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Plotsiris-Defense-Telemetry/2.5 (Open-Source Multi-Domain COP)",
    "Accept": "application/json, text/plain, */*"
}


def safe_get(url: str, timeout: int = 8, headers: Optional[Dict[str, str]] = None) -> Optional[requests.Response]:
    """Execute an HTTP GET request with SSL verification fallback and clean timeouts.
    
    Tries verified SSL first; if local CA certificates or proxies fail verification,
    gracefully falls back to verify=False so open-source feeds always populate.
    """
    merged_headers = dict(DEFAULT_HEADERS)
    if headers:
        merged_headers.update(headers)

    try:
        resp = requests.get(url, timeout=timeout, headers=merged_headers)
        if resp.status_code == 200:
            return resp
        logger.debug(f"Feed {url} returned HTTP {resp.status_code}")
        return resp
    except requests.exceptions.SSLError:
        try:
            logger.debug(f"SSL verification fallback for feed {url}")
            resp = requests.get(url, verify=False, timeout=timeout, headers=merged_headers)
            return resp
        except Exception as e:
            logger.debug(f"SSL fallback failed for {url}: {e}")
            return None
    except requests.exceptions.RequestException as e:
        logger.debug(f"HTTP request failed for {url}: {e}")
        return None
    except Exception as e:
        logger.debug(f"Unexpected error fetching {url}: {e}")
        return None
