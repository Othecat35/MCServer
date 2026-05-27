# Variables
__version__ = "1.13.10"
special_plural = {
  "is": "are",
  "this": "these"
}

# Functions
def pluralize(singular: str, count: int = 0, plural: str = ""):
  if count != 1:
    if plural:
      return plural

    if singular in special_plural:
      return special_plural[singular]

    if singular.endswith(("ch", "sh", "x", "s", "o")):
      return f"{singular}es"
    elif singular.endswith("y") and singular[-2] not in "aeiou":
      return f"{singular[:-1]}ies"
    else:
      return f"{singular}s"

  return singular