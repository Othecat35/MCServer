import logging as log
from collections import deque
from collections.abc import Callable
from typing import TypedDict

class Dependency(TypedDict):
    project_id: str
    dependency_type: str

class Project(TypedDict):
    is_manual: bool
    dependencies: dict[str, int]
    dependents: dict[str, int]

class ProjectData(TypedDict):
    project_id: str
    is_manual: bool
    dependencies: list[Dependency]
    dependents: list[Dependency]

dependency_type = {
    "embedded": 0,
    "optional": 1,
    "required": 2,
    "incompatible": 3
}

def test_dependencies(project_id: str) -> dict[str, int]:
    dependencies = {
        "a": {
            "b": 2,
            "c": 2,
            "d": 2
        },
        "b": {
            "c": 2,
            "d": 2
        },
        "c": {
            "e": 2
        },
        "d": {
            "e": 2
        },
        "e": {}
    }

    return dependencies[project_id]

def resolve_dependencies(project_ids: list[str] | str, get_dependencies: Callable) -> list:
    if isinstance(project_ids, str):
        project_ids = [project_ids]

    queued_projects: deque[str] = deque()
    visited_projects: set[str] = set()
    dependency_graph: dict[str, Project] = {}

    for project_id in project_ids:
        log.debug(f"Adding project '{project_id}' to queue")
        queued_projects.append(project_id)
        project: Project = {
            "is_manual": True,
            "dependencies": {},
            "dependents": {}
        }

        dependency_graph[project_id] = project

    while queued_projects:
        project_id = queued_projects.popleft()
        if project_id in visited_projects:
            log.debug(f"Project '{project_id}' has already been visited")
            continue

        dependencies = get_dependencies(project_id)
        dependency_graph[project_id]["dependencies"] = dependencies

        for dependency_id, dependency_type in dependencies.items():
            if dependency_id in visited_projects:
                dependency_graph[dependency_id]["dependents"][project_id] = dependency_type
            else:
                dependency_graph[dependency_id] = {
                    "is_manual": False,
                    "dependencies": {},
                    "dependents": {
                        project_id: dependency_type
                    }
                }

                if dependency_type == 2: # NOTE: yay hardcoded value until I need to change this
                    log.debug(f"Adding dependency '{dependency_id}' to queue")
                    queued_projects.append(dependency_id)

        visited_projects.add(project_id)

    resolved_dependencies: list[ProjectData] = []
    for project_id, project in dependency_graph.items():
        dependencies: list[Dependency] = []
        for dependency_id, dependency_type in project["dependencies"]:
            dependency: Dependency = {
                "project_id": dependency_id,
                "dependency_type": dependency_type
            }

            dependencies.append(dependency)

        dependents: list[Dependency] = {}
        for dependency_id, dependency_type in project["dependencies"]:
            dependency: Dependency = {
                "project_id": dependency_id,
                "dependency_type": dependency_type
            }


        project_data: ProjectData = {
            "project_id": project_id,
            "is_manual": project["is_manual"],
            "dependencies": dependencies
        }

        resolved_dependencies.append(project_data)

    return resolved_dependencies

print(resolve_dependencies("a", test_dependencies))