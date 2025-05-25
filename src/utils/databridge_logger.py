import logging
import os

def setup_databridge_logger(config=None):
    if config is None:
        config = {}
    
    log_level = getattr(logging, config.get('logging', {}).get('level', 'INFO'))
    log_file = config.get('logging', {}).get('file', 'databridge.log')
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Get the databridge logger
    logger = logging.getLogger('databridge')
    
    # Remove existing handlers to prevent duplicates and allow file cleanup
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    
    # Configure the logger directly instead of using basicConfig
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    
    # Create and configure file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Create and configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logger.setLevel(log_level)
    return logger
