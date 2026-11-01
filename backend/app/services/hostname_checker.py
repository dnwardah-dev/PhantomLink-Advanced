import ipaddress


def check_hostname_security(hostname: str) -> dict:
    if not isinstance(hostname, str) or not hostname:
        return {"safe": False, "reason": "Invalid hostname"}

    hostname = hostname.lower().rstrip(".")

    blocked_names = {"localhost", "localhost.localdomain"}

    blocked_suffixes = (
        ".localhost",
        ".local",
        ".internal",
        ".test",
        ".invalid",
        ".home.arpa",
    )

    if hostname in blocked_names or hostname.endswith(blocked_suffixes):
        return {
            "safe": False,
            "reason": "Local or reserved hostname is blocked"
        }

    try:
        ip = ipaddress.ip_address(hostname)

        if not ip.is_global:
            return {
                "safe": False,
                "reason": "Non-public IP address is blocked"
            }

    except ValueError:
        pass

    return {
        "safe": True,
        "reason": "Hostname passed initial security checks"
    }
