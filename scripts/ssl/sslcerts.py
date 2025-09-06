import ssl
import socket
import json
from datetime import datetime

def get_ssl_info(hostname, port=443):
    """Fetch SSL certificate details for a given hostname."""
    context = ssl.create_default_context()

    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            cipher = ssock.cipher()
            tls_version = ssock.version()

    def parse_date(date_str):
        return datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z").isoformat()

    ssl_info = {
        "hostname": hostname,
        "tls_version": tls_version,
        "cipher": cipher[0],
        "subject": dict(x[0] for x in cert.get("subject", [])),
        "issuer": dict(x[0] for x in cert.get("issuer", [])),
        "serialNumber": cert.get("serialNumber"),
        "version": cert.get("version"),
        "notBefore": parse_date(cert["notBefore"]),
        "notAfter": parse_date(cert["notAfter"]),
        "subjectAltName": [name for _, name in cert.get("subjectAltName", [])],
    }

    return ssl_info

def save_ssl_info(hostname, filename="../../json/ssl.json"):
    """Fetch SSL info and save it to JSON file."""
    info = get_ssl_info(hostname)
    with open(filename, "w") as f:
        json.dump(info, f, indent=4)
    return filename

# If run directly, just print usage
if __name__ == "__main__":
    print("This is a module. Import and call save_ssl_info() from another script.")
