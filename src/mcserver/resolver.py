import logging as log
from collections import deque
from collections.abc import Callable

def resolve_dependencies(initial_nodes: list[str] | str, get_dependencies: Callable, check_conflict: Callable) -> list:
    if isinstance(initial_nodes, str):
        initial_nodes = [initial_nodes]

    queued_nodes: deque[str] = deque()
    visited_nodes: set[str] = set()
    dependency_graph: dict[str, dict] = {}

    for node in initial_nodes:
        log.debug(f"Adding node '{project_id}' to queued nodes")
        queued_nodes.append(node_id)
        node_data = {
            "is_manual": True,
            "dependencies": {},
            "dependents": {}
        }

        dependency_graph[project_id] = node_data

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
