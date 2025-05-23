import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name=None, logfile="offensivepython.log"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    if not os.path.exists("logs"):
        os.mkdir("logs")

    fh = RotatingFileHandler(f"logs/{logfile}", maxBytes=5*1024*1024, backupCount=5)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
