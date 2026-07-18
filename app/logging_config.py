import logging
import logging.config
from pathlib import Path
from typing import Dict,Any
from app.core.config import settings


#define log directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'app.log'


def setup_logging(debug: bool = settings.debug) -> None:
    
    'log formatting'
    log_format = "%{asctime}s - %(name)s - %(levelname)s - %(message)s"

    logging_config: Dict[str, Any] = {
        'version':1,
        'disable_existing_logger':False,
        'formatters':{
            'standard':{
                'format':log_format,
                'datefmt': "%Y-%m-%d %H:%M:%S",
            },
        },
        'handlers':{
            'console':{
                'class':"logging.StreamHandler",
                'level':"DEBUG",
                'formatter': 'standard',
                'stream':'ext://sys.stdout',
            },
            'file':{
                'class': "logging.handlers.RotatingFileHandler",
                'level': "INFO",
                'formatter': 'standard',
                'filename': str(LOG_FILE),
                'maxBytes':10485760, #10 MB
                'backupCount':5,
            },
        },
        'loggers':{
            'uvicorn':{
                'handlers':['console' if debug else 'file'],
                'level':"DEBUG" if debug else "INFO",
                'propagate': False,
            },
            'uvicorn.access':{
                'handlers':['console' if debug else 'file'],
                'level': "DEBUG" if debug else "INFO",
                'propagate': False,
            },
            'app':{
                'handlers':['console' if debug else 'file'],
                'level': "DEBUG" if debug else "INFO",
                'propagete': False,
            },
            
        },
        'root':{
                'handlers':['console' if debug else 'file'],
                'level':"DEBUG" if debug else "INFO",
            },
    }

    logging.config.dictConfig(logging_config)