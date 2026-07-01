#Modules
# Standard
import collections
import typing

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
class NodeData(typing.TypedDict):
  manual: bool
  type: typing.Literal[0] | typing.Literal[1] | typing.Literal[2] | typing.Literal[3]
  dependencies: dict[str, typing.Literal[0] | typing.Literal[1] | typing.Literal[2] | typing.Literal[3]]
  dependants: dict[str, typing.Literal[0] | typing.Literal[1] | typing.Literal[2] | typing.Literal[3]]

# Functions
def get_dependecies() -> dict[str, typing.Literal[0] | typing.Literal[1] | typing.Literal[2] | typing.Literal[3]]:
  return {}

def is_conflicting(node_type: typing.Literal[0] | typing.Literal[1] | typing.Literal[2] | typing.Literal[3], dependant_type: typing.Literal[0] | typing.Literal[1] | typing.Literal[2] | typing.Literal[3]) -> bool:
  if node_type == dependency_types["incompatible"] and dependant_type == dependency_types["required"]:
    return True
  elif node_type == dependency_types["required"] and dependant_type == dependency_types["incompatible"]:
    return True

  return False

def resolve_dependencies(initial_seeds: list[str] | str, get_dependency_data: typing.Callable, is_conflicting: typing.Callable) -> dict[str, NodeData]:
  if isinstance(initial_seeds, str): initial_seeds = [initial_seeds]
  unresolved_nodes = collections.deque()

  resolved_nodes = set()
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

    dependencies = get_dependency_data(node_id)
    resolved_data[node_id]["dependencies"] = dependencies
    for dependency_id, dependency_type in dependencies.items():
      if dependency_id in resolved_data:
        dependency_node = resolved_data[dependency_id]
        if is_conflicting(dependency_node["type"], dependency_type):
          raise DependencyConflictError(dependency_node["dependencies"], {
            node_id: dependency_type
          })

        dependency_node["type"] = max(dependency_node["type"], dependency_type)
        if dependency_type == dependency_types["required"]:
          unresolved_nodes.append(dependency_id)

        dependency_node["dependants"][node_id] = dependency_type
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

  return resolved_data





