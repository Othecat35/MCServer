from argparse import Namespace


def init(args: Namespace) -> int:
    from ..modrinth.shared import SearchSortIndex

    # CLI Arguments
    game_version: str = args.game_version

    loader_name: str = args.loader_name
    loader_version: str | None = args.loader_version

    min_ram: int = args.min_ram
    max_ram: int = args.max_ram

    search_limit: int = args.search_limit
    sort_index: SearchSortIndex = args.sort_index

    # Imports
    import copy
    import logging as log

    from .. import __version__, config, shared, state
    from ..metadata import metadata_file, set_metadata

    if min_ram > max_ram:
        log.error("Minimum RAM cannot be larger than maximum RAM")
        return 1

    # Is first initializing
    is_first_initialize = not metadata_file.exists()

    if not is_first_initialize:
        log.info("Server is already initialized, exiting...")
        return 1

    shared.set_loader_context(loader_name)

    # Special loader version
    if loader_name == "vanilla":
        loader_version = None

    # Special latest game_version
    if game_version in ["latest", "latest-release", "latest-snapshot"]:
        from ..mojang import manifest as mojang_manifest

        match game_version:
            case "latest" | "latest-release":
                log.info("Fetching the latest release version for Minecraft...")
                game_version = mojang_manifest.get_latest_release_version()
                log.info(f"Latest Minecraft release version is: {game_version}")
            case "latest-snapshot":
                log.info("Fetching the latest snapshot version for Minecraft...")
                game_version = mojang_manifest.get_latest_snapshot_version()
                log.info(f"Latest Minecraft snapshot version is: {game_version}")

    # Special latest loader_version
    if loader_version == "latest":
        match loader_name:
            # Mod Loaders
            case "fabric":
                log.info("Fetching the latest version for Fabric Loader...")
                from ..fabricmc import meta as fabricmc_meta

                loader_versions = fabricmc_meta.get_loader_versions()
                for version in loader_versions:
                    if version["is_stable"]:
                        loader_version = version["loader_version"]
                        break

                log.info(f"Latest Fabric loader version is: {loader_version}")
            # case "legacy_fabric":
            #     pass
            case "quilt":
                log.info("Fetching the latest version for Quilt Loader...")
                from ..quiltmc import meta as quiltmc_meta

                loader_versions = quiltmc_meta.get_loader_versions()
                latest_quilt_version = loader_versions[0]
                loader_version = str(latest_quilt_version["loader_version"])
                log.info(f"Latest Quilt loader version is: {loader_version}")
            # Plugin Loader
            case "paper":
                log.info("Fetching the latest version for Paper...")
                from ..papermc import api as papermc_api

                latest_paper_version = papermc_api.get_latest_project_build(
                    "paper", game_version
                )
                loader_version = str(latest_paper_version["build_id"])
                log.info(f"Latest Paper build version is: {loader_version}")
            case "purpur":
                log.info("Fetching the latest version for Purpur...")
                from ..purpurmc import api as purpurmc_api

                latest_purpur_version = purpurmc_api.get_latest_project_build(
                    "purpur", game_version
                )
                loader_version = str(latest_purpur_version["build_id"])
                log.info(f"Latest Purpur build version is: {loader_version}")

            case _:
                log.error(f"Unknown loader: {loader_name}")
                return 1

        if loader_version == "latest":
            log.error("No stable version found")
            return 1

    shared.mcserver_dir.mkdir(exist_ok=True)
    state.set_state("initializing_server")

    config.configs_dir.mkdir(exist_ok=True)
    shared.tempfiles_dir.mkdir(exist_ok=True)
    if shared.loader_context["project_directory"] is not None:
        shared.loader_context["project_directory"].mkdir(exist_ok=True)

    # Write configuration to file
    for config_name in shared.default_configs:
        configuration = shared.default_configs[config_name]
        default_config = copy.deepcopy(configuration["config_data"])

        config_override: dict = {}
        match config_name:
            case "launcher":
                config_override = {"ram": {"min": min_ram, "max": max_ram}}

            case "modrinth":
                config_override = {
                    "search_limit": search_limit,
                    "sort_index": sort_index,
                }

            case "server":
                config_override = {
                    "game_version": game_version,
                    "loader": {"name": loader_name, "version": loader_version},
                }

        config_data = shared.merge_dict(default_config, config_override)
        try:
            config.write_config(
                config_name, configuration["format_version"], config_data
            )
        except FileExistsError:
            if is_first_initialize:
                log.debug(f"Configuration file {config_name} already exists")
            else:
                log.info(
                    f"Configuration for '{config_name}' already exist, skipping..."
                )

    set_metadata(__version__)
    log.info("Initialized server configurations.")

    return 0
