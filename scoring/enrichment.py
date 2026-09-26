import ipaddress
import socket
import urllib.parse
import requests


def is_safe_public_url(url):
    """
    Validates that a URL uses http/https and does NOT resolve to
    private, loopback, link-local (cloud metadata), or reserved IP addresses.
    Prevents Server-Side Request Forgery (SSRF).
    """
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Port restriction: only allow standard web ports to prevent internal/external port scanning
        if parsed.port not in (None, 80, 443):
            return False

        # Disallow explicit localhost or metadata hostnames
        if hostname.lower() in ("localhost", "metadata.google.internal"):
            return False

        # Resolve hostname to IP addresses
        addr_info = socket.getaddrinfo(hostname, None)
        if not addr_info:
            return False

        for item in addr_info:
            ip_str = item[4][0]
            ip = ipaddress.ip_address(ip_str)

            # Block private networks (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
            # Block loopback (127.0.0.0/8, ::1)
            # Block link-local / cloud metadata (169.254.0.0/16, fe80::/10)
            # Block reserved, multicast, and unspecified (0.0.0.0, ::)
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
                or ip.is_unspecified
            ):
                return False

        return True
    except (ValueError, socket.error, socket.gaierror):
        return False


def enrich_lead(lead):
    """
    Basic V1 enrichment.
    Checks whether an existing website is reachable.
    Guarded against Server-Side Request Forgery (SSRF).
    """

    result = {
        "website_status": None,
    }

    if not lead.website:
        return result

    website = lead.website.strip()

    if not website.startswith(("http://", "https://")):
        website = "https://" + website

    # SSRF Protection: verify target is a valid public endpoint before requesting
    if not is_safe_public_url(website):
        result["website_status"] = "not_working"
        return result

    try:
        response = requests.get(
            website,
            timeout=5,
            allow_redirects=False,  # Prevent redirect-based SSRF bypass
            headers={
                "User-Agent": "FreelancerOS/1.0"
            },
        )

        # 2xx and 3xx redirect status codes confirm website exists/reachable
        if response.status_code < 400:
            result["website_status"] = "working"
        else:
            result["website_status"] = "not_working"

    except requests.RequestException:
        result["website_status"] = "not_working"

    return result