import json
from pathlib import Path

def find_file_by_prefix(directory: str, prefix: str) -> Path:
    files = list(Path(directory).glob(f"{prefix}*"))

    if not files:
        raise FileNotFoundError(
            f"Файл с префиксом {prefix!r} не найден в {directory!r}"
        )

    if len(files) > 1:
        raise RuntimeError(
            f"Найдено несколько файлов с префиксом {prefix!r}: "
            f"{[file.name for file in files]}"
        )

    return files[0]

def read_text_file(path: str | Path) -> str:
    return Path(path).read_text(
        encoding="utf-8"
    )

def find_file_by_prefix_and_read(directory: str, prefix: str) -> str:
    return read_text_file(
        find_file_by_prefix(
            directory=directory,
            prefix=prefix
        )
    )

def load_channels() -> dict:
    with open("channels.json", encoding="utf-8") as file:
        return json.load(file)