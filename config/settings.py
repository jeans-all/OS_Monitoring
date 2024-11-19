import os
from pathlib import Path

# root directory of project
ROOT_DIR = Path(__file__).parent.parent

# data directory
DATA_DIR = ROOT_DIR / 'data'
LOG_DIR = DATA_DIR / 'logs'

# database path
DB_PATH = DATA_DIR / 'system_info.db'

# data collection interval (sec)
COLLECTION_INTERVAL = 5 

# logging setting
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
