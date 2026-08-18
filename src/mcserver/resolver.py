import logging as log
from collections import deque
from collections.abc import Callable
from typing import Literal, TypedDict, TypeAlias

DependencyType: TypeAlias = Literal["embedded", "optional", "required", "incompatible"]
dependency_types: dict[DependencyType, int] = {
    "embedded": 0,
    "optional": 1,
    "required": 2,
    "incompatible": 3,
}
dependency_types2: list[DependencyType] = [
    "embedded",
    "optional",
    "required",
    "incompatible",
]


class Dependency(TypedDict):
    project_id: str
    dependency_type: DependencyType


class Project(TypedDict):
    is_manual: bool
    dependencies: dict[str, int]
    dependents: dict[str, int]


class ProjectData(TypedDict):
    project_id: str
    is_manual: bool
    dependencies: list[Dependency]
    dependents: list[Dependency]


# NOTE: These are just theory, or not?
def human_to_resolver(dependencies: list[Dependency]) -> dict[str, int]:
    resolver_dependencies: dict[str, int] = {}
    for dependency in dependencies:
        resolver_dependencies[dependency["project_id"]] = dependency_types[
            dependency["dependency_type"]
        ]

    return resolver_dependencies


def resolver_to_human(dependency_graph: dict[str, Project]) -> list[ProjectData]:
    projects: list[ProjectData] = []
    for project_id, project_data in dependency_graph.items():
        dependencies: list[Dependency] = []
        for dependency_id, dependency_type in project_data["dependencies"].items():
            dependency: Dependency = {
                "project_id": dependency_id,
                "dependency_type": dependency_types2[dependency_type],
            }

            dependencies.append(dependency)

        dependents: list[Dependency] = []
        for dependency_id, dependency_type in project_data["dependents"].items():
            dependent: Dependency = {
                "project_id": dependency_id,
                "dependency_type": dependency_types2[dependency_type],
            }

            dependents.append(dependent)

        project: ProjectData = {
            "project_id": project_id,
            "is_manual": project_data["is_manual"],
            "dependencies": dependencies,
            "dependents": dependents,
        }

        projects.append(project)

    return projects


def resolve_dependencies(
    project_ids: list[str] | str,
    get_dependencies: Callable[[str], dict[str, int]],
    should_queue: Callable[[int], bool],
) -> dict[str, Project]:
    """Resolve dependency tree using BFS

    Args:
        project_ids: Projects to start with
        get_dependencies: Callback that returns a dictionary
        should_queue: Callback that returns a bool

    Raises:
        TypeError: Callback 'get_dependency' does not return a dictionary
    """
    if isinstance(project_ids, str):
        project_ids = [project_ids]

    queued_projects: deque[str] = deque()
    visited_projects: set[str] = set()
    dependency_graph: dict[str, Project] = {}

    for project_id in project_ids:
        log.debug(f"Adding project '{project_id}' to the queue")
        queued_projects.append(project_id)
        project: Project = {"is_manual": True, "dependencies": {}, "dependents": {}}
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
                dependency_graph[dependency_id]["dependents"][
                    project_id
                ] = dependency_type
            else:
                dependency_graph[dependency_id] = {
                    "is_manual": False,
                    "dependencies": {},
                    "dependents": {project_id: dependency_type},
                }

                if should_queue(dependency_type):
                    log.debug(f"Adding dependency '{dependency_id}' to queue")
                    queued_projects.append(dependency_id)

        visited_projects.add(project_id)

    return dependency_graph


def required_only(dependency_type: int) -> bool:
    return dependency_type == dependency_types["required"]


def test_dependencies(project_id: str) -> dict[str, int]:
    dependencies = {
        "embeddium": [{"project_id": "sodium", "dependency_type": "incompatible"}],
        "fabric-api": [],
        "origins": [{"project_id": "fabric-api", "dependency_type": "required"}],
        "pehkui": [{"project_id": "fabric-api", "dependency_type": "required"}],
        "podium": [{"project_id": "sodium", "dependency_type": "required"}],
        "sodium": [],
        "thdilos-fox-origin-expanded": [
            {"project_id": "thdilos-fox-origin", "dependency_type": "required"},
            {"project_id": "pehkui", "dependency_type": "required"},
            {"project_id": "origins", "dependency_type": "required"},
        ],
        "thdilos-fox-origin": [
            {"project_id": "pehkui", "dependency_type": "required"},
            {"project_id": "origins", "dependency_type": "required"},
        ]
    }

    return human_to_resolver(dependencies[project_id])


print(resolver_to_human(resolve_dependencies(["embeddium", "podium"], test_dependencies, required_only)))
