try:
    from .. import urls
    purpurmc_api_url = getattr(urls, "purpurmc_api_url", "https://api.purpurmc.org")
except ImportError:
    purpurmc_api_url: str = "https://api.purpurmc.org"