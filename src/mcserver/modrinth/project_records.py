import json
from typing import NotRequired, TypedDict

from ..shared import update_file
from .paths import modrinth_dir
from .typings import DependencyType, Environment, File

project_records_dir = modrinth_dir / "project_records"
current_format_version = 1


class ProjectRecordFormatVersionError(Exception):
    pass


class ProjectRecordPayload(TypedDict):
    # Project
    project_name: str
    project_slug: str | None

    # Version
    version_id: str | None
    version_environment: Environment | None
    file: File | None

    # Metadata
    added_time: str | None # probably ISO-8601
    discovered_time: str # probably ISO-8601
    updated_time: str | None # probably ISO-8601

    # Relationships
    is_manual: bool
    highest_type: DependencyType | None
    dependencies: dict[str, int]
    dependents: dict[str, int]


class ProjectRecordData(ProjectRecordPayload):
    format_version: int


def record_exists(project_id: str) -> bool:
    return (project_records_dir / f"{project_id}.json").exists()


def write_record(project_id: str, record_payload: ProjectRecordPayload) -> None:
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
    record_data: ProjectRecordData = {
        **record_payload,
        "format_version": current_format_version,
    }

    record_json = json.dumps(record_data, indent=2)
    update_file(project_record_file, record_json.encode())


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

    if record_data["format_version"] > current_format_version:
        raise ProjectRecordFormatVersionError(
            f"Format version of a record for project '{project_id}' is higher than this version of MCServer"
        )

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
