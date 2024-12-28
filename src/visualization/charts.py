import plotly.express as px
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
from anytree import Node, PreOrderIter
from anytree.exporter import DictExporter
import streamlit as st

def convert_bytes(x, to_unit: str):
    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3
    }
    return x / units[to_unit]

class ChartGenerator:
    
    @staticmethod
    def create_cpu_memory_chart(df):
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=df['cpu_percent'], 
                name='CPU Usage'
            ), 
            secondary_y=False
        )

        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['memory_percent'], 
                name='Memory Usage'
            ), 
            secondary_y=True
        )

        fig.update_layout(
            title="CPU and Memory Usage Over Time", 
            xaxis_title="Time", 
            yaxis_title="CPU Usage (%)", 
            yaxis2_title="Memory Usage (%)"
        )

        return fig

    @staticmethod
    def create_network_chart(df):
        fig = make_subplots()
        fig.add_trace(go.Scatter(
            x = df['timestamp'], 
            y = df['network_bytes_sent'],
            name = 'Network Bytes Sent',
            mode = 'lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x = df['timestamp'], 
            y = df['network_bytes_recv'],
            name = 'Network Bytes Received',
            mode = 'lines+markers'
        ))

        fig.update_layout(title='Network Usage Over Time', yaxis_type='log')
        
        return fig

    @staticmethod
    def create_memory_composition_chart(df, unit='MB'):
 
        df_converted = df.copy()
        memory_columns = ['memory_used', 'memory_cached', 'memory_buffers', 'memory_available']
        
        for col in memory_columns:
            df_converted[col] = df_converted[col].apply(lambda x: convert_bytes(x, unit))

        fig = px.area(
            df_converted, 
            x='timestamp', 
            y=memory_columns,
            title=f'Memory Usage Composition Over Time ({unit})',
            labels={
                'value': f'Memory ({unit})', 
                'variable': 'Type'
            },
            color_discrete_map={
                'memory_used': 'red',
                'memory_cached': 'blue',
                'memory_buffers': 'green',
                'memory_available': 'gray'
            }
        )
        
        return fig
    @staticmethod
    def create_system_io_wait_char(df):
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['read_io_bytes_per_sec'],
            name='Read IO',
            mode='lines',
            fill='tozeroy', 
            line=dict(color='blue') 
        ))
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['write_io_bytes_per_sec'],
            name='Write IO',
            mode='lines',
            fill='tozeroy',
            line=dict(color='red')
        ))

        # line gragh to represent Busy percentage
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['busy_percentage'],
            name='Busy %',
            mode='lines',
            line=dict(color='green', dash='dash'),
            yaxis='y2',  # second Y-axis
        ))

        # setting up layout
        fig.update_layout(
            title='System IO Performance',
            xaxis_title='Time',
            yaxis=dict(title='IO Bytes/sec', showgrid=False),
            yaxis2=dict(
                title='Busy %',
                overlaying='y',
                side='right',
                range=[0, 5]
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return fig


    @staticmethod
    @st.fragment
    def create_memory_swap_comparison_chart(df, unit='MB'):
        def convert_bytes(x, to_unit):
            units = {
                'B': 1,
                'KB': 1024,
                'MB': 1024**2,
                'GB': 1024**3
            }
            return x / units[to_unit]

        df_converted = df.copy()
        memory_columns = ['memory_used', 'memory_total', 'swap_used', 'swap_total']
        
        for col in memory_columns:
            df_converted[col] = df_converted[col].apply(lambda x: convert_bytes(x, unit))

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        df_converted['memory_usage_percent'] = (df_converted['memory_used'] / df_converted['memory_total']) * 100
        
        # primary y-axis: memory usage
        fig.add_trace(
            go.Scatter(
                x=df_converted['timestamp'], 
                y=df_converted['memory_used'], 
                name=f"Memory Used ({unit})"
            ),
            secondary_y=False,
        )
        
        # secondary y-aix: swap usage
        fig.add_trace(
            go.Scatter(
                x=df_converted['timestamp'], 
                y=df_converted['swap_used'], 
                name=f"Swap Used ({unit})"
            ),
            secondary_y=True,
        )

        # third y-axis: memory usage percentage
        fig.add_trace(
            go.Scatter(
                x=df_converted['timestamp'],
                y=df_converted['memory_usage_percent'],
                name="Memory Usage Percent (%)"
            )
        )
        
        fig.update_layout(
            title=f'Memory and Swap Usage Over Time ({unit})',
            yaxis_title=f"Memory Usage ({unit})",
            yaxis2_title=f"Swap Usage ({unit})"
        )
        
        return fig

    @staticmethod
    def create_process_tree(processes):
        root = None
        for pid, data in processes.items():
            if data['ppid'] not in processes or pid == data['ppid']:
                # This is the root process or a process without a parent
                root = data['node']
            elif data['ppid'] in processes:
                data['node'].parent = processes[data['ppid']]['node']
        
        if root is None:
            # If no root was found, use the process with the lowest PID as root
            root = min(processes.values(), key=lambda x: x['node'].pid)['node']
        
        return root

    @staticmethod
    def create_process_chart(root):
        node_labels = []
        node_colors = []
        source = []
        target = []
        value = []

        for i, node in enumerate(PreOrderIter(root)):
            node_labels.append(f"{node.name}")
            node_colors.append("lightblue" if node.is_leaf else "lightgreen")
            
            if node.parent:
                parent_index = node_labels.index(f"{node.parent.name}")
                source.append(parent_index)
                target.append(i)
                value.append(1)

        fig = go.Figure(data=[go.Sankey(
            node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = node_labels,
            color = node_colors
            ),
            link = dict(
            source = source,
            target = target,
            value = value
        ))])

        fig.update_layout(title_text="Process Hierarchy", font_size=10)
        return fig
    
