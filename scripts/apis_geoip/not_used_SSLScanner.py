import ssl
import socket
from datetime import datetime

class SSLCertScanner:
    def __init__(self):
        self.source = "LocalSSLScan"

    def fetch_result(self, target_url):
        context = ssl.create_default_context()
        try:
            conn = socket.create_connection((target_url, 443), timeout=5)
            with context.wrap_socket(conn, server_hostname=target_url) as ssock:
                cert = ssock.getpeercert()
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": self.source
            }

        # Parse certificate details
        subject = dict(x[0] for x in cert.get("subject", []))
        issuer = dict(x[0] for x in cert.get("issuer", []))
        cn = subject.get("commonName", "")
        issuer_cn = issuer.get("commonName", "")
        not_after = cert.get("notAfter", "")

        try:
            expiry_date = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
            is_expired = expiry_date < datetime.utcnow()
        except:
            expiry_date = None
            is_expired = None

        is_self_signed = cn == issuer_cn
        unsafe = is_expired or is_self_signed if is_expired is not None else False

        return {
            "success": True,
            "unsafe": unsafe,
            "source": self.source,
            "extra": {
                "common_name": cn,
                "issuer": issuer_cn,
                "expires_on": not_after,
                "is_expired": is_expired,
                "is_self_signed": is_self_signed
            }
        }
