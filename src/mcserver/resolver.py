import logging as log
from collections import deque
from typing import Callable

def resolve_dependencies(project_ids: list[str] | str, get_dependencies: Callable, check_conflict: Callable):
    if isinstance(project_ids, str):
        project_ids = [project_ids]

    queued_nodes: deque[str] = deque()
    visited_nodes: set[str] = set()
    dependency_graph: dict = {}

    for project_id in project_ids:
        log.debug(f"Adding project ID '{project_id}' to queued nodes")
        queued_nodes.append(project_id)
        dependency_graph[project_id] = {
            "is_manual": True,
            "dependencies": {},
            "dependents": {}
        }

    while queued_nodes:
        project_id = queued_nodes.popleft()
        if project_id in visited_nodes:
            log.debug(f"Project ID '{project_id}' has already been visited")
            continue

        dependencies = get_dependencies(project_id)
        dependency_graph[project_id]["dependencies"] = dependencies

        for dependency_id, dependency_type in dependencies.items():
            if dependency_id in visited_nodes:
                dependency_graph[dependency_id]["dependents"][project_id] = dependency_type
            else:
                dependency_graph[dependency_id] = {
                    "is_manual": False,
                    "dependencies": {},
                    "dependents": {
                        project_id: dependency_type
                    }
                }

                if dependency_type == "required":
                    log.debug(f"Adding dependency ID '{dependency_id}' to queued nodes")
                    queued_nodes.append(dependency_id)

        visited_nodes.add(project_id)
