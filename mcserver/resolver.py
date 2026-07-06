# #Modules
# # Standard
# import collections

# from typing import Callable, Literal, TypedDict

# #Variables
# dependency_types = {
#     "incompatible": 3,
#     "required": 2,
#     "optional": 1,
#     "embedded": 0
# }

# #Errors
# class DependencyConflictError(Exception):
#     def __init__(self, node_id: str, incompatible_nodes: list[str] | str, required_nodes: list[str] | str | None = None):
#         if required_nodes is None: required_nodes = []
#         if isinstance(required_nodes, str): required_nodes = [required_nodes]
#         if isinstance(incompatible_nodes, str): incompatible_nodes = [incompatible_nodes]

#         required_message = ""
#         if required_nodes:
#             required_join = "', '".join(required_nodes)
#             required_message = f" but required by '{required_join}'"

#         incompatible_join = "', '".join(incompatible_nodes)
#         super().__init__(f"Node '{node_id}' is incompatible with '{incompatible_join}'{required_message}")

#         self.node_id = node_id
#         self.incompatible_nodes = incompatible_nodes
#         self.required_nodes = required_nodes

# #TypedDict
# class NodeData(TypedDict):
#     manual: bool
#     type: Literal[0, 1, 2, 3]
#     dependencies: dict[str, Literal[0, 1, 2, 3]]
#     dependants: dict[str, Literal[0, 1, 2, 3]]
#     node_id: str

# # Functions
# def filter_dependencies_type(dependencies: dict, filter_dependency_type: int) -> list[str]:
#     dependencies_list = []
#     for dependency_node, dependency_type in dependencies.items():
#         if dependency_type == filter_dependency_type:
#             dependencies_list.append(dependency_node)

#     return dependencies_list

# def get_dependency_data(node_id: str, game_versions: list[str] | str, loader_versions: list[str] | str) -> dict[str, Literal[0, 1,2, 3]]:
#     if isinstance(game_versions, str): game_versions = [game_versions]
#     if isinstance(loader_versions, str): loader_versions = [loader_versions]
#     return {}

# def check_conflics(node_id: str, node_data: NodeData, dependant_id: str, dependant_type: Literal[0 ,1, 2, 3]) -> None:
#     if node_data["type"] == dependency_types["required"] and dependant_type == dependency_types["incompatible"]:
#         raise DependencyConflictError(node_id, dependant_id, filter_dependencies_type(node_data["dependants"], dependency_types["required"]))
#     elif node_data["type"] == dependency_types["incompatible"] and dependant_type == dependency_types["required"]:
#         raise DependencyConflictError(node_id, filter_dependencies_type(node_data["dependants"], dependency_types["incompatible"]), dependant_id)

# def resolve_dependencies(initial_seeds: list[str] | str, get_dependency_data: Callable, check_conflicts: Callable, loader_versions: list[str] | str | None = None, game_versions: list[str] | str | None = None) -> list[NodeData]:
#     if isinstance(initial_seeds, str): initial_seeds = [initial_seeds]

#     if isinstance(loader_versions, str): loader_versions = [loader_versions]
#     if isinstance(game_versions, str): game_versions = [game_versions]

#     unresolved_nodes = collections.deque()
#     resolved_nodes: set[str] = set()
#     resolved_data = {}

#     for seed in initial_seeds:
#         if seed not in unresolved_nodes:
#             unresolved_nodes.append(seed)
#             resolved_data[seed] = {
#                 "manual": True,
#                 "type": dependency_types["required"],
#                 "dependencies": {},
#                 "dependants": {}
#             }

#     while unresolved_nodes:
#         node_id = unresolved_nodes.popleft()
#         if node_id in resolved_nodes:
#             continue

#         dependencies = get_dependency_data(node_id, game_versions, loader_versions)
#         resolved_data[node_id]["dependencies"] = dependencies

#         for dependency_id, dependency_type in dependencies.items():
#             if dependency_id in resolved_data:
#                 dependency_data = resolved_data[dependency_id]

