import logging
from argparse import Namespace

from .. import config, shared
from ..modrinth import project_records
from ..shared import get_loader_context

logger = logging.getLogger(__name__)

def run(args: Namespace) -> int:
    if not config.config_exists("server"):
        logger.error("Configuration for 'server' does not exist")
        return 1

    server_config = config.read_config("server", shared.default_configs["server"]["format_version"])
    project_label, _ = get_loader_context(server_config["loader"]["name"])

    project_list: list[str] = []
    for project_record_file in project_records.project_records_dir.iterdir():
        project_record = project_records.read_record(project_record_file.stem)
        project_list.append(f"{project_record['project_name']} ({project_record['project_slug']})")

    if len(project_list) == 0:
        logger.info(f"There's no {project_label} installed")
        return 1

    logger.info(f"List of {project_label} added:")
    print("\n".join(project_list))
    return 0
