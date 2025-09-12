import ssl
import socket
import json
import os
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend

def get_ssl_info(hostname, port=443):
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            der_cert = ssock.getpeercert(binary_form=True)  # binary DER form
            cert = ssock.getpeercert()
            cipher = ssock.cipher()
            tls_version = ssock.version()

    x509_cert = x509.load_der_x509_certificate(der_cert, default_backend())
    public_key = x509_cert.public_key()
    key_size = getattr(public_key, "key_size", None)

    def parse_date(date_str):
        return datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z").isoformat()

    return {
        "hostname": hostname,
        "tls_version": tls_version,
        "cipher": cipher[0],
        "key_size": key_size,
        "subject": dict(x[0] for x in cert.get("subject", [])),
        "issuer": dict(x[0] for x in cert.get("issuer", [])),
        "serialNumber": cert.get("serialNumber"),
        "version": cert.get("version"),
        "notBefore": parse_date(cert["notBefore"]),
        "notAfter": parse_date(cert["notAfter"]),
        "subjectAltName": [name for _, name in cert.get("subjectAltName", [])],
    }

def save_ssl_info(hostname, filename="ssl.json"):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    json_dir = os.path.join(project_root, "json")
    os.makedirs(json_dir, exist_ok=True)
    file_path = os.path.join(json_dir, filename)

    info = get_ssl_info(hostname)
    with open(file_path, "w") as f:
        json.dump(info, f, indent=4)

    return file_path
