import json
from typing import NotRequired, TypedDict
from .shared import project_records_dir, DependencyType, ProjectEnvironment, VersionFile

# Wait, what data a record actually store? whatever the get_project_version returns

class ProjectRecordData(TypedDict):
    version_number: NotRequired[str]
    version_id: str
    project_id: str
    project_environment: ProjectEnvironment
    file: VersionFile
    dependencies: dict[str, DependencyType]
    dependents: dict[str, DependencyType]
    # project_name: str
    # version_name: str
    # project_slug: str
    # project_environments: list[ProjectEnvironment]
    # game_versions: 

def create_record(project_id: str, record_data: ProjectRecordData):
    project_record_file = project_records_dir / f"{project_id}.json"

def read_record(project_id: str) -> ProjectRecordData:
    project_record_file = project_records_dir / f"{project_id}.json"
    project_record_data = 
    record_data: ProjectRecordData = {}
    return record_data

def update_record(project_id: str, new_record_data):
    project_record_file = project_records_dir / f"{project_id}.json"

def delete_record(project_id: str):
    project_record_file = project_records_dir / f"{project_id}.json"
    project_record_file.unlink()