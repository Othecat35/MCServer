import json
from typing import NotRequired, TypedDict

from .paths import modrinth_dir
from .typings import DependencyType, Environment, FileHashes

project_records_dir = modrinth_dir / "project_records"


current_format_version = 1


class ProjectRecordFile(TypedDict):
    file_hashes: FileHashes
    file_name: str


class ProjectRecordData(TypedDict):
    format_version: int

    # Version (Following the project_version typings)
    version_id: str
    version_name: NotRequired[str]
    version_environment: Environment

    # Metadata
    added_time: str  # probably ISO-8601
    file: ProjectRecordFile

    # Relationships
    is_manual: bool
    highest_type: DependencyType
    dependencies: dict[str, DependencyType]
    dependents: dict[str, DependencyType]


def write_record(project_id: str, record_data: ProjectRecordData) -> None:
    """Write a record for a project record (create a new record or overwrite it)
    Args:
        project_id: The id of the Modrinth project
        record_data: The data of the project

    Raises:
        FileNotFoundError: Path to `project_records_dir` does not exist
        NotADirectoryError: Path to `project_record_dir` is not a directory
    """
    if not project_records_dir.exists():
        raise FileNotFoundError(
            f"Failed to create a project record for '{project_id}': Directory {project_records_dir} does not exist"
        )

    if not project_records_dir.is_dir():
        raise NotADirectoryError(
            f"Failed to create a project record for '{project_id}': Path {project_records_dir} is not a directory."
        )

    project_record_file = project_records_dir / f"{project_id}.json"
    record_json = json.dumps(record_data)
    project_record_file.write_text(record_json)


def read_record(project_id: str) -> ProjectRecordData:
    """Read a project record data
    Args:
        project_id: The ID of the Modrinth project

    Raises:
        FileNotFoundError: The record file for the project does not exist

    Returns:
        ThData of the project record
    """
    project_record_file = project_records_dir / f"{project_id}.json"
    if not project_record_file.exists():
        raise FileNotFoundError(
            f"Failed to read record data for project ID '{project_id}': File {project_record_file} does not exist"
        )

    record_json = project_record_file.read_text()
    record_data: ProjectRecordData = json.loads(record_json)
    return record_data


def delete_record(project_id: str):
    """Delete the record file for the project
    Args:
        project_id: The ID of the Modrinth project

    Raises:
        FileNotFoundError: The record file for the project does not exist
    """
    project_record_file = project_records_dir / f"{project_id}.json"
    if not project_record_file.exists():
        return

    project_record_file.unlink()
