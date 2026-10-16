import json
from typing import NotRequired, TypedDict
from .shared import project_records_dir, DependencyType, ProjectEnvironment, VersionFile

# Wait, what data a record actually store?
# For now it is whatever the get_project_version returns


class ProjectRecordData(TypedDict):
    version_number: NotRequired[str]
    version_id: str
    project_id: str
    added_time: str  # probably ISO-8601
    project_environment: ProjectEnvironment
    file: VersionFile
    dependencies: dict[str, DependencyType]
    dependents: dict[str, DependencyType]


def create_record(project_id: str, record_data: ProjectRecordData):
    project_record_file = project_records_dir / f"{project_id}.json"
    if project_record_file.exists():
        raise FileExistsError(f"{project_record_file} already exists")


def read_record(project_id: str) -> ProjectRecordData:
    project_record_file = project_records_dir / f"{project_id}.json"
    record_data: ProjectRecordData = {}
    return record_data


def update_record(project_id: str, new_record_data) -> ProjectRecordData:
    project_record_file = project_records_dir / f"{project_id}.json"
    record_data: ProjectRecordData = {}
    return record_data


def delete_record(project_id: str):
    project_record_file = project_records_dir / f"{project_id}.json"
    project_record_file.unlink()
