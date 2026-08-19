from argparse import Namespace


def main(args: Namespace) -> int:
    import logging as log

    from .. import state

    # Check MCServer status
    current_state = state.get_state()
    if current_state["is_active"]:
        log.error(
            f"There's another active MCServer process ({current_state["action"]}) running with process ID: {current_state["process_id"]}"
        )
        return 1

    # Set state
    state.set_state("running_server")

    import os
    import shutil
    from pathlib import Path

    from .. import config

    # Load configs
    launcher_config = config.load_config("launcher")

    jarfile = Path(launcher_config["jarfile"])
    memory_config = launcher_config["ram"]

    # Download jarfile
    if not jarfile.exists():
        import json

        from .. import networking

        state.set_state("downloading_server")

        server_config = config.load_config("server")
        game_version = server_config["game_version"]
        server_loader = server_config["loader"]

        loader_name = server_loader["name"]
        loader_version = server_loader["version"]

        if loader_name != "vanilla" and loader_version is None:
            log.error(f"Loader version cannot be null")
            return 1

        match loader_name:
            # Mod loaders
            case "fabric":
                from ..fabricmc import meta as fabricmc_meta

                log.info(
                    f"Downloading Fabric loader {loader_version} for Minecraft version {game_version}..."
                )
                networking.download(
                    fabricmc_meta.download_url(game_version, loader_version, "1.0.1"),
                    jarfile,
                )

            #            case "quilt":
            #                log.info(f"Downloading Quilt loader {loader_version} for Minecraft version {game_version}...")
            #                networking.download(f"https://")

            #            case "legacy-fabric":
            #                pass

            # Plugin loaders
            case "paper":
                from ..papermc import api as papermc_api

                log.info(
                    f"Downloading Paper build {loader_version} for Minecraft version {game_version}..."
                )

                download_prop = papermc_api.get_project_build(
                    "paper", game_version, loader_version
                )["download_props"]["server:default"]
                networking.download(download_prop["download_url"], jarfile)
            case "purpur":
                from ..purpurmc import api as purpurmc_api

                log.info(
                    f"Downloading Purpur build {loader_version} for Minecraft version {game_version}..."
                )
                networking.download(
                    purpurmc_api.download_url("purpur", game_version, loader_version),
                    jarfile,
                )

            # Vanilla
            case "vanilla":
                from ..mojang import manifest as mojang_manifest

                log.info(f"Downloading vanilla Minecraft version {game_version}...")

                version_manifest = mojang_manifest.get_version_manifest()[
                    "game_versions"
                ]
                package_url = None
                for version in version_manifest:
                    if version["version_id"] == game_version:
                        package_url = version["package_url"]
                        break

                if package_url is None:
                    log.error(f"Minecraft version not found: {game_version}")
                    return 1

                package_data = networking.request(package_url)["text"]
                package_json = json.loads(package_data)
                version_download = package_json["downloads"]["server"]

                networking.download(
                    version_download["url"],
                    jarfile,
                    hashes={"sha1": version_download["sha1"]},
                )
            case _:
                log.error(f"Loader is not supported: {loader_name}")

    # Check stuff
    if not shutil.which("java"):
        log.error("Java is not installed in PATH")
        return 1

    if memory_config["min"] > memory_config["max"]:
        log.error("Minimum RAM is bigger than maximum RAM")
        return 1

    # Run the server
    java_command_argv = [
        "java",
        f"-Xmx{memory_config['max']}M",
        f"-Xms{memory_config['min']}M",
        "-jar",
        str(jarfile),
    ]

    if launcher_config["is_nogui"]:
        java_command_argv.append("nogui")

    # Execute java
    log.debug(f"Executing command: {' '.join(java_command_argv)}")

    state.set_state("server_running")
    os.execvp(java_command_argv[0], java_command_argv)
