import argparse


def main(args: argparse.Namespace) -> int:
    projects: list[str] = args.projects

    from ..modrinth import api as modrinth_api
    from ..shared import format_number

    project_information = modrinth_api.get_project_information(projects)
    for project in project_information:
        if "project_title" in project and "project_slug" in project:
            print(f"Name: {project['project_title']} ({project['project_slug']})")

        if "download_count" in project:
            print(f"Downloads: {format_number(project['download_count'])}")

        if "follower_count" in project:
            print(f"Followers: {format_number(project["follower_count"])}")

        if "project_slug" in project:
            print(
                f"Homepage: https://modrinth.com/{project['project_type']}/{project['project_slug']}"
            )

    return 0
