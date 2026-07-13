#Modules
# Standard
from pathlib import Path
from typing import Literal, TypedDict

#Paths
banned_ips_file = Path("banned-ips.json")

#TypedDicts
class BannedIPEntry(TypedDict):
    ip: str      # IPv4 or IPv6
    created: str # yyyy-MM-dd HH:mm:ss Z
    source: str
    expires: str # "forever" or yyyy-MM-dd HH:mm:ss Z
    reason: str

class BannedIP(TypedDict):
    ip_address: str                        #IPv4 or IPv6
    created_time: str                      #Time format: yyyy-MM-dd HH:mm:ss Z
    ban_source: str
    expires_time: Literal["forever"] | str #Time format: yyyy-MM-dd HH:mm:ss Z
    ban_reason: str