import os
import sys
import logging
from logging.handlers import RotatingFileHandler

def get_logger(name=__name__):
    """
    Factory function to initialize and return a configured logger instance 
    with size-bounded file rotating handlers.
    """
    logger = logging.getLogger(name)
    
    # If the logger has already been initialized, just return it
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Dynamic Path Resolution: 
    # This automatically finds the folder where tracker.py lives, making it 100% portable.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tracker_log_path = os.path.join(base_dir, 'tracker.log')
    error_log_path = os.path.join(base_dir, 'error.log')

    # 1. Rotating Handler for tracker.log (Standard Output Logs)
    stdout_handler = RotatingFileHandler(
        filename=tracker_log_path, 
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=2
    )
    stdout_handler.setFormatter(log_formatter)
    stdout_handler.setLevel(logging.INFO)

    # 2. Rotating Handler for error.log (Warnings and Errors)
    error_handler = RotatingFileHandler(
        filename=error_log_path,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=2
    )
    error_handler.setFormatter(log_formatter)
    error_handler.setLevel(logging.WARNING)

    # 3. Console Handler for manual CLI runs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)

    # Register handlers
    logger.addHandler(stdout_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    return logger