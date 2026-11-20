# Modules
# Standard
import logging
import shutil
import sys
import textwrap
from pathlib import Path
from typing import Literal, TypedDict
from warnings import deprecated

# MCServer
from .constants import iec_prefixes, si_prefixes

logger: logging.Logger = logging.getLogger(__name__)

class LoaderContext(TypedDict):
    project_directory: Path | None
    project_label: Literal["project", "mod", "plugin"]

# Variables
mod_loaders: list[str] = ["fabric"]  # , "quilt"]
plugin_loaders: list[str] = ["paper", "purpur"]
loader_list: list[str] = ["vanilla"] + mod_loaders + plugin_loaders

loader_context: LoaderContext = {"project_directory": None, "project_label": "project"}

special_plural: dict[str, str] = {"is": "are", "this": "these"}

color_output_mode: Literal["always", "never", "auto"] = "auto"
ansi_codes: dict[str, str] = {
    "gray": "\x1b[90m",
    "green": "\x1b[92m",
    "red": "\x1b[91m",
    "yellow": "\x1b[93m",
    "bold": "\x1b[1m",
    "reset": "\x1b[0m",
    "clear_line": "\x1b[K",
    "cursor_down": "\x1b[B",
    "cursor_up": "\x1b[A",
    "first_column": "\x1b[G",
}

stdout_istty: bool = sys.stdout.isatty()
isatty: bool = stdout_istty and sys.stderr.isatty()
last_status: str | None = None

default_configs = {
    "launcher": {
        "format_version": 1,
        "config_data": {
            "ram": {
                "_comment": "Memory size in MebiByte (MiB)",
                "min": 512,
                "max": 2_048,
            },
            "jarfile": "Server.jar",
            "is_nogui": True,
        },
    },
    "modrinth": {
        "format_version": 1,
        "config_data": {"search_limit": 20, "sort_index": "relevance"},
    },
    "server": {
        "format_version": 1,
        "config_data": {
            "game_version": "",  # Auto-fetched the latest version when init without --mc-version
            "loader": {"name": "vanilla", "version": None},
        },
    },
}

# Paths
current_dir: Path = Path.cwd()
mcserver_dir: Path = Path(".mcserver")
tempfiles_dir: Path = mcserver_dir / "tempfiles"

mods_dir: Path = Path("mods")
plugins_dir: Path = Path("plugins")


# Functions
def pluralize(singular: str, count: int = 0, plural: str = "") -> str:
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


def format_number(number: float, unit_type: str = "si") -> str:
    is_negative = number < 0
    number = abs(number)
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

    return f"{'-' if is_negative else ''}{round(number, 2):g}{prefixes[iteration]}"


def merge_dict(base: dict, update: dict) -> dict:
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            merge_dict(base[key], value)
        else:
            base[key] = value

    return base


def confirmation_prompt(prompt: str, default_option: bool = False) -> bool:
    accepted_value: str = "y/n"
    if default_option:
        accepted_value: str = "Y/n"
    else:
        accepted_value: str = "y/N"

    try:
        answer: str = input(f"{prompt} [{accepted_value}]: ")
    except KeyboardInterrupt:
        print()  # To avoid weird no newline when Ctrl+C
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


def support_mods(loader_name: str) -> bool:
    return loader_name in mod_loaders or loader_name in plugin_loaders


def get_loader_context(loader_name: str) -> tuple[str, Path | None]:
    if loader_name in mod_loaders:
        return ("mod", mods_dir)
    elif loader_name in plugin_loaders:
        return ("plugin", plugins_dir)
    else:  # Vanilla
        return ("project", None)

@deprecated("Use get_loader_context instead")
def set_loader_context(loader_name: str) -> None:
    global loader_context
    logger.debug("set_loader_context was called!")

    if loader_name in mod_loaders:
        loader_context = {"project_directory": mods_dir, "project_label": "mod"}
    elif loader_name in plugin_loaders:
        loader_context = {"project_directory": plugins_dir, "project_label": "plugin"}


def wrap_string(
    string: str,
    initial_indent: str | int = "",
    subsequent_indent: str | int = "",
    width: int | None = None,
) -> str:
    if isinstance(initial_indent, int):
        initial_indent = " " * initial_indent

    if isinstance(subsequent_indent, int):
        subsequent_indent = " " * subsequent_indent

    terminal_width: int = width or shutil.get_terminal_size().columns
    return "\n".join(
        textwrap.wrap(
            string,
            width=terminal_width,
            initial_indent=initial_indent,
            subsequent_indent=subsequent_indent,
        )
    )


# ANSI
def ansi(name: str, output_to: Literal["stdout", "strderr"] = "stdout") -> str:
    match color_output_mode:
        case "always":
            return ansi_codes.get(name, "")
        case "never":
            return ""
        case "auto":
            if (
                output_to == "stdout"
                and sys.stdout.isatty()
                or output_to == "strderr"
                and sys.stderr.isatty()
            ):
                return ansi_codes.get(name, "")
        case _:
            raise ValueError(
                f"Invalid string '{color_output_mode}' of variable color_output_mode"
            )

    return ""


def wrap_ansi(string: str, ansi_name: str) -> str:
    return f"{ansi(ansi_name)}{string}{ansi('reset')}"


# def mod_environment_color(environment: str, padding: int = 0):
#     if environment == "required":
#         return wrap_ansi(f"{'Required': <{padding}}", "green")
#     elif environment == "optional":
#         return wrap_ansi(f"{'Optional': <{padding}}", "yellow")
#     elif environment == "unsupported":
#         return wrap_ansi(f"{'Unsupported': <{padding}}", "red")
#     elif environment == "unknown":
#         return wrap_ansi(f"{'Unknown': <{padding}}", "gray")
#     return f"{environment: <{padding}}"


def project_environment_name(project_environment: str) -> str:
    project_environments = {
        "client_only": "Client-side only",
        "server_only": "Server-side only",
        "dedicated_server_only": "Dedicated server only",
        "client_and_server": "Client and server",
        "server_only_client_optional": "Optional on client",
        "client_only_server_optional": "Optional on server",
        "client_or_server_prefers_both": "Works best on both",
        "client_or_server": "Works the same on either",
        "singleplayer_only": "Singleplayer only",
    }

    return project_environments.get(project_environment, project_environment)


def update_file(file_path: Path, file_data: bytes) -> None:
    temporary_file = Path(str(file_path) + ".tmp")
    logger.debug(f"Writing into '{temporary_file}'")
    temporary_file.write_bytes(file_data)
    logger.debug(f"Replacing '{temporary_file}' with '{file_path}'")
    temporary_file.replace(file_path)


def print_status(status: str, updating_status: str | None = None) -> None:
    global last_status
    if updating_status is not None and stdout_istty:
        print(
            f"{ansi('first_column')}{ansi('clear_line')}{updating_status}",
            end="",
            flush=True,
        )
    else:
        if status != last_status:
            print(status, end="", flush=True)

    last_status = status


def print_string(string: str) -> None:
    print(f"{ansi('first_column')}{ansi('clear_line')}{string}")