#                 check_conflicts(dependency_id, dependency_data,    node_id, dependency_type)
#                 dependency_data["type"] = max(dependency_data["type"], dependency_type)
#                 if dependency_type == dependency_types["required"]:
#                     unresolved_nodes.append(dependency_id)

#                 dependency_data["dependants"][node_id] = dependency_type
#             else:
#                 resolved_data[dependency_id] = {
#                     "manual": False,
#                     "type": dependency_type,
#                     "dependencies": {},
#                     "dependants": {
#                         node_id: dependency_type
#                     }
#                 }

#                 if dependency_type == dependency_types["required"]:
#                     unresolved_nodes.append(dependency_id)

#         resolved_nodes.add(node_id)

#     node_list = []
#     for node_id, node_data in resolved_data.items():
#         node = dict(node_data)
#         node["node_id"] = node_id

#         node_list.append(node)

#     return node_list










# def resolve_projects(projects_id: list | str, game_version: str, loader_name: str) -> dict:
#     projects_id = list(projects_id)
#     unresolved_ids = deque()
#     resolved_data = {}

#     # Initial seeding
#     for project_id in projects_id:
#         project_id = slug_to_id(project_id)

#         log.debug(f"Adding project '{project_id}' as unresolved")
#         unresolved_ids.append(project_id)
#         resolved_data[project_id] = {
#             "metadata": {},
#             "relationship": {
#                 "manual": True,
#                 "type": version_dependency_types["required"],
#                 "dependencies": {},
#                 "dependants": {}
#             }
#         }

#     # Main code
#     while unresolved_ids:
#         project_id = unresolved_ids.popleft()

#         project_data = resolved_data.pop(project_id)
#         project_metadata = project_data["metadata"]
#         project_relationship = project_data["relationship"]

#         log.debug(f"Processing project '{project_id}'")

#         skip_fetch_version = False

#         if project_index_exists(project_id):
#             project_index_data = read_project_index(project_id)

#             project_index_relationship = project_index_data["relationship"]
#             project_dependency_type = project_index_relationship["type"]

#             if project_dependency_type == version_dependency_types["incompatible"]:
#                 project_dependants = project_index_relationship["dependants"]

#                 incompatible_dependants = filter_dependencies_type(project_dependants, "incompatible")
#                 required_dependants = filter_dependencies_type(project_dependants, "required")
#                 raise ResolveProjectsConflictsError(project_id, incompatible_dependants, required_dependants)

#             log.debug("Project index exists, using it as cache")
#             project_index_relationship["dependants"].update(project_relationship["dependants"])
#             if project_relationship["manual"]:
#                 project_index_relationship["manual"] = True

#             project_data = project_index_data
#             skip_fetch_version = True

#         if not skip_fetch_version:
#             log.debug("Fetching project version")
#             version = get_project_versions(project_id, game_version, loader_name)[0]
#             project_id = version["project_id"]

#             # Check if entry with project ID still exists (meaning we're still using slug)
#             if project_id in resolved_data:
#                 log.debug(f"Found existing data with ID {project_id}")
#                 existing_entry = resolved_data.pop(project_id)
#                 existing_entry_relationship = existing_entry["relationship"]

#                 # Check if existing entry is marked as incompatible
#                 if existing_entry_relationship["type"] == version_dependency_types["incompatible"]:
#                     incompatible_dependants = filter_dependencies_type(existing_entry_relationship["dependants"], "incompatible")
#                     raise ResolveProjectsConflictsError(project_id, incompatible_dependants)

#                 log.debug(f"Keeping existing data")
#                 project_relationship["dependants"].update(existing_entry_relationship["dependants"])

#             if "version_id" in version:
#                 project_metadata["version_id"] = version["version_id"]

#             if "version_name" in version:
#                 project_metadata["version_name"] = version["version_name"]
            
#             if "version_number" in version:
#                 project_metadata["version_number"] = version["version_number"]

