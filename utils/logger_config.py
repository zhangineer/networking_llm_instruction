# logger_config.py

import logging
import logging.handlers


def create_logger(filename, name=__name__):
    # Create a logger object
    logger = logging.getLogger(name)

    logger.propagate = False

    # Set the desired logging level to DEBUG for dev purposes, this should be changed to WARNING in production
    # this is only the threshold, actual message types to log will be defined in each scenario individually
    logger.setLevel(logging.DEBUG)

    log_file = filename
    max_log_size = 5 * 1024 * 1024 # max size = 5 MB
    file_handler = logging.handlers.RotatingFileHandler(filename=log_file, maxBytes=max_log_size, backupCount=5)
    file_handler.setLevel(logging.DEBUG)

    # This is for console logging
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add formatter to the console handler
    file_handler.setFormatter(formatter)
    ch.setFormatter(formatter)  # Optionally set formatter for console handler as well

    # Add console handler to logger
    logger.addHandler(file_handler)
    logger.addHandler(ch)
    logger.info("________________________________Begin Logging________________________________")

    return logger
