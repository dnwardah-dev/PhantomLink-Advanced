import re


def check_unicode_hostname(hostname: str) -> dict:
    if not isinstance(hostname, str) or not hostname:
        return {"safe": False, "reason": "Invalid hostname"}

    if hostname != hostname.strip():
        return {"safe": False, "reason": "Hostname contains surrounding whitespace"}

    try:
        hostname.encode("ascii")
    except UnicodeEncodeError:
        return {
            "safe": False,
            "reason": "Unicode hostname requires additional verification"
        }

    host = hostname.lower().rstrip(".")

    if not host or len(host) > 253:
        return {"safe": False, "reason": "Invalid hostname length"}

    if host.startswith("xn--") or ".xn--" in host:
        return {
            "safe": False,
            "reason": "Punycode hostname requires additional verification"
        }

    if re.search(r"[^a-z0-9.\-:\[\]]", host):
        return {
            "safe": False,
            "reason": "Unsupported hostname characters"
        }

    return {
        "safe": True,
        "reason": "Hostname passed initial Unicode checks"
    }
