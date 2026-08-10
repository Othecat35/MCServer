#!/usr/bin/env python3
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestMCServer(unittest.TestCase):
    script_path = Path.cwd() / "mcserver"

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.test_directory = Path(self.temporary_directory.name)

        self.mcserver_path = self.test_directory / ".mcserver"
        self.configs_path = self.mcserver_path / "configs"

    def tearDown(self):
        self.temporary_directory.cleanup()


if __name__ == "__main__":
    unittest.main()
