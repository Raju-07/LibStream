import logging
import logging.config
from pathlib import Path
from typing import Any, Dict

# Define log directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"
AUTH_FILE = LOG_DIR / 'auth_file.log'
DATABASE_FILE = LOG_DIR / 'database_file.log'


def setup_logging(debug: bool = False) -> None:
    """
    Configure logging with conditional output.
    
    Args:
        debug: If True, logs to console. If False, logs to file.
    """
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "standard",
                "filename": str(LOG_FILE),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "auth_file":{
                'class': "logging.handlers.RotatingFileHandler",
                'level': "INFO",
                'formatter':"standard",
                'filename': str(AUTH_FILE),
                'maxBytes': 10485760, #10MB,
                'backupCount':5,
            },
            "database_file":{
                'class': "logging.handlers.RotatingFileHandler",
                'level': "INFO",
                'formatter':"standard",
                'filename': str(DATABASE_FILE),
                'maxBytes': 10485760, #10MB,
                'backupCount':5,
            },
        },
        "loggers": {
            "uvicorn.error": {
                "handlers": ["console" if debug else "file"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": False,
            },
            "app": {
                "handlers": ["console" if debug else "file"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": False,
            },
            "app.auth":{
                'handlers': ["console" if debug else "auth_file"],
                'level': "DEBUG" if debug else "INFO",
                'propagate':False,
            },
            "app.database":{
                "handlers": ["console" if debug else "database_file"],
                'level': "DEBUG" if debug else "INFO",
                'propagate': False,
            },
            'watchfiles':{
                'level': "WARNING",
                'propagate': False,
            },
        },
        "root": {
            "level": "DEBUG" if debug else "INFO",
            "handlers": ["console" if debug else "file"],
        },
    }
    
    logging.config.dictConfig(logging_config)