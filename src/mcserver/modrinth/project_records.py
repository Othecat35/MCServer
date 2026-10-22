import json
from typing import NotRequired, TypedDict

from .paths import modrinth_dir
from .shared import DependencyType, ProjectEnvironment, ProjectLicense, VersionFile

project_records_dir = modrinth_dir / "project_records"

# Wait, what data a record actually store?
# For now it is whatever the get_project_version returns


class ProjectRecordData(TypedDict):
    # Project
    project_name: str
    """The title or name of the project"""
    project_slug: str
    """"""
    short_description: str
    """A short sentence summarizing the project, no more than a sentence or two."""
    categories: list[str]
    """A list of the featured categories that the project has."""
    additional_categories: list[str]
    """A list of additional categories that the project also has. These are supplementary to the featured categories, and does not include them again."""
    project_license: ProjectLicense
    published_time: str

    # Version
    version_id: str
    version_name: str
    version_number: NotRequired[str]
    project_environment: ProjectEnvironment
    """All the environments that versions of this project support. Not in any particular order, we recommend using the environment information on a version instead. For an explanation of each environment, see the blog post here: https://modrinth.com/news/article/new-environments/#new-system"""

    # Metadata
    added_time: str  # probably ISO-8601
    file: VersionFile

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

    record_data: ProjectRecordData = {}
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
