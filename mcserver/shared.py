# Modules
import sys

from constants import iec_prefixes, si_prefixes

from pathlib import Path

# Variables
special_plural = {
  "is": "are",
  "this": "these"
}

current_dir: Path = Path.cwd()
mcserver_dir: Path = Path(".mcserver")

color_output_mode = "auto" # 'never', 'auto', 'always'
ansi_codes = {
  "gray": "\033[90m",
  "green": "\033[92m",
  "red": "\033[91m",
  "yellow": "\033[93m",

  "bold": "\033[1m",
  "reset": "\033[0m",

  "clear_line": "\033[K",
  "cursor_up": "\033[A",
  "start_line": "\033[G"
}

isatty = sys.stdout.isatty() and sys.stderr.isatty()
last_status_message = ""

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

def merge_dict(base: dict, update: dict) -> dict:
  for key, value in update.items():
    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
      merge_dict(base[key], value)
    else:
      base[key] = value

  return base

def confirmation_prompt(prompt: str, default_option: bool = False) -> bool:
  accepted_value = "y/n"
  if default_option:
    accepted_value = "Y/n"
  else:
    accepted_value = "y/N"

  try:
    answer = input(f"{prompt} [{accepted_value}]: ")
  except KeyboardInterrupt:
    print() # To avoid weird no newline when Ctrl+C
    return False

  match answer.lower():
    case "y" | "yes":
      return True
    case "n" | "no":
      return False
    case "":
      return default_option
    case _:
      return False

# ANSI
def ansi(name: str):
  match color_output_mode:
    case "always":
      return ansi_codes.get(name, "")
    case "never":
      return ""
    case "auto":
      if isatty:
        return ansi_codes.get(name, "")

      return ""
    case _:
      raise ValueError(f"Invalid string '{color_output_mode}' of variable color_output_mode")

def wrap_ansi(string: str, ansi_name: str):
  return f"{ansi(ansi_name)}{string}{ansi('reset')}"

def mod_environment_color(environment: str, padding: int = 0):
  if environment == "required":
    return wrap_ansi(f"{'Required': <{padding}}", "green")
  elif environment == "optional":
    return wrap_ansi(f"{'Optional': <{padding}}", "yellow")
  elif environment == "unsupported":
    return wrap_ansi(f"{'Unsupported': <{padding}}", "red")
  elif environment == "unknown":
    return wrap_ansi(f"{'Unknown': <{padding}}", "gray")
  return f"{environment: <{padding}}"

def print_status(message: str, dynamic: str | None = None):
  if dynamic is None: dynamic = ""
  global last_status_message

  if dynamic and isatty:
    print(f"{ansi('clear_line')} {dynamic}", end=ansi('start_line'), flush=True)
  else:
    if message != last_status_message:
      print(message, flush=True)

      last_status_message = message
