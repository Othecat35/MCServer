#Modules
# Standard
import json
from pathlib import Path
from typing import Literal, TypedDict

#Paths
banned_ips_file = Path("banned-ips.json")

#TypedDicts
class BannedIPEntry(TypedDict):
    ip: str      # IPv4 or IPv6
    created: str # Time format: yyyy-MM-dd HH:mm:ss Z
    source: str
    expires: Literal["forever"] | str # Time Format:  yyyy-MM-dd HH:mm:ss Z
    reason: str

class BannedIPRecord(TypedDict):
    ip_address: str                        #IPv4 or IPv6
    created_time: str                      #Time format: yyyy-MM-dd HH:mm:ss Z
    ban_source: str
    expires_time: Literal["forever"] | str #Time format: yyyy-MM-dd HH:mm:ss Z
    ban_reason: str

#Functions
def add_ip_record(ip_address: str, created_time: str, ban_source: str, expires_time: Literal["forever"] | str, ban_reason: str) -> None:
    banned_ip_record: BannedIPRecord = {
        "ip_address": ip_address,
        "created_time": created_time,
        "ban_source": ban_source,
        "expires_time": expires_time,
        "ban_reason": ban_reason
    }

    add_ips(banned_ip)

def add_ip_records(banned_ip_records: list[BannedIPRecord] | BannedIPRecord) -> None:
    if not isinstance(banned_ip_records, list):
        banned_ip_records = [banned_ip_records]

    with open(banned_ips_file, mode="r+") as file:
        banned_ip_data = json.load(file)
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

def list_ip_records() -> list[BannedIPRecord]:
    banned_ip_data: list[BannedIPEntry] = json.loads(banned_ips_file.read_text())
    banned_ip_records: list[BannedIPRecord] = []
    for ip_entry in banned_ip_data:
        banned_ip_record: BannedIPRecord = {
            "ip_address": ip_entry["ip"],
            "created_time": ip_entry["created"],
            "ban_source": ip_entry["source"],
            "expires_time": ip_entry["expires"],
            "ban_reason": ip_entry["ban_reason"]
        }

        banned_ip_records.append(banned_ip_record)

    return banned_ip_records
