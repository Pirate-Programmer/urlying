import ssl
import socket
import json
import os
import subprocess
import shutil
import tempfile
import re
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

def _fmt_dt(dt):
    """
    Accept either:
      - timezone-aware properties like not_valid_after_utc (preferred), or
      - older naive datetime properties (fallback),
      - or an input string (returned as-is if parsing fails).
    Returns ISO 8601 string or None.
    """
    if dt is None:
        return None

    # Preferred: use isoformat if available (handles tz-aware datetimes)
    if hasattr(dt, "isoformat"):
        try:
            return dt.isoformat()
        except Exception:
            pass

    # For older string inputs, try to parse common OpenSSL format
    if isinstance(dt, str):
        try:
            return datetime.strptime(dt, "%b %d %H:%M:%S %Y %Z").isoformat()
        except Exception:
            return dt

    return None


def _x509_to_dict(x509_cert):
    """
    Convert a cryptography.x509.Certificate to a serializable dict.
    Defensive: if PEM/DER serialization fails, we continue without them.
    """
    subj = {}
    for attr in x509_cert.subject:
        key = attr.oid._name if hasattr(attr.oid, "_name") else attr.oid.dotted_string
        subj[key] = attr.value

    issuer = {}
    for attr in x509_cert.issuer:
        key = attr.oid._name if hasattr(attr.oid, "_name") else attr.oid.dotted_string
        issuer[key] = attr.value

    san = []
    try:
        ext = x509_cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        san = ext.value.get_values_for_type(x509.DNSName)
    except Exception:
        san = []

    public_key = x509_cert.public_key()
    key_size = getattr(public_key, "key_size", None)

    try:
        sig_alg = x509_cert.signature_hash_algorithm.name
    except Exception:
        sig_alg = None

    # pick the preferred datetime attributes if available (utc-aware)
    not_before = None
    not_after = None
    if hasattr(x509_cert, "not_valid_before_utc"):
        try:
            not_before = _fmt_dt(x509_cert.not_valid_before_utc)
        except Exception:
            not_before = _fmt_dt(getattr(x509_cert, "not_valid_before", None))
    else:
        not_before = _fmt_dt(getattr(x509_cert, "not_valid_before", None))

    if hasattr(x509_cert, "not_valid_after_utc"):
        try:
            not_after = _fmt_dt(x509_cert.not_valid_after_utc)
        except Exception:
            not_after = _fmt_dt(getattr(x509_cert, "not_valid_after", None))
    else:
        not_after = _fmt_dt(getattr(x509_cert, "not_valid_after", None))

    result = {
        "subject": subj,
        "issuer": issuer,
        "serialNumber": format(x509_cert.serial_number, "x"),
        "version": x509_cert.version.name if hasattr(x509_cert, "version") else None,
        "notBefore": not_before,
        "notAfter": not_after,
        "subjectAltName": san,
        "key_size": key_size,
        "signature_algorithm": sig_alg,
    }

    # PEM and DER are optional — do them inside try/except to avoid crashes
    try:
        pem = x509_cert.public_bytes(encoding=serialization.Encoding.PEM).decode("utf-8")
        result["pem"] = pem
    except Exception:
        pass

    try:
        der_hex = x509_cert.public_bytes(encoding=serialization.Encoding.DER).hex()
        result["der_bytes"] = der_hex
    except Exception:
        pass

    return result


def _parse_verify_return(out):
    """
    Parse 'Verify return code: <num> (<text>)' from openssl output.
    Returns (code:int|None, text:str|None).
    """
    if not out:
        return None, None
    m = re.search(r"Verify return code:\s*(\d+)\s*\((.*?)\)", out)
    if m:
        try:
            return int(m.group(1)), m.group(2).strip()
        except Exception:
            return None, m.group(2).strip()
    return None, None


