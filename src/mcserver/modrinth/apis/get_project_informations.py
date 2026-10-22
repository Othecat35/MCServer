from ..typings import ProjectInformation


class GetProjectInformationError(Exception):
    pass


def main(project_ids: list[str] | str) -> list[ProjectInformation]:
    """Get information about Modrinth projects

    Args:
        project_ids: The ID of the projects

    Returns:
        List of project informations
    """
    if isinstance(project_ids, str):
        project_ids = [project_ids]

    import json
    import logging as log

    from ... import networking
    from .. import constants, shared
    from ..typings import (
        DonationPlatform,
        Environment,
        EnvironmentSide,
        GalleryImage,
        MonetizationStatus,
        ProjectLicense,
        ProjectStatus,
        ProjectType,
    )

    query_parameters = {"ids": json.dumps(project_ids)}

    response = networking.request(
        f"{constants.modrinth_api_url}/v2/projects", query_parameters
    )

    if "json" not in response:
        raise GetProjectInformationError("Cannot load JSON response")

    project_informations: list[ProjectInformation] = []
    for information in response["json"]:
        # Checks
        project_status: ProjectStatus = information["status"]
        if project_status not in shared.PROJECT_STATUS:
            log.debug(f"Unknown project status: {project_status}")

        project_type: ProjectType = information["project_type"]
        if project_type not in shared.PROJECT_TYPE:
            log.debug(f"Unknown project type: {project_type}")

        monetization_status: MonetizationStatus = information["monetization_status"]
        if monetization_status not in shared.MONETIZATION_STATUS:
            log.debug(f"Unknown monetization status: {monetization_status}")

        client_side: EnvironmentSide = information["client_side"]
        if client_side not in shared.ENVIRONMENT_SIDE:
            log.debug(f"Unknown client side: {client_side}")

        server_side: EnvironmentSide = information["server_side"]
        if server_side not in shared.ENVIRONMENT_SIDE:
            log.debug(f"Unknown server side: {server_side}")

        # Lists
        categories: list[str] = []
        for category in information["categories"]:
            categories.append(category)

        additional_categories: list[str] = []
        for additional_category in information["additional_categories"]:
            categories.append(additional_category)

        environments: list[Environment] = []
        for environment in information["environment"]:
            if environment in shared.ENVIRONMENT:
                log.debug(f"Unknown environment: {environment}")

            environments.append(environment)

        game_versions: list[str] = []
        for game_version in information["game_versions"]:
            game_versions.append(game_version)

        loader_names: list[str] = []
        for loader_name in information["loaders"]:
            loader_names.append(loader_name)

        version_ids: list[str] = []
        for version_id in information["versions"]:
            version_ids.append(version_id)

        gallery: list[GalleryImage] = []
        for image in information["gallery"]:
            gallery_image: GalleryImage = {
                "image_url": image["url"],
                "is_featured": image["featured"],
                "created_time": image["created"],
            }

            if "title" in image:
                gallery_image["image_title"] = image["title"]

            if "description" in image:
                gallery_image["image_description"] = image["description"]

            if "ordering" in image:
                gallery_image["ordering_number"] = image["ordering"]

            gallery.append(gallery_image)

        donation_platforms: list[DonationPlatform] = []
        if "donation_urls" in information:
            for platform in information["donation_urls"]:
                donation_platform: DonationPlatform = {}
                if "id" in platform:
                    donation_platform["platform_id"] = platform["id"]

                if "platform" in platform:
                    donation_platform["platform_name"] = platform["platform"]

                if "url" in platform:
                    donation_platform["donation_url"] = platform["url"]

                donation_platforms.append(donation_platform)

        # Dictionaries
        project_license: ProjectLicense = {}
        information_license = information["license"]
        if "id" in information_license:
            project_license["license_id"] = information_license["id"]

        if "name" in information_license:
            project_license["license_name"] = information_license["name"]

        if "url" in information_license:
            project_license["license_url"] = information_license["url"]

        # Construction
        project_information: ProjectInformation = {
            "project_id": information["id"],
            "team_id": information["team"],
            "project_name": information["title"],
            "short_description": information["description"],
            "description": information["body"],
            "project_status": project_status,
            "project_type": project_type,
            "categories": categories,
            "additional_categories": additional_categories,
            "environments": environments,
            "game_versions": game_versions,
            "loader_names": loader_names,
            "version_ids": version_ids,
            "project_license": project_license,
            "published_time": information["published"],
            "updated_time": information["updated"],
            "download_count": information["downloads"],
            "follower_count": information["followers"],
            "gallery": gallery,
            "thread_id": information["thread_id"],
            "monetization_status": monetization_status,
            "client_side": client_side,
            "server_side": server_side,
        }

        if "slug" in information:
            project_information["project_slug"] = information["slug"]

        if "organization" in information:
            project_information["organization_id"] = information["organization"]

        if "requested_status" in information:
            project_information["requested_status"] = information["requested_status"]

        if "approved" in information:
            project_information["approved_time"] = information["approved"]

        if "queued" in information:
            project_information["queued_time"] = information["queued"]

        if "icon_url" in information:
            project_information["icon_url"] = information["icon_url"]

        if "raw_icon_url" in information:
            project_information["raw_icon_url"] = information["raw_icon_url"]

        if "color" in information:
            project_information["icon_color"] = information["color"]

        if "issues_url" in information:
            project_information["issues_url"] = information["issues_url"]

        if "source_url" in information:
            project_information["source_url"] = information["source_url"]

        if "wiki_url" in information:
            project_information["wiki_url"] = information["wiki_url"]

        if "discord_url" in information:
            project_information["discord_url"] = information["discord_url"]

        if "donation_urls" in information:
            project_information["donation_platforms"] = donation_platforms

        if "body_url" in information:
            project_information["body_url"] = information["body_url"]

        if "moderator_message" in information:
            project_information["moderator_message"] = information["moderator_message"]

        project_informations.append(project_information)

    return project_informations
