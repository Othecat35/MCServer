#Imports
# Standard
import json
import logging as log
from typing import Literal, TypeAlias, TypedDict

# MCServer
from .shared import project_records_dir

#Types
dependency_types: tuple[str, str, str, str] = ("embedded", "optional", "required", "incompatible")
DependencyTypes: TypeAlias = Literal["embedded", "optional", "required", "incompatible"]

#TypedDicts
class ProjectRelationships(TypedDict):
    dependencies: dict[str, DependencyTypes]
    dependents: dict[str, DependencyTypes]

#Functions
def create(project_id: str, dependencies: dict[str, DependencyTypes] | None = None, dependents: dict[str, DependencyTypes] | None = None) -> ProjectRelationships:
    if dependencies is None:
        dependencies = {}

    if dependents is None:
        dependents = {}

    project_record_dir = project_records_dir / project_id
    relationships_file = project_record_dir / "relationships.json"
    project_relationships: ProjectRelationships = {
        "dependencies": {},
        "dependents": {}
    }

    for dependency_id, dependency_type in dependencies.items():
        if dependency_type not in dependency_types:
            log.error(f"Invalid dependency type '{dependency_type}' for dependency ID '{dependency_id}' of project ID '{project_id}'")
            continue

        project_relationships["dependencies"][dependency_id] = dependency_type

    for dependent_id, dependent_type in dependents.items():
        if dependent_type not in dependency_types:
            log.error(f"Invalid dependency type '{dependent_type}' for dependent ID '{dependent_id}' of project ID '{project_id}'")
            continue

        project_relationships["dependents"][dependent_id] = dependent_type

    if relationships_file.exists():
        log.error(f"Relationships for project ID '{project_id}' already exists")
        return project_relationships

    project_record_dir.mkdir(parents=True)
    relationships_data = json.dumps(project_relationships, indent=2)
    relationships_file.write_text(relationships_data)
    return project_relationships

def read(project_id: str) -> ProjectRelationships:
    project_record_dir = project_records_dir / project_id
    relationships_file = project_record_dir / "relationships.json"
    project_relationships: ProjectRelationships = {
        "dependencies": {},
        "dependents": {}
    }

    if not relationships_file.exists():
        log.error(f"Relationships file for project ID '{project_id}' does not exist")
        return project_relationships

    relationships_data = relationships_file.read_text()
    relationships_json: ProjectRelationships = {
        "dependencies": {},
        "dependents": {}
    }

    try:
        relationships_json = json.loads(relationships_data)
    except json.JSONDecodeError as error:
        log.error(f"Error parsing relationships file for project ID '{project_id}': {error.msg} at line {error.colno} column {error.colno}")
        return project_relationships

    dependencies = relationships_json["dependencies"]
    dependents = relationships_json["dependents"]

    for dependency_id, dependency_type in dependencies.items():
        if dependency_type not in dependency_types:
            log.error(f"Invalid type '{dependency_type}' for dependency ID '{dependency_id}' of project ID '{project_id}'")
            continue

        project_relationships["dependencies"][dependency_id] = dependency_type

    for dependent_id, dependent_type in dependents.items():
        if dependent_type not in dependency_types:
            log.error(f"Invalid type '{dependent_type}' for dependent ID '{dependent_id}' of project ID '{project_id}'")
            continue

        project_relationships["dependents"][dependent_id] = dependent_type

    return project_relationships

def update(project_id: str, new_dependencies: dict[str, DependencyTypes] | None = None, new_dependents: dict[str, DependencyTypes] | None = None) -> ProjectRelationships:
    if new_dependencies is None:
        new_dependencies = {}

    if new_dependents is None:
        new_dependents = {}

    project_record_dir = project_records_dir / project_id
    relationships_file = project_record_dir / "relationships.json"
    if not relationships_file.exists():
        log.error(f"Relationships file for project ID '{project_id}' does not exist")

    project_relationships: ProjectRelationships = {
        "dependencies": {},
        "dependents": {}
    }



    return project_relationships