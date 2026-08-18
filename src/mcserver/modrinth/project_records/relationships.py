# Imports
# Standard
import json
import logging as log
from typing import TypedDict

# MCServer
from .shared import project_records_dir
from .shared import DependencyTypes

# Types
dependency_types: list[str] = ["embedded", "optional", "required", "incompatible"]


# TypedDicts
class ProjectRelationships(TypedDict):
    dependencies: dict[str, DependencyTypes]
    dependents: dict[str, DependencyTypes]


# Functions
def create(
    project_id: str,
    dependencies: dict[str, DependencyTypes] | None = None,
    dependents: dict[str, DependencyTypes] | None = None,
) -> None:
    """Create a new project relationships record

    Args:
        project_id: The Modrinth project ID
        dependencies: List of dependencies and its type
        dependents: List of dependents and its type

    Raises:
        FileNotFoundError: When project_records_dir does not exist
        FileExistError: When project already have a record

    Returns:
        None
    """
    if dependencies is None:
        dependencies = {}

    if dependents is None:
        dependents = {}

    if not project_records_dir.exists():
        raise FileNotFoundError(f"Directory '{project_records_dir}' does not exist")

    project_record_dir = project_records_dir / project_id
    relationships_file = project_record_dir / "relationships.json"
    if relationships_file.exists():
        raise FileExistsError(
            f"Relationships for project ID '{project_id}' already exists"
        )

    project_relationships: ProjectRelationships = {"dependencies": {}, "dependents": {}}
    for dependency_id, dependency_type in dependencies.items():
        if dependency_type not in dependency_types:
            log.error(
                f"Invalid dependency type '{dependency_type}' for dependency ID '{dependency_id}' of project ID '{project_id}', ignoring..."
            )
            continue

        project_relationships["dependencies"][dependency_id] = dependency_type

    for dependent_id, dependency_type in dependents.items():
        if dependency_type not in dependency_types:
            log.error(
                f"Invalid dependency type '{dependency_type}' for dependent ID '{dependent_id}' of project ID '{project_id}', ignoring..."
            )
            continue

        project_relationships["dependents"][dependent_id] = dependency_type

    relationships_data = json.dumps(project_relationships, indent=2)
    relationships_file.write_text(relationships_data)


def read(project_id: str) -> ProjectRelationships:
    """Read a project's relationships record

    Args:
        project_id: The Modrinth project ID

    Raises:
        FileNotFoundError: Project has no relationships record or project_records_dir does not exist
        json.JSONDecodeError: Project relationships record file is corrupted

    Returns:
        List of dependencies and dependents of the project
    """
    if not project_records_dir.exists():
        raise FileNotFoundError(f"Directory '{project_records_dir}' does not exist")

    project_record_dir = project_records_dir / project_id
    relationships_file = project_record_dir / "relationships.json"
    project_relationships: ProjectRelationships = {"dependencies": {}, "dependents": {}}

    if not relationships_file.exists():
        raise FileNotFoundError(
            f"Relationships file for project ID '{project_id}' does not exist"
        )

    relationships_data = relationships_file.read_text()
    relationships_json: ProjectRelationships = {"dependencies": {}, "dependents": {}}

    try:
        relationships_json = json.loads(relationships_data)
    except json.JSONDecodeError as error:
        raise error

    dependencies = relationships_json["dependencies"]
    dependents = relationships_json["dependents"]

    for dependency_id, dependency_type in dependencies.items():
        if dependency_type not in dependency_types:
            log.error(
                f"Invalid type '{dependency_type}' for dependency ID '{dependency_id}' of project ID '{project_id}', ignoring..."
            )
            continue

        project_relationships["dependencies"][dependency_id] = dependency_type

    for dependent_id, dependent_type in dependents.items():
        if dependent_type not in dependency_types:
            log.error(
                f"Invalid type '{dependent_type}' for dependent ID '{dependent_id}' of project ID '{project_id}', ignoring..."
            )
            continue

        project_relationships["dependents"][dependent_id] = dependent_type

    return project_relationships


def update(
    project_id: str,
    new_dependencies: dict[str, DependencyTypes] | None = None,
    new_dependents: dict[str, DependencyTypes] | None = None,
) -> None:
    """Update an existing project relationships record

    Args:
        project_id: The Modrinth project ID
        new_dependencies: New dependencies relationships data
        new_dependents: New dependents relationships data

    Raises:
        FileNotFoundError: Project has no relationships record or project_records_dir does not exist
        json.JSONDecodeError: Project relationships record file is corrupted
    """
    if new_dependencies is None:
        new_dependencies = {}

    if new_dependents is None:
        new_dependents = {}

    if not project_records_dir.exists():
        raise FileNotFoundError(f"Directory '{project_records_dir}' does not exist")

    project_record_dir = project_records_dir / project_id
    relationships_file = project_record_dir / "relationships.json"
    if not relationships_file.exists():
        raise FileNotFoundError(
            f"Relationships file for project ID '{project_id}' does not exist"
        )

    project_relationships: ProjectRelationships = {"dependencies": {}, "dependents": {}}
    relationships_data = relationships_file.read_text()

    try:
        relationships_json = json.loads(relationships_data)
    except json.JSONDecodeError as error:
        raise error

    project_relationships.update(relationships_json)
    relationships_data = json.dumps(project_relationships, indent=2)
    relationships_file.write_text(relationships_data)


def delete(project_id: str):
    """ "Delete a project's relationships record

    Args:
        project_id: The Modrinth project ID

    Raises:
        FileNotFoundError: Project has no relationships record or project_records_dir does not exist
    """
    if not project_records_dir.exists():
        raise FileNotFoundError(
            f"Relationships file for project ID '{project_id}' does not exist"
        )

    project_record_dir = project_records_dir / project_id
    relationships_file = project_record_dir / "relationships.json"
    if not relationships_file.exists():
        raise FileNotFoundError(
            f"Relationships file for project ID '{project_id}' does not exist"
        )

    relationships_file.unlink()
