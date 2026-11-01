from urllib.parse import urlsplit


def validate_url(url: str) -> dict:
    if not isinstance(url, str) or not url.strip():
        return {"valid": False, "reason": "URL cannot be empty"}

    url = url.strip()

    if len(url) > 2048:
        return {"valid": False, "reason": "URL is too long"}

    if any(ord(char) < 33 or ord(char) == 127 for char in url):
        return {"valid": False, "reason": "URL contains invalid characters"}

    try:
        parsed = urlsplit(url)

        if parsed.scheme.lower() not in ("http", "https"):
            return {"valid": False, "reason": "Unsupported URL scheme"}

        if not parsed.netloc or not parsed.hostname:
            return {"valid": False, "reason": "Invalid hostname"}

        if parsed.username is not None or parsed.password is not None:
            return {"valid": False, "reason": "Credentials in URL are not allowed"}

        if parsed.hostname.endswith("."):
            return {"valid": False, "reason": "Hostname must not end with a dot"}

        import ipaddress

        try:
            ipaddress.ip_address(parsed.hostname)
            if not is_public_ip(parsed.hostname):
                return {
                    "valid": False,
                    "reason": "Private or non-public IP addresses are blocked"
                }
        except ValueError:
            pass

        port = parsed.port

        return {
            "valid": True,
            "reason": "URL format accepted",
            "scheme": parsed.scheme.lower(),
            "hostname": parsed.hostname,
            "port": port
        }

    except ValueError:
        return {"valid": False, "reason": "Malformed URL"}

import ipaddress


def is_public_ip(ip_address: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_address)
        return ip.is_global
    except ValueError:
        return False


def validate_url_with_dns(url: str) -> dict:
    from app.services.dns_checker import check_dns_security

    result = validate_url(url)

    if not result["valid"]:
        return result

    from app.services.hostname_checker import check_hostname_security

    from app.services.ip_obfuscation_checker import check_ip_obfuscation

    from app.services.unicode_checker import check_unicode_hostname

    unicode_result = check_unicode_hostname(result["hostname"])

    if not unicode_result["safe"]:
        return {
            "valid": False,
            "reason": unicode_result["reason"]
        }

    obfuscation_result = check_ip_obfuscation(result["hostname"])

    if not obfuscation_result["safe"]:
        return {
            "valid": False,
            "reason": obfuscation_result["reason"]
        }

    hostname_result = check_hostname_security(result["hostname"])

    if not hostname_result["safe"]:
        return {
            "valid": False,
            "reason": hostname_result["reason"]
        }

    dns_result = check_dns_security(result["hostname"])

    if not dns_result["safe"]:
        return {
            "valid": False,
            "reason": dns_result["reason"],
            "resolved_ips": dns_result.get("resolved_ips", [])
        }

    return {
        **result,
        "dns_verified": True,
        "resolved_ips": dns_result["resolved_ips"]
    }
