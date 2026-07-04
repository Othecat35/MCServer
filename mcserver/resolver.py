#Modules
# Standard
import collections

from typing import Callable, Literal, TypedDict

#Variables
dependency_types = {
  "incompatible": 3,
  "required": 2,
  "optional": 1,
  "embedded": 0
}

#Errors
class DependencyConflictError(Exception):
  def __init__(self, node_id: str, incompatible_nodes: list[str] | str, required_nodes: list[str] | str | None = None):
    if required_nodes is None: required_nodes = []
    if isinstance(required_nodes, str): required_nodes = [required_nodes]
    if isinstance(incompatible_nodes, str): incompatible_nodes = [incompatible_nodes]

    required_message = ""
    if required_nodes:
      required_join = "', '".join(required_nodes)
      required_message = f" but required by '{required_join}'"

    incompatible_join = "', '".join(incompatible_nodes)
    super().__init__(f"Node '{node_id}' is incompatible with '{incompatible_join}'{required_message}")

    self.node_id = node_id
    self.incompatible_nodes = incompatible_nodes
    self.required_nodes = required_nodes

#TypedDict
class NodeData(TypedDict):
  manual: bool
  type: Literal[0, 1, 2, 3]
  dependencies: dict[str, Literal[0, 1, 2, 3]]
  dependants: dict[str, Literal[0, 1, 2, 3]]
  node_id: str

# Functions
def filter_dependencies_type(dependencies: dict, filter_dependency_type: int) -> list[str]:
  dependencies_list = []
  for dependency_node, dependency_type in dependencies.items():
    if dependency_type == filter_dependency_type:
      dependencies_list.append(dependency_node)

  return dependencies_list

def get_dependency_data(node_id: str, game_versions: list[str] | str, loader_versions: list[str] | str) -> dict[str, Literal[0, 1,2, 3]]:
  if isinstance(game_versions, str): game_versions = [game_versions]
  if isinstance(loader_versions, str): loader_versions = [loader_versions]
  return {}

def check_conflics(node_id: str, node_data: NodeData, dependant_id: str, dependant_type: Literal[0 ,1, 2, 3]) -> None:
  if node_data["type"] == dependency_types["required"] and dependant_type == dependency_types["incompatible"]:
    raise DependencyConflictError(node_id, dependant_id, filter_dependencies_type(node_data["dependants"], dependency_types["required"]))
  elif node_data["type"] == dependency_types["incompatible"] and dependant_type == dependency_types["required"]:
    raise DependencyConflictError(node_id, filter_dependencies_type(node_data["dependants"], dependency_types["incompatible"]), dependant_id)

def resolve_dependencies(initial_seeds: list[str] | str, get_dependency_data: Callable, check_conflicts: Callable, loader_versions: list[str] | str | None = None, game_versions: list[str] | str | None = None) -> list[NodeData]:
  if isinstance(initial_seeds, str): initial_seeds = [initial_seeds]

  if isinstance(loader_versions, str): loader_versions = [loader_versions]
  if isinstance(game_versions, str): game_versions = [game_versions]

  unresolved_nodes = collections.deque()
  resolved_nodes: set[str] = set()
  resolved_data = {}

  for seed in initial_seeds:
    if seed not in unresolved_nodes:
      unresolved_nodes.append(seed)
      resolved_data[seed] = {
        "manual": True,
        "type": dependency_types["required"],
        "dependencies": {},
        "dependants": {}
      }

  while unresolved_nodes:
    node_id = unresolved_nodes.popleft()
    if node_id in resolved_nodes:
      continue

    dependencies = get_dependency_data(node_id, game_versions, loader_versions)
    resolved_data[node_id]["dependencies"] = dependencies

    for dependency_id, dependency_type in dependencies.items():
      if dependency_id in resolved_data:
        dependency_data = resolved_data[dependency_id]

        check_conflicts(dependency_id, dependency_data,  node_id, dependency_type)
        dependency_data["type"] = max(dependency_data["type"], dependency_type)
        if dependency_type == dependency_types["required"]:
          unresolved_nodes.append(dependency_id)

        dependency_data["dependants"][node_id] = dependency_type
      else:
        resolved_data[dependency_id] = {
          "manual": False,
          "type": dependency_type,
          "dependencies": {},
          "dependants": {
            node_id: dependency_type
          }
        }

        if dependency_type == dependency_types["required"]:
          unresolved_nodes.append(dependency_id)

    resolved_nodes.add(node_id)

  node_list = []
  for node_id, node_data in resolved_data.items():
    node = dict(node_data)
    node["node_id"] = node_id

    node_list.append(node)

  return node_list
