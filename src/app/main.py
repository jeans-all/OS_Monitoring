import streamlit as st
import time
from pathlib import Path
import sys

# Add root directory of project to PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.data.collector import SystemDataCollector
from src.data.storage import DataStorage
from src.visualization.charts import ChartGenerator
from config.settings import COLLECTION_INTERVAL

def main():
    st.title("System Monitoring Dashboard")

    # Reset data storage and dashboard generator
    storage = DataStorage()
    chart_gen = ChartGenerator()

    # Real time data collection and saving
    collector = SystemDataCollector()
    data = collector.collect_system_data()

    if data:
        storage.save_to_db(data)    
    
    # load stored data
    df = storage.load_data()

    # new feature
    data_mem = collector.collect_system_memory()
    if data_mem:
        storage.save_to_db_mem(data_mem)
        
    df_mem = storage.load_data_mem()

    if sys.platform.startswith('linux') or sys.platform == 'win32':
        data_process_io_wait = collector.collect_process_io_wait_time()
    
        if data_process_io_wait:
            storage.save_to_db_process_io_wait(data_process_io_wait)
   
   
    data_system_io_wait_time = collector.collect_system_io_wait_time()
    if data_system_io_wait_time:
        storage.save_to_db_system_io_wait(data_system_io_wait_time)
    
    (df_process_io_wait, df_system_io_wait) = storage.load_data_io_wait()
        

    if not df.empty:

        # current system status
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("CPU Usage", f"{data['cpu_percent']}%")
        with col2:
            st.metric("Memory Usage", f"{data['memory_percent']}%")
        with col3:
            st.metric("Disk Usage", f"{data['disk_usage']}%")


    if not df_mem.empty:
        memory_composition_chart = chart_gen.create_memory_composition_chart(df_mem, unit = 'GB')
        memory_swap_comparison_chart = chart_gen.create_memory_swap_comparison_chart(df_mem, unit = 'GB')

        st.plotly_chart(memory_composition_chart)
        st.plotly_chart(memory_swap_comparison_chart)

        # cpu-memory chart
        cpu_memory_chart = chart_gen.create_cpu_memory_chart(df)
        st.plotly_chart(cpu_memory_chart)

        # network chart
        network_chart = chart_gen.create_network_chart(df)
        st.plotly_chart(network_chart, use_container_width=True)



    # process hierarchy 
    processes = collector.get_process_data()
    if len(processes) > 0:

        root = chart_gen.create_process_tree(processes)

        fig = chart_gen.create_process_chart(root)
        st.plotly_chart(fig, use_container_width=True)


    if not df_process_io_wait.empty:
        print("draw a chart here")   
    else:
        print("psutil doesn't support monitoring of per-process IO wait information")

    if not df_system_io_wait.empty:
        fig = chart_gen.create_system_io_wait_char(df_system_io_wait)
        st.plotly_chart(fig, use_container_width=True)


    time.sleep(COLLECTION_INTERVAL)
    st.rerun()

if __name__ == "__main__":
    main()