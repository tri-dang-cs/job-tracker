import logging
import sys
import os

def get_logger(name, log_to_console=True, filename=None, level=logging.DEBUG):
    # check environment variables
    log_to_console = os.environ.get('LOG_TO_CONSOLE') is not None
    filename = os.environ.get('LOG_FILENAME', filename)
    level = os.environ.get('LOG_LEVEL', level)

    match os.environ.get('LOG_LEVEL', '').upper():
        case 'DEBUG':
            level = logging.DEBUG
        case 'INFO':
            level = logging.INFO
        case 'WARNING':
            level = logging.WARNING
        case 'ERROR':
            level = logging.ERROR
        case 'CRITICAL':
            level = logging.CRITICAL

    # 
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if filename:
        file_handler = logging.FileHandler('app.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger