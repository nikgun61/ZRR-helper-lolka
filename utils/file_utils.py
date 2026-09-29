import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ChannelConfig:
    id: int
    type: str
    comment: str = ""


def find_file_by_prefix(directory: Path, prefix: str) -> Path:
    """Возвращает единственный файл в directory, имя которого начинается с prefix."""
    if not directory.is_dir():
        raise FileNotFoundError(f"Директория не найдена: {directory}")

    matches = sorted(
        path for path in directory.iterdir()
        if path.is_file() and path.name.startswith(prefix)
    )
    if not matches:
        raise FileNotFoundError(f"Файл с префиксом {prefix!r} не найден в {directory}")
    if len(matches) > 1:
        names = ", ".join(path.name for path in matches)
        raise RuntimeError(f"Найдено несколько файлов с префиксом {prefix!r} в {directory}: {names}")
    return matches[0]


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_file_by_prefix_and_read(directory: Path, prefix: str) -> str:
    return read_text_file(find_file_by_prefix(directory, prefix))


def load_channels(path: Path) -> list[ChannelConfig]:
    if not path.is_file():
        raise FileNotFoundError(f"Файл конфигурации каналов не найден: {path}")

    raw = json.loads(read_text_file(path))
    if not isinstance(raw, list):
        raise ValueError(f"{path.name}: ожидается JSON-массив каналов")

    channels = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"{path.name}[{index}]: ожидается объект")
        try:
            channel_id = int(item["id"])
            channel_type = str(item["type"]).strip()
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{path.name}[{index}]: нужны поля 'id' (число) и 'type'") from exc
        channels.append(ChannelConfig(
            id=channel_id,
            type=channel_type,
            comment=str(item.get("comment", "")),
        ))
    return channels
