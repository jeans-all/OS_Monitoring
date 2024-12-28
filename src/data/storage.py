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
        self._create_table_mem()
        self._create_table_system_io_wait()
    
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
            conn.commit()

    def _create_table_mem(self):
        query = '''
            CREATE TABLE IF NOT EXISTS memory_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            memory_total REAL NOT NULL, 
            memory_available REAL NOT NULL,
            memory_used REAL NOT NULL,
            memory_cached REAL NOT NULL,
            memory_buffers REAL NOT NULL,
            memory_percent REAL NOT NULL,
            swap_total REAL NOT NULL,
            swap_used REAL NOT NULL,
            swap_free REAL NOT NULL,
            swap_percent REAL NOT NULL
        )
        '''

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query)
            conn.commit()
    
    def save_to_db(self, data):
        if data is None: return
        query = '''
        INSERT INTO system_metrics (timestamp, cpu_percent, memory_percent, disk_usage, network_bytes_sent, network_bytes_recv)
        VALUES (:timestamp, :cpu_percent, :memory_percent, :disk_usage, :network_bytes_sent, :network_bytes_recv)
        '''
        try:

            logger.debug(f"Attempting to save data: {data}")
            logger.debug(f"Data type: {type(data)}")
            logger.debug(f"Data keys: {list(data.keys())}")
            
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
                conn.commit()
            logger.info("Data saved successfully")
        
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            logger.error(f'Query was: {query}')


    def save_to_db_mem(self, data):
        if data is None: 
            return
        
        query = '''
        INSERT INTO memory_metrics (
            timestamp,
            memory_total, 
            memory_available, 
            memory_used, 
            memory_cached, 
            memory_buffers, 
            memory_percent,
            swap_total, 
            swap_used, 
            swap_free, 
            swap_percent
        )
        VALUES (
            :timestamp,
            :memory_total, 
            :memory_available, 
            :memory_used, 
            :memory_cached, 
            :memory_buffers, 
            :memory_percent,
            :swap_total, 
            :swap_used, 
            :swap_free, 
            :swap_percent
        )
        '''
        
        try:
            logger.debug(f"Attempting to save data: {data}")
            logger.debug(f"Data type: {type(data)}")
            logger.debug(f"Data keys: {list(data.keys())}")
            
            params = {
                'timestamp': data['timestamp'],
                'memory_total': data['memory_total'],
                'memory_available': data['memory_available'],
                'memory_used': data['memory_used'],
                'memory_cached': data['memory_cached'],
                'memory_buffers': data['memory_buffers'],
                'memory_percent': data['memory_percent'],
                'swap_total': data['swap_total'],
                'swap_used': data['swap_used'],
                'swap_free': data['swap_free'],
                'swap_percent': data['swap_percent']
            }
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(query, params)
                conn.commit()  # Ensure changes are committed
            
            logger.info("Memory metrics saved successfully")
        
        except Exception as e:
            logger.error(f"Error saving memory metrics: {e}")
            logger.error(f'Query was: {query}')

   
    def save_to_db_system_io_wait(self, data):
        if data is None: return

        querySystem = '''
            INSERT INTO system_io_wait (
                timestamp, 
                read_io_bytes_per_sec,
                write_io_bytes_per_sec,
                busy_percentage
            ) 
            VALUES (
                :timestamp, 
                :read_io_bytes_per_sec,
                :write_io_bytes_per_sec,
                :busy_percentage            )
        '''
        
        params1 = {
            'timestamp': data['timestamp'],
            'read_io_bytes_per_sec': data['read_io_bytes_per_sec'],
            'write_io_bytes_per_sec': data['write_io_bytes_per_sec'],
            'busy_percentage': data['busy_percentage']
        }
        try: 
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(querySystem, params1)
            
            logger.info("system-wide io wait metric saved successfully")

        except Exception as e:
            logger.error(f'Error saving system io wait metrics: {e}')
            logger.error(f'Query was {querySystem}')

    def _create_table_system_io_wait(self):

        query = '''
        CREATE TABLE IF NOT EXISTS system_io_wait (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            timestamp DATETIME NOT NULL,
            read_io_bytes_per_sec REAL NOT NULL,
            write_io_bytes_per_sec REAL NOT NULL,
            busy_percentage REAL NOT NULL
        )
        '''

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query)
            conn.commit()


    def save_to_db_process_io_wait(self, data):
        queryProcess = '''
            INSERT INTO process_io_wait (
                timestamp, 
                process_name, 
                io_wait_time_per_process)
            VALUES (
                :timestamp, 
                :process_name, 
                :process_io_wait_time
            )
        '''
        params2 = {
            'timestamp': data['timestamp'],
            'process_name': None,
            'process_io_wait_time': None
        }

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(queryProcess, params2)
                
                for p in data['process_io_times']:
                    params2['process_name'] = p['name']
                    params2['process_io_wait_time'] = p['read_time'] + p['write_time']

                    conn.execute(queryProcess, params2)

            logger.info("process io wait metric saved successfully")
        
        except Exception as e:
            logger.error(f'Error saving io wait metrics: {e}')
            logger.error(f'Query was {queryProcess}')

    def load_data(self, limit=100):
        query = f"SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT {limit}"
        try:
            with sqlite3.connect(self.db_path) as conn:
                return pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return pd.DataFrame()

    def load_data_mem(self, limit=100):
        query = f"SELECT * FROM memory_metrics ORDER BY timestamp DESC LIMIT {limit}"
        try: 
            with sqlite3.connect(self.db_path) as conn:
                return pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Error loading memory metrics: {e}")
            return pd.DataFrame()
    

    def load_data_io_wait(self, limit=100):
        query1 = f"SELECT * FROM process_io_wait ORDER BY timestamp DESC LIMIT {limit}"
        try:
            with sqlite3.connect(self.db_path) as conn:
                df1 = pd.read_sql_query(query1, conn)
        except Exception as e:
            if 'no such table' in str(e): 
                logger.info('Process io wait monitoring not available on Mac')
            else:
                logger.info(f"Error loading io process wait metric: {e}")
            df1 = pd.DataFrame()
        
        query2 = f"SELECT * FROM system_io_wait ORDER BY timestamp DESC LIMIT {limit}"

        try:
            with sqlite3.connect(self.db_path) as conn:
                df2 = pd.read_sql_query(query2, conn)
        except Exception as e:
            logger.error(f"Error loading system io wait metric: {e}")
            df2 = pd.DataFrame()

        return (df1, df2)

    # since process graph is real-time, we don't need to store it into database
    