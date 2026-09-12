#!/usr/bin/env python3
import unittest

from src.mcserver.resolver import resolve_dependencies, human_to_resolver, resolver_to_human, dependency_types

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
        ],
    }

    return human_to_resolver(dependencies[project_id])

def required_only(dependency_type: int) -> bool:
    return dependency_type == dependency_types["required"]

class TestDependencyResolver(unittest.TestCase):
    def test_resolve(self):
        print(resolver_to_human(resolve_dependencies("thdilos-fox-origin", test_dependencies, required_only)))


if __name__ == "__main__":
    unittest.main()
