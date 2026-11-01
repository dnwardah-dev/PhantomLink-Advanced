import ipaddress
import re


def check_ip_obfuscation(hostname: str) -> dict:
    if not isinstance(hostname, str) or not hostname:
        return {"safe": False, "reason": "Invalid hostname"}

    host = hostname.lower().rstrip(".")

    try:
        ip = ipaddress.ip_address(host)
        return {
            "safe": ip.is_global,
            "reason": "Public IP" if ip.is_global else "Non-public IP blocked"
        }
    except ValueError:
        pass

    # Reject hexadecimal/octal-like IPv4 representations
    parts = host.split(".")

    if any(part.startswith("0x") for part in parts):
        return {"safe": False, "reason": "Hexadecimal IP representation blocked"}

    if re.fullmatch(r"[0-9.]+", host):
        return {"safe": False, "reason": "Ambiguous numeric hostname blocked"}

    return {
        "safe": True,
        "reason": "No obvious IP obfuscation detected"
    }
