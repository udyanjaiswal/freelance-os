from django.test import TestCase
from scoring.enrichment import is_safe_public_url
from discovery.sources.osm import sanitize_osm_input


class SSRFAndInjectionSecurityTests(TestCase):
    def test_ssrf_blocks_private_and_loopback_ips(self):
        """SSRF protection must block private, loopback, and cloud metadata IPs."""
        blocked_urls = [
            "http://127.0.0.1",
            "http://127.0.0.1:80",
            "http://localhost",
            "http://10.0.0.1",
            "http://172.16.0.1",
            "http://192.168.1.1",
            "http://169.254.169.254",  # AWS/GCP metadata
            "http://metadata.google.internal",
            "http://0.0.0.0",
            "http://[::1]",
            "http://[::]",
            "ftp://example.com",
            "file:///etc/passwd",
        ]
        for url in blocked_urls:
            self.assertFalse(
                is_safe_public_url(url),
                f"URL should have been blocked by SSRF defense: {url}",
            )

    def test_ssrf_blocks_non_standard_ports(self):
        """SSRF protection must block non-standard ports to prevent port scanning."""
        port_scan_urls = [
            "http://8.8.8.8:22",
            "http://8.8.8.8:3306",
            "http://8.8.8.8:6379",
            "http://8.8.8.8:8000",
            "http://8.8.8.8:8080",
        ]
        for url in port_scan_urls:
            self.assertFalse(
                is_safe_public_url(url),
                f"Non-standard port should have been blocked: {url}",
            )

    def test_overpass_ql_injection_sanitization(self):
        """Sanitization must neutralize control characters and quotes from Overpass queries."""
        malicious_input = 'salons"]; node(1); ["name"~"test'
        cleaned = sanitize_osm_input(malicious_input)
        self.assertNotIn('"', cleaned)
        self.assertNotIn(';', cleaned)
        self.assertNotIn('[', cleaned)
        self.assertNotIn(']', cleaned)
        self.assertEqual(cleaned, "salons node(1) name~test")
