#Modules
# Standard
import json
import logging as log
from pathlib import Path
from typing import Literal, TypedDict

#Paths
banned_ips_file = Path("banned-ips.json")

#TypedDicts
class BannedIPEntry(TypedDict):
    ip: str | Literal["<unknown>"]    # IPv4 or IPv6
    created: str                      # Time format: yyyy-MM-dd HH:mm:ss Z
    source: str
    expires: Literal["forever"] | str # Time Format:  yyyy-MM-dd HH:mm:ss Z
    reason: str

class BannedIPRecord(TypedDict):
    ip_address: str                        # IPv4 or IPv6
    created_time: str                 # Time format: yyyy-MM-dd HH:mm:ss Z
    ban_source: str
    expires_time: str | Literal["forever"] # Time format: yyyy-MM-dd HH:mm:ss Z
    ban_reason: str

#Functions
# Add IPs
def add_ip(ip_address: str, created_time: str, ban_source: str, expires_time: str | Literal["forever"] = "forever", ban_reason: str = "Banned via MCServer.") -> None:
    banned_ip_record: BannedIPRecord = {
        "ip_address": ip_address,
        "created_time": created_time,
        "ban_source": ban_source,
        "expires_time": expires_time,
        "ban_reason": ban_reason
    }

    add_ips(banned_ip_record)

def add_ips(banned_ip_records: list[BannedIPRecord] | BannedIPRecord) -> None:
    if not isinstance(banned_ip_records, list):
        banned_ip_records = [banned_ip_records]

    with open(banned_ips_file, mode="r+") as file:
        banned_ips_data = json.load(file)
        for ip_record in banned_ip_records:
            banned_ip_entry: BannedIPEntry = {
                "ip": ip_record["ip_address"],
                "created": ip_record["created_time"],
                "source": ip_record["ban_source"],
                "expires": ip_record["expires_time"],
                "reason": ip_record["ban_reason"]
            }

            banned_ips_data.append(banned_ip_entry)

        file.seek(0)
        json.dump(banned_ips_data, file, indent=2)
        file.truncate()

# Remove IPs
def remove_ip(ip_address: str) -> None:
    remove_ips(ip_address)

def remove_ips(ip_addresses: list[str] | str) -> None:
    if not isinstance(ip_addresses, list):
        ip_addresses = [ip_addresses]

    unbanned_ip_addresses: set[str] = set()
    for ip_address in ip_addresses:
        unbanned_ip_addresses.add(ip_address)

    with open(banned_ips_file, mode="r+") as file:
        banned_ips_data: list[BannedIPEntry] = json.load(file)
        new_banned_ips_data: list[BannedIPEntry] = []
        for ip_entry in banned_ips_data:
            ip_address = ip_entry["ip"]
            if ip_address in unbanned_ip_addresses:
                log.debug(f"Removed IP address '{ip_address}' from the banned IP address list")
                continue

            new_banned_ips_data.append(ip_entry)

        file.seek(0)
        json.dump(new_banned_ips_data, file, indent=2)
        file.truncate()

# TODO: add 'update_ip' and 'update_ips', just use plain dict.update() because it has no depth

# List IPs
def list_ips() -> list[BannedIPRecord]:
    banned_ip_data: list[BannedIPEntry] = json.loads(banned_ips_file.read_text())
    banned_ip_records: list[BannedIPRecord] = []
    for ip_entry in banned_ip_data:
        banned_ip_record: BannedIPRecord = {
            "ip_address": ip_entry["ip"],
            "created_time": ip_entry["created"],
            "ban_source": ip_entry["source"],
            "expires_time": ip_entry["expires"],
            "ban_reason": ip_entry["reason"]
        }

        banned_ip_records.append(banned_ip_record)

    return banned_ip_records
