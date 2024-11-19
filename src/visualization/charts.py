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
