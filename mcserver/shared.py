from constants import iec_prefixes, si_prefixes

# Variables
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

def format_number(number: str | float, unit_type: str = "si"):
  number = float(number)
  unit_multiples = 0
  prefixes = []

  if unit_type == "si":
    unit_multiples = 1_000
    prefixes = si_prefixes
  elif unit_type == "iec":
    unit_multiples = 1_024
    prefixes = iec_prefixes
  else:
    raise ValueError(f"'{unit_type}' is not a valid number unit type")

  iteration = 0
  while number >= unit_multiples:
    if iteration >= len(prefixes) - 1:
      break

    number /= unit_multiples
    iteration += 1

  return f"{round(number, 2):g}{prefixes[iteration]}"

def merge_dict(base: dict, update: dict):
  for key, value in update.items():
    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
      merge_dict(base[key], value)
    else:
      base[key] = value

  return base