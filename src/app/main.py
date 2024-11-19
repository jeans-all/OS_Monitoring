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

    if not df.empty:
        # cpu-memory chart
        cpu_memory_chart = chart_gen.create_cpu_memory_chart(df)
        st.plotly_chart(cpu_memory_chart)

        # network chart
        network_chart = chart_gen.create_network_chart(df)
        st.plotly_chart(network_chart)

        # current system status
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("CPU Usage", f"{data['cpu_percent']}%")
        with col2:
            st.metric("Memory Usage", f"{data['memory_percent']}%")
        with col3:
            st.metric("Disk Usage", f"{data['disk_usage']}%")

    time.sleep(COLLECTION_INTERVAL)
    st.rerun()

if __name__ == "__main__":
    main()