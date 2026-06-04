import json

from network import request_url

# Functions
def get_latest_build(project_name: str, mc_version: str):
  request_url(f"https://fill.papermc.io/v3/projects/{project_name}/versions/${mc_version}/builds")