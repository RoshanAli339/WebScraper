from prophet import Prophet
import pandas as pd
import plotly.express as px
from plotly import graph_objs as go


def predictIndex(indexHistory):
    indexHistory = indexHistory[['Date', 'Close']]
    indexHistory.columns = ['ds', 'y']
    indexHistory['ds'] = pd.to_datetime(indexHistory['ds'])
    m = Prophet()
    m.fit(indexHistory)
    future = m.make_future_dataframe(periods=365)
    forecast = m.predict(future)
    fig = px.line(forecast[['ds', 'yhat']], x='ds', y='yhat', title='Price Prediction')
    fig.layout.update(xaxis_rangeslider_visible=True)
    fig.show()


def plotRawData(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
    fig.layout.update(title_text='Historical Data', xaxis_rangeslider_visible=True)
    fig.show()
