from . import paths


def create_file(file_name: str, file_data: bytes):
    paths.cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = paths.cache_dir / file_name
    cache_file.write_bytes(file_data)
