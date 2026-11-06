import logging
from pathlib import Path
from src.config import settings
def configure_logging() -> logging.Logger:
    Path('logs').mkdir(exist_ok=True)
    logger=logging.getLogger('supportpearlz'); logger.setLevel(settings.log_level.upper())
    if not logger.handlers:
        fmt=logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        sh=logging.StreamHandler(); sh.setFormatter(fmt); logger.addHandler(sh)
        fh=logging.FileHandler('logs/supportpearlz.log',encoding='utf-8'); fh.setFormatter(fmt); logger.addHandler(fh)
    return logger
