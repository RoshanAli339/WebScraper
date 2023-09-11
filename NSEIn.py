from datetime import  datetime, timedelta
import pandas as pd
import requests
import urllib.parse
import matplotlib.pyplot as plt


class NSE:

    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.allIndices = {}
        self.equityShares = {}

    def all_indices(self):
        url = "https://www.nseindia.com/api/allIndices"
        response = self.session.get(url=url)
        data = response.json()['data']
        indexName, indexSymbol, current, percentChange, opening, high, low, prevClose = [], [], [], [], [], [], [], []
        for index in data:
            indexName.append(index['index'])
            indexSymbol.append(index['indexSymbol'])
            current.append(index['last'])
            percentChange.append(index['percentChange'])
            opening.append(index['open'])
            high.append(index['high'])
            low.append(index['low'])
            prevClose.append(index['previousClose'])
        self.allIndices.update({
            'Index': indexName,
            'Symbol': indexSymbol,
            'Current': current,
            '%Change': percentChange,
            'Open': opening,
            'High': high,
            'Low': low,
            'Perv. Close': prevClose
        })

    def equity(self, eqIndex):
        encodedIndex = urllib.parse.quote(eqIndex, safe='')
        apiUrl = "https://www.nseindia.com/api/equity-stockIndices?index="+encodedIndex
        response = self.session.get(url=apiUrl)
        data = response.json()
        data = data['data']
        symbol, lastPrice, change, percentChange, opening, high, low, prevClose, totalTradeVol, totalTradeVal = \
            ([] for i in range(10))
        for index in data:
            symbol.append(index['symbol'])
            lastPrice.append(index['lastPrice'])
            change.append(index['change'])
            percentChange.append(index['pChange'])
            opening.append(index['open'])
            high.append(index['dayHigh'])
            low.append(index['dayLow'])
            prevClose.append(index['previousClose'])
            totalTradeVol.append(index['totalTradedVolume'])
            totalTradeVal.append(index['totalTradedValue']/10**5)
        data = {
            'SYMBOL': symbol,
            'Last Price': lastPrice,
            'CHANGE': change,
            '%Change': percentChange,
            'Open': opening,
            'Day High': high,
            'Day Low': low,
            'Prev. Close': prevClose,
            'Volume(shares)': totalTradeVol,
            'Value(Rupees)': totalTradeVal,
        }
        self.equityShares.update({eqIndex: data})

    def get_quote(self, symbol):
        symbol = urllib.parse.quote(symbol, safe='')
        apiUrl = "https://www.nseindia.com/api/quote-equity?symbol="+symbol
        tradeInfoUrl = apiUrl + "&section=trade_info"
        response = self.session.get(url=apiUrl)
        tradeResponse = self.session.get(url=tradeInfoUrl)
        data = response.json()
        tradeData = tradeResponse.json()
        tradeData = tradeData['marketDeptOrderBook']['tradeInfo']
        genInfo = {
            'Company Name': [data['info']['companyName']],
            'Symbol': [data['info']['symbol']],
            'Industry': [data['metadata']['industry']],
            'ISIN Code': [data['info']['isin']]
        }
        yearlyInfo = {
            'Yearly Max Value': [data['priceInfo']['weekHighLow']['max']],
            'Max Value on': [data['priceInfo']['weekHighLow']['maxDate']],
            'Yearly Min Value': [data['priceInfo']['weekHighLow']['min']],
            'Min Value on': [data['priceInfo']['weekHighLow']['minDate']]
        }
        priceInfo = {
            'Last Price': [data['priceInfo']['lastPrice']],
            'Opening Price': [data['priceInfo']['open']],
            'Value Change': [data['priceInfo']['change']],
            'Percent Change': [data['priceInfo']['pChange']],
            'Today Highest Price': [data['priceInfo']['intraDayHighLow']['max']],
            'Today Least Price': [data['priceInfo']['intraDayHighLow']['min']],
            'Volume Weighted Average Price': [data['priceInfo']['vwap']]
        }
        tradeInfo = {
            'Total Traded Volume': [tradeData['totalTradedVolume']],
            'Total Traded Value(Rs. Lakhs)': [tradeData['totalTradedValue']],
            'Total Market Capital(Rs. Lakhs)': [tradeData['totalMarketCap']]
        }
        print(pd.DataFrame(genInfo).T)
        print(pd.DataFrame(priceInfo).T)
        print(pd.DataFrame(tradeInfo).T)
        print(pd.DataFrame(yearlyInfo).T)

    def dailyChart(self, symbol):
        encodedSymbol = urllib.parse.quote(symbol, safe='')
        apiUrl = "https://www.nseindia.com/api/chart-databyindex?index="+encodedSymbol
        response = self.session.get(apiUrl)
        data = response.json()
        data = data['grapthData']
        df = pd.DataFrame(data)
        df.columns = ["Timestamp", "Price"]
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms').dt.strftime('%H:%M:%S')
        timeStamps = [datetime.strptime(i, '%H:%M:%S') for i in list(df['Timestamp'])]
        time_difference = timeStamps[-1] - timeStamps[0]

        if time_difference <= timedelta(hours=4):
            interval = timedelta(minutes=30)
        elif time_difference <= timedelta(hours=8):
            interval = timedelta(hours=1)
        else:
            interval = timedelta(hours=2)
        num_ticks = int(time_difference.total_seconds() / interval.total_seconds())
        step = len(df) // num_ticks
        selected_data = df.iloc[::step]

        # Create a plot
        plt.figure(figsize=(10, 6))
        plt.plot(df['Timestamp'], df['Price'])

        # Customize the X-axis labels using the selected data
        plt.xticks(selected_data['Timestamp'], selected_data['Timestamp'], rotation=45)
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    nse = NSE()
    nse.dailyChart('ADANIPORTSEQN')
