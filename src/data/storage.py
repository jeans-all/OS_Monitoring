import sqlite3
import pandas as pd 
from pathlib import Path 
import logging
from config.settings import DB_PATH, LOG_DIR, LOG_FORMAT 

# setup logging
logging.basicConfig(
    level=logging.INFO, 
    format=LOG_FORMAT, 
    handlers=[
        logging.FileHandler(LOG_DIR / 'storage.log'), 
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataStorage:
    def __init__(self):
        self.db_path = DB_PATH
        self._create_table()
    
    def _create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            timestamp DATETIME NOT NULL,
            cpu_percent REAL NOT NULL,
            memory_percent REAL NOT NULL,
            disk_usage REAL NOT NULL,
            network_bytes_sent REAL NOT NULL,
            network_bytes_recv REAL NOT NULL  
        )
        '''

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query)
    
    def save_to_db(self, data):
        if data is None: return
        print(data)
        query = '''
        INSERT INTO system_metrics (timestamp, cpu_percent, memory_percent, disk_usage, network_bytes_sent, network_bytes_recv)
        VALUES (:timestamp, :cpu_percent, :memory_percent, :disk_usage, :network_bytes_sent, :network_bytes_recv)
        '''
        # (:timestamp, :cpu_percent, :memory_percent, :disk_usage, :network_bytes_sent, :network_bytes_recv)
        try:

            logger.info(f"Attempting to save data: {data}")
            logger.info(f"Data type: {type(data)}")
            logger.info(f"Data keys: {list(data.keys())}")
            
            params = {
                'timestamp': data['timestamp'],
                "cpu_percent": data["cpu_percent"],
                "memory_percent": data["memory_percent"],
                "disk_usage": data["disk_usage"],
                "network_bytes_sent": data["network_bytes_sent"],
                "network_bytes_recv": data["network_bytes_recv"]
            }
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(query, params)
            logger.info("Data saved successfully")
        
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            logger.error(f'Query was: {query}')
    
    def load_data(self, limit=100):
        query = f"SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT {limit}"
        try:
            with sqlite3.connect(self.db_path) as conn:
                return pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return pd.DataFrame()
