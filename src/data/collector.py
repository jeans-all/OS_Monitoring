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


    @staticmethod
    def collect_system_io(duration=1):
        # I/O Bottlenecks & Disk Saturation
        try:

            # Get initial counters
            io_start = psutil.disk_io_counters()
            time.sleep(duration)

            # Get counters after 1 second
            io_end = psutil.disk_io_counters()
            
            # Calculate per-second metrics
            read_io_bytes = io_end.read_bytes - io_start.read_bytes
            write_io_bytes = io_end.write_bytes - io_start.write_bytes
            
            # Check busy time percentage (busy time percent means busy time / actual time elapsed. In the code below 1000 (= 1 sec) is an elapsed time)
            busy_time = io_end.busy_time - io_start.busy_time
            busy_percentage = (busy_time / (duration*1000)) * 100  # Convert milliseconds to percentage
            
            return {
                "read_io_bytes_per_sec": read_speed,
                "write_io_bytes_per_sec": write_speed,
                "busy_percentage": busy_percentage
            }

        except Exception as e:
            logger.error(f'Error collecting IO metric: {e}')
            return None


    # High Wait Time
    @staticmethod
    def check_io_wait_time():
        cpu_times = psutil.cpu_times()
        iowait = cpu_times.iowait
        
        # Get per-process I/O wait
        processes_io = []
        for proc in psutil.process_iter(['name', 'io_counters']):
            try:
                proc_io = proc.io_counters()
                processes_io.append({
                    'name': proc.name(),
                    'read_time': proc_io.read_time,
                    'write_time': proc_io.write_time
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return {
            'system_iowait': iowait,
            'process_io_times': sorted(processes_io, 
                                    key=lambda x: x['read_time'] + x['write_time'], 
                                    reverse=True)[:5]  # Top 5 processes
    }
