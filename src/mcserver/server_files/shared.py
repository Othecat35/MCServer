import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def update_file(file_path: Path, file_data: bytes):
    temporary_file = Path(str(file_path) + ".tmp")
    logger.debug(f"Writing into '{temporary_file}'")
    temporary_file.write_bytes(file_data)
    logger.debug(f"Replacing '{temporary_file}' with '{file_path}'")
    temporary_file.replace(file_path)