def _fetch_chain_with_openssl_cli(hostname, port=443, timeout=10, debug_write_raw_output=True):
    """
    Fetch chain using `openssl s_client -showcerts`.
    Returns tuple (certs_list, openssl_raw_output, verify_code, verify_text).
    Raises FileNotFoundError if openssl missing.
    Raises RuntimeError for other fatal openssl failures (timeouts, connection issues, or debug dump created).
    """
    if shutil.which("openssl") is None:
        raise FileNotFoundError("openssl not found on PATH")

    cmd = [
        "openssl", "s_client", "-showcerts",
        "-connect", f"{hostname}:{port}",
        "-servername", hostname,
    ]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            input="QUIT\n"
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("openssl s_client timed out") from e
    except Exception as e:
        raise RuntimeError(f"openssl s_client failed: {e}") from e

    out = (proc.stdout or "") + "\n" + (proc.stderr or "")

    # quick check for common connection errors reported by openssl text
    if any(s in out for s in ["Connection refused", "connect:errno", "No route to host", "Connection timed out"]):
        raise RuntimeError(f"openssl reported connection error when connecting to {hostname}:{port}: first-lines: {out.splitlines()[:6]}")

    # Extract PEM blocks between BEGIN/END CERTIFICATE
    pem_blocks = []
    current_block = []
    in_block = False
    for raw_line in out.splitlines():
        line = raw_line.strip()
        if line == "-----BEGIN CERTIFICATE-----":
            in_block = True
            current_block = [line]
            continue
        if in_block:
            current_block.append(line)
            if line == "-----END CERTIFICATE-----":
                pem = "\n".join(current_block) + "\n"
                pem_blocks.append(pem)
                in_block = False
                current_block = []

    certs = []
    for pem in pem_blocks:
        try:
            cert = x509.load_pem_x509_certificate(pem.encode("utf-8"), default_backend())
            certs.append(cert)
        except Exception:
            # skip unparsable blocks
            continue

    verify_code, verify_text = _parse_verify_return(out)

    # If parsing yields no certs and debug requested, write raw output to tempfile for inspection and raise
    if debug_write_raw_output and not certs:
        try:
            tf = tempfile.NamedTemporaryFile(delete=False, prefix="openssl_debug_", suffix=".txt", mode="w", encoding="utf-8")
            tf.write(f"COMMAND: {' '.join(cmd)}\n\n")
            tf.write("===== STDOUT+STDERR =====\n")
            tf.write(out)
            tf.close()
            raise RuntimeError(f"openssl returned no PEM blocks; raw output written to {tf.name}")
        except Exception as e:
            raise RuntimeError(f"openssl returned no PEM blocks and debug write failed: {e}")

    return certs, out, verify_code, verify_text


