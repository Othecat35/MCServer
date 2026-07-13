#Functions
def loads(string: str) -> dict[str, str]:
    parsed_properties: dict[str, str] = {}
    for line in string.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("#"): #Ignore line that starts with hashtag, comment after a text is not detected for now
            continue

        if not "=" in line:
            continue

        key, value = line.split("=", 1)
        parsed_properties[key.strip()] = value.strip()

    return parsed_properties

def dumps(parsed_object: dict[str, str]) -> str:
    lines: list[str] = []

    for key, value in parsed_object.items():
        lines.append(f"{key}={value}")

    return "\n".join(lines)

print(loads("""#hello, there
a=bcd
b=jhsashjka
"""))