import psutil
import time 
from datetime import datetime
from pathlib import Path 
import logging
import sys

from config.settings import LOG_DIR, LOG_FORMAT


# logging setup
logging.basicConfig(
    level=logging.INFO, 
    format=LOG_FORMAT, 
    handlers=[
        logging.FileHandler(LOG_DIR / 'collector.log'), 
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemDataCollector:
    @staticmethod
    def collect_system_data():
        try:
            return {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                'cpu_percent': psutil.cpu_percent(interval=1), 
                'memory_percent': psutil.virtual_memory().percent, 
                'disk_usage': psutil.disk_usage('/').percent, 
                'network_bytes_sent': psutil.net_io_counters().bytes_sent, 
                'network_bytes_recv': psutil.net_io_counters().bytes_recv, 
            }
        except Exception as e:
            logger.error(f'Error collecting system data: {e}')
            return None
    
    @staticmethod
    def collect_system_memory():
        try: 

            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            res = {

                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 

                # 상세 메모리 메트릭
                'memory_total': mem.total,  # GB 단위
                'memory_available': mem.available,
                'memory_used': mem.used,
                'memory_cached':  -1,
                'memory_buffers': -1,
                'memory_percent': mem.percent,
                
                # 스왑 메모리 메트릭
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_free': swap.free,
                'swap_percent': swap.percent
            }
            if hasattr(mem, 'cached'): mem['memory_cached'] = mem.cached 
            if hasattr(mem, 'buffers'): mem['memory_cached'] = mem.buffers  

            return res

        except Exception as e:
            logger.error(f'Error collecting system memory: {e}')
            return None
    