def get_ssl_info(hostname, port=443, timeout=5.0, openssl_timeout=10):
    """
    Return dict with leaf info plus 'chain' (may be empty), 'chain_method', 'chain_error',
    and openssl verification results (openssl_verify_code / openssl_verify_text).
    Uses stdlib ssl for leaf; uses openssl CLI for chain when available.
    """
    info = {
        "hostname": hostname,
        "tls_version": None,
        "cipher": None,
        "key_size": None,
        "subject": {},
        "issuer": {},
        "serialNumber": None,
        "version": None,
        "notBefore": None,
        "notAfter": None,
        "subjectAltName": [],
        "signature_algorithm": None,
        "chain": [],
        "chain_method": "none",
        "chain_error": None,
        "leaf_present": False,
        "openssl_verify_code": None,
        "openssl_verify_text": None,
    }

    # First, get leaf info (stdlib ssl)
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                der_cert = ssock.getpeercert(binary_form=True)
                cert_struct = ssock.getpeercert()
                cipher = ssock.cipher()
                tls_version = ssock.version()

        x509_leaf = x509.load_der_x509_certificate(der_cert, default_backend())
        info["leaf_present"] = True
        info["tls_version"] = tls_version
        info["cipher"] = cipher[0] if cipher else None
        info["key_size"] = getattr(x509_leaf.public_key(), "key_size", None)
        try:
            info["subject"] = dict(x[0] for x in cert_struct.get("subject", []))
            info["issuer"] = dict(x[0] for x in cert_struct.get("issuer", []))
        except Exception:
            info["subject"] = {}
            info["issuer"] = {}
        info["serialNumber"] = cert_struct.get("serialNumber")
        info["version"] = cert_struct.get("version")
        try:
            info["notBefore"] = _fmt_dt(cert_struct.get("notBefore"))
            info["notAfter"] = _fmt_dt(cert_struct.get("notAfter"))
        except Exception:
            try:
                # try cryptography properties (fallback)
                if hasattr(x509_leaf, "not_valid_before_utc"):
                    info["notBefore"] = _fmt_dt(x509_leaf.not_valid_before_utc)
                else:
                    info["notBefore"] = _fmt_dt(x509_leaf.not_valid_before)
                if hasattr(x509_leaf, "not_valid_after_utc"):
                    info["notAfter"] = _fmt_dt(x509_leaf.not_valid_after_utc)
                else:
                    info["notAfter"] = _fmt_dt(x509_leaf.not_valid_after)
            except Exception:
                pass
        try:
            info["subjectAltName"] = [name for _, name in cert_struct.get("subjectAltName", [])] if cert_struct.get("subjectAltName") else []
        except Exception:
            info["subjectAltName"] = []
        try:
            info["signature_algorithm"] = x509_leaf.signature_hash_algorithm.name
        except Exception:
            info["signature_algorithm"] = None
        try:
            info["leaf_pem"] = x509_leaf.public_bytes(encoding=serialization.Encoding.PEM).decode("utf-8")
        except Exception:
            pass
    except Exception as e:
        info["chain_error"] = f"leaf-fetch-failed: {e}"
        return info

    # Now fetch chain using openssl CLI (preferred)
    try:
        certs, raw_out, verify_code, verify_text = _fetch_chain_with_openssl_cli(hostname, port, timeout=openssl_timeout)
        info["openssl_verify_code"] = verify_code
        info["openssl_verify_text"] = verify_text
        if certs:
            info["chain"] = [_x509_to_dict(c) for c in certs]
            info["chain_method"] = "openssl-cli"
        else:
            # nothing parsed from openssl output; include leaf only
            info["chain"] = [_x509_to_dict(x509_leaf)]
            info["chain_error"] = info.get("chain_error") or "openssl-returned-no-certs"
            info["chain_method"] = "leaf-only"
    except FileNotFoundError as e:
        # openssl missing: keep leaf-only but give clear error
        info["chain"] = [_x509_to_dict(x509_leaf)]
        info["chain_method"] = "leaf-only"
        prev = info.get("chain_error")
        info["chain_error"] = (prev + "; " if prev else "") + f"openssl-not-found: {e}"
    except RuntimeError as e:
        # runtime problems such as parsing or timeout: include message and leaf-only fallback
        info["chain"] = [_x509_to_dict(x509_leaf)]
        info["chain_method"] = "leaf-only"
        prev = info.get("chain_error")
        info["chain_error"] = (prev + "; " if prev else "") + f"openssl-failed: {e}"
    except Exception as e:
        info["chain"] = [_x509_to_dict(x509_leaf)]
        info["chain_method"] = "leaf-only"
        prev = info.get("chain_error")
        info["chain_error"] = (prev + "; " if prev else "") + f"openssl-failed-unexpected: {e}"

    return info


def save_ssl_info(hostname, filename="ssl.json"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    info = get_ssl_info(hostname)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4)
    return file_path


if __name__ == "__main__":
    # simple local test
    target = "accounts.google.com"
    out_path = save_ssl_info(target, "ssl_test.json")
    print("Wrote:", out_path)
