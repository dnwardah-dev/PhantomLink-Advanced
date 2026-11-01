import ipaddress
import dns.resolver
import dns.exception

from app.services.url_validator import validate_url
from urllib.parse import urlsplit


def inspect_dns(raw_url: str) -> dict:
    """
    Inspect A and AAAA DNS records without connecting
    to the target website.
    """
    url = validate_url(raw_url)
    hostname = urlsplit(url).hostname

    result = {
        "hostname": hostname,
        "analysis_type": "dns_lookup",
        "status": "unknown",
        "ipv4": [],
        "ipv6": [],
        "blocked_addresses": [],
        "errors": [],
    }

    resolver = dns.resolver.Resolver()
    resolver.timeout = 2
    resolver.lifetime = 4

    for record_type, target in (
        ("A", "ipv4"),
        ("AAAA", "ipv6"),
    ):
        try:
            answers = resolver.resolve(
                hostname,
                record_type,
                search=False,
            )

            for answer in answers:
                address = str(answer)
                ip = ipaddress.ip_address(address)

                if ip.is_global:
                    result[target].append(address)
                else:
                    result["blocked_addresses"].append({
                        "address": address,
                        "record_type": record_type,
                        "reason": "Non-global IP address",
                    })

        except dns.resolver.NoAnswer:
            continue

        except dns.resolver.NXDOMAIN:
            result["errors"].append("Domain does not exist.")
            break

        except dns.exception.Timeout:
            result["errors"].append(
                f"{record_type} DNS lookup timed out."
            )

        except dns.exception.DNSException as exc:
            result["errors"].append(
                f"{record_type} lookup failed: {type(exc).__name__}"
            )

    result["ipv4"] = sorted(set(result["ipv4"]))
    result["ipv6"] = sorted(set(result["ipv6"]))

    if result["blocked_addresses"]:
        result["status"] = "non_public_address_detected"
    elif result["ipv4"] or result["ipv6"]:
        result["status"] = "resolved"
    elif result["errors"]:
        result["status"] = "lookup_failed"
    else:
        result["status"] = "no_address_records"

    return result