#             if "dependencies" in version:
#                 project_relationship["dependencies"] = adapt_dependencies_data(version["dependencies"])

#         for dependency_id, dependency_type in project_relationship["dependencies"].items():
#             if dependency_id in resolved_data:
#                 dependency_data = resolved_data[dependency_id]
#                 dependency_data_relationship = dependency_data["relationship"]

#                 dependency_data_type = dependency_data_relationship["type"]
#                 dependency_data_dependants = dependency_data_relationship["dependants"]

#                 if dependency_type == version_dependency_types["required"]:
#                     if dependency_data_type == version_dependency_types["incompatible"]:
#                         incompatible_dependants = filter_dependencies_type(dependency_data_dependants, "incompatible")
#                         raise ResolveProjectsConflictsError(dependency_id, incompatible_dependants, project_id)
#                     elif dependency_data_type == version_dependency_types["optional"]:
#                         log.debug(f"Adding initially optional dependency '{project_id}' to unresolved")
#                         unresolved_ids.append(dependency_id)
#                 elif dependency_type == version_dependency_types["incompatible"] and dependency_data_type == version_dependency_types["required"]:
#                     required_dependants = filter_dependencies_type(dependency_data_dependants, "required")
#                     raise ResolveProjectsConflictsError(dependency_id, project_id, required_dependants)

#                 log.debug(f"Updating project data '{dependency_id}' with new '{dependency_type}' type dependant")
#                 dependency_data_dependants[project_id] = dependency_type
#                 dependency_data_relationship["type"] = max(dependency_data_relationship["type"], dependency_type)
#             else:
#                 log.debug(f"Adding new project entry for dependency: {dependency_id}")
#                 resolved_data[dependency_id] = {
#                     "metadata": {},
#                     "relationship": {
#                         "manual": False,
#                         "type": dependency_type,
#                         "dependencies": {},
#                         "dependants": {
#                             project_id: dependency_type
#                         }
#                     }
#                 }

#                 # Only process required mods
#                 if dependency_type == version_dependency_types["required"]:
#                     unresolved_ids.append(dependency_id)

#         resolved_data[project_id] = project_data

#     # Populate resolved_data with even more data
#     fetch_ids = []
#     for project_id, project_data in resolved_data.items():
#         #If project data doesn't have slug, fetch it
#         if not project_data["metadata"].get("project_slug"): fetch_ids.append(project_id)

#     if fetch_ids != []:
#         projects = json.loads(request(f"{modrinth_base_api}/v2/projects", query={
#             "ids": json.dumps(fetch_ids)
#         })["body"])

#         for project in projects:
#             if resolved_data[project["id"]]["relationship"]["type"] in (version_dependency_types["required"], version_dependency_types["incompatible"]):
#                 slug_id[project["slug"]] = {
#                     "id": project["id"]
#                 }

#             project_metadata = resolved_data[project["id"]]["metadata"]

#             project_metadata["project_slug"] = project["slug"]
#             project_metadata["project_title"] = project["title"]
#             project_metadata["project_description"] = project["description"]
#             project_metadata["project_license"] = project["license"]
#             project_metadata["loaders"] = project["loaders"]

#         # Update with new slug to ID data
#         slug_id_file.write_text(json.dumps(slug_id, indent=2))

#     # Write project index
#     for project_id, project_data in resolved_data.items():
#         project_type = project_data["relationship"]["type"]
#         if project_type in (version_dependency_types["required"], version_dependency_types["incompatible"]):
#             log.debug(f"Indexing project '{project_id}' with type {project_type} and manual {project_data["relationship"]['manual']}")
#             #write_project_index(project_id, project_data)
#             if project_index_exists(project_id):
#                 update_project_index(project_id, project_data["metadata"], project_data["relationship"])
#             else:
#                 create_project_index(project_id, project_data["metadata"], project_data["relationship"])

#     if debug_mode: print(json.dumps(resolved_data, indent=2))
#     return resolved_data