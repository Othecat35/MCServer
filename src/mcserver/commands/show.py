from argparse import Namespace


def show(args: Namespace) -> int:
    projects: list[str] = args.projects

    import logging

    from .. import shared
    from ..modrinth import apis as modrinth_api
    from ..shared import format_number, pluralize

    logger = logging.getLogger(__name__)

    logger.info(f"Getting {pluralize("project", len(projects))} informations...")
    project_informations = modrinth_api.get_project_informations(projects)

    logger.info(f"Showing {len(project_informations)} out of {len(projects)} {pluralize("project", len(project_informations))}.")
    for project_information in project_informations:
        slug_or_id = project_information.get("project_slug", project_information["project_id"])
        print(f"Name: {project_information["project_name"]} ({slug_or_id})")

        download_count = project_information["download_count"]
        print(f"{pluralize("Download", download_count)}: {format_number(download_count)}")

        follower_count = project_information["follower_count"]
        print(f"{pluralize("Follower", follower_count)}: {format_number(follower_count)}")

        categories = project_information["categories"]
        readable_categories: list[str] = []
        for category in categories:
            readable_categories.append(category.replace("-", " ").title())
        print(f"{pluralize("Category", len(categories))}: {', '.join(readable_categories)}")

        loader_names = project_information["loader_names"]
        loaders: list[str] = []
        for loader in loader_names:
            loaders.append(loader.title())
        print(f"{pluralize("Loader", len(loader_names))}: {', '.join(loaders)}")

        game_versions = project_information["game_versions"]
        print(f"Minecraft {pluralize("Version", len(game_versions))}: {', '.join(game_versions)}")

        environments = project_information["environments"]
        readable_environments: list[str] = []
        for environment in environments:
            readable_environments.append(shared.project_environment_name(environment))
        print(f"{pluralize("Environment", len(environments))}: {', '.join(readable_environments)}")

        print(f"Homepage: https://modrinth.com/{project_information["project_type"]}/{slug_or_id}")
        print(f"Description: {project_information["short_description"]}")

    return 0
