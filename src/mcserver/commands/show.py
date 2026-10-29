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

        if "additional_categories" in project_information:
            additional_categories = project_information["additional_categories"]
            readable_additional_categories: list[str] = []
            for additional_category in additional_categories:
                readable_additional_categories.append(additional_category.replace("-", " ").title())
            print(f"Additional {pluralize("Category", len(additional_categories))}: {', '.join(readable_additional_categories)}")


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

        project_license = project_information["project_license"]
        license_string = ""
        if "license_name" in project_license:
            license_string = project_license["license_name"]

        if "license_id" in project_license:
            if license_string != "":
                license_string += f"({project_license['license_id']})"
            else:
                license_string = project_license["license_id"]
        print(f"License: {license_string}")

        print(f"Homepage: https://modrinth.com/{project_information["project_type"]}/{slug_or_id}")

        if "source_url" in project_information:
            print(f"Source Code: {project_information["source_url"]}")

        if "issues_url" in project_information:
            print(f"Issues: {project_information["issues_url"]}")

        if "wiki_url" in project_information:
            print(f"Wiki: {project_information["wiki_url"]}")

        if "discord_url" in project_information:
            print(f"Discord: {project_information["discord_url"]}")

        print(f"Description: {project_information["short_description"]}")

    return 0
