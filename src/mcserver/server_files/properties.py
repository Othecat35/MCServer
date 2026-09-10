# Imports
from typing import TypedDict


# TypedDicts
class ParsedProperties(TypedDict):
    comments: list[str]
    data: dict[str, str]


# Functions
def loads(properties_data: str) -> ParsedProperties:
    parsed_properties: ParsedProperties = {"comments": [], "data": {}}

    for line in properties_data.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("#"):
            parsed_properties["comments"].append(line.strip()[1:])

        if not "=" in line:
            continue

        key, value = line.split("=", 1)
        parsed_properties["data"][key.strip()] = value.replace("\:", r":")

    return parsed_properties


# Dump only support comments that are on top of the file
def dumps(parsed_properties: ParsedProperties) -> str:
    properties_data: list[str] = []
    for comment in parsed_properties["comments"]:
        lines.append(f"#{comment}")

    for key, value in parsed_properties["data"].items():
        lines.append(f"{key}={value.replace(':', r'\:')}")

    return "\n".join(lines)
