import plotly.express as px
import plotly.graph_objects as go 
from plotly.subplots import make_subplots

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
        return px.line(df, x='timestamp', y=['network_bytes_sent', 'network_bytes_recv'], title='Network Usage Over Time')


    @staticmethod
    def create_memory_composition_chart(df, unit='MB'):
        # conver unit 
        def convert_bytes(x, to_unit):
            units = {
                'B': 1,
                'KB': 1024,
                'MB': 1024**2,
                'GB': 1024**3
            }
            return x / units[to_unit]

        # copy dataframe and convert unit of data
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
        
        # 메모리 사용률 계산 (퍼센트)

        # df_converted['memory_usage_percent'] = (df_converted['memory_used'] / df_converted['memory_total']) * 100
        
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
        
        fig.update_layout(
            title=f'Memory and Swap Usage Over Time ({unit})',
            yaxis_title=f"Memory Usage ({unit})",
            yaxis2_title=f"Swap Usage ({unit})"
        )
        
        return fig

# 사용 예시:
# 단위를 지정하여 차트 생성
# chart1 = create_memory_composition_chart(df, unit='GB')
# chart2 = create_memory_swap_comparison_chart(df, unit='MB')
