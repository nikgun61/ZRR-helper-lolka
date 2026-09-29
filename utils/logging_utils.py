import logging
from pathlib import Path

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(log_dir: Path, level: int = logging.INFO) -> None:
    """Логирование одновременно в консоль и в <log_dir>/bot.log."""
    log_dir.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_dir / "bot.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    # Защита от дублирования записей при повторном вызове.
    for handler in list(root.handlers):
        root.removeHandler(handler)
        handler.close()
    root.addHandler(console_handler)
    root.addHandler(file_handler)
