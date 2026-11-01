import ipaddress
import socket


def check_dns_security(hostname: str) -> dict:
    if not hostname or not isinstance(hostname, str):
        return {
            "safe": False,
            "reason": "Invalid hostname"
        }

    try:
        results = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM
        )

        resolved_ips = sorted({
            result[4][0] for result in results
        })

        if not resolved_ips:
            return {
                "safe": False,
                "reason": "No IP addresses resolved"
            }

        for address in resolved_ips:
            ip = ipaddress.ip_address(address)

            if not ip.is_global:
                return {
                    "safe": False,
                    "reason": "DNS resolves to a non-public IP",
                    "resolved_ips": resolved_ips
                }

        return {
            "safe": True,
            "reason": "All resolved IPs are public",
            "resolved_ips": resolved_ips
        }

    except (socket.gaierror, OSError, ValueError):
        return {
            "safe": False,
            "reason": "DNS resolution failed"
        }
