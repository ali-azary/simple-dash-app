import sys
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import webbrowser
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl  
import requests
import pandas as pd
import warnings
warnings.filterwarnings(action='ignore')
from datetime import datetime
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
url_stocks = 'https://finance.yahoo.com/markets/stocks/most-active/?start=0&count=100'
stocks = pd.read_html(requests.get(url_stocks, headers=headers).text)[0]['Symbol'].to_list()


# Initialize the app with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])

def common_layout(fig):
    """Applies a common layout to all figures"""
    fig.update_layout(
        title_x=0.5,  # Center title
        width=800,  # Consistent width
        height=600,  # Consistent height
        template="plotly_white"  # Consistent theme
    )
    return fig

def empty_figure():
    """Initial placeholder figure with same layout as main graph"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[], y=[], mode="lines"))
    fig.update_layout(title="Loading Data...")
    return common_layout(fig)

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.H1("Stock Market Dashboard", className="text-center mb-4"), width=12
        )
    ]),

    dbc.Row([
        # Sidebar for dropdown
        dbc.Col([
            html.H4("Select a Stock", className="mb-2"),
            dcc.Dropdown(stocks, 'AAPL', id='dropdown-selection', className="mb-4"),
            html.H4("Select Start Date", className="mb-2"),
            dcc.DatePickerSingle(
                id='start-date-picker',
                min_date_allowed=datetime(2000, 1, 1),
                max_date_allowed=datetime.today(),
                initial_visible_month=datetime(2020, 1, 1),
                date="2020-01-01"
            ),
            html.H4("Select End Date", className="mb-2"),
            dcc.DatePickerSingle(
                id='end-date-picker',
                min_date_allowed=datetime(2000, 1, 1),
                max_date_allowed=datetime.today(),
                initial_visible_month=datetime.today(),
                date=datetime.today().strftime("%Y-%m-%d")
            )

        ], width=3, className="bg-light p-3 rounded"),

        # Main graph area
        dbc.Col([
            dcc.Graph(id="stock-graph", figure=empty_figure())  # Default figure
        ], width=9)
    ], align="center")
], fluid=True)

@callback(
    Output('stock-graph', 'figure'),
    [Input('dropdown-selection', 'value'),
     Input('start-date-picker', 'date'),
     Input('end-date-picker', 'date')]
)

def update_graph(symbol, start_date, end_date):
    if not symbol or not start_date or not end_date:
        return empty_figure()
    
    period1 = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    period2 = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

    url_history = 'https://finance.yahoo.com/quote/' + symbol + '/history/?period1=' + str(period1) + '&period2=' + str(period2)

    data = pd.read_html(requests.get(url_history, headers=headers).text)[0]
    data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    data.iloc[:, 1:] = data.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
    data['Date'] = pd.to_datetime(data['Date'])
    fig = go.Figure(data=[go.Scatter(x=data['Date'], y=data["Adj Close"], mode="lines")])
    fig.update_layout(title=f"Stock Prices: {symbol}")
    fig.update_layout(
            title_x=0.5,  # Center title
            width=600,  # Set width
            height=400   # Set height
        )

    return common_layout(fig)  

class DashWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Standalone Dash App")
        self.setGeometry(100, 100, 1200, 800)  # Window size

        # Web View
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://127.0.0.1:8050/"))  # Load Dash app

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

server = app.server
        
if __name__ == '__main__':
    app.run_server(debug=True)
    app = QApplication(sys.argv)
    main_window = DashWindow()
    main_window.show()
    sys.exit(app.exec())
