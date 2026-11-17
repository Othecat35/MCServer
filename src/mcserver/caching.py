from .paths import cache_dir


def create_file(file_name: str, file_data: bytes):
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / file_name
    cache_file.write_bytes(file_data)
