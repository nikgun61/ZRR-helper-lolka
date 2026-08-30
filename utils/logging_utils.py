import logging
from pathlib import Path


def setup_logging() -> None:
    log_directory = Path('logs')
    log_directory.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        log_directory / 'bot.log',
        encoding='utf-8',
    )
    file_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            console_handler,
            file_handler,
        ],
    )