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
        self.allIndices = pd.DataFrame()
        self.equityShares = {}
        self.sme = pd.DataFrame()

    def bmiToday(self):
        url = "https://www.nseindia.com/api/allIndices"
        response = self.session.get(url=url)
        data = response.json()
        data = data['data']
        indexName, indexSymbol, lastPrice, percentChange, opening, high, low, prevClose, pChange365 = [], [], [], [], [], [], [], [], []
        for index in data:
            indexName.append(index['index'])
            indexSymbol.append(index['indexSymbol'])
            lastPrice.append(index['last'])
            percentChange.append(index['percentChange'])
            opening.append(index['open'])
            high.append(index['high'])
            low.append(index['low'])
            prevClose.append(index['previousClose'])
            pChange365.append(index['perChange365d'])
        self.allIndices = pd.DataFrame({
            'Index': indexName,
            'Symbol': indexSymbol,
            'Last Price': lastPrice,
            '%Change': percentChange,
            'Open': opening,
            'High': high,
            'Low': low,
            'Perv. Close': prevClose,
            'Percent Change/Yr': pChange365
        })

    def getHistoricalIndex(self, index):
        encodedIndex = urllib.parse.quote(index, safe='')
        today = datetime.now().strftime('%d-%m-%Y')
        oneYearAgo = (datetime.now() - timedelta(days=365)).strftime('%d-%m-%Y')

        apiUrl = f"https://www.nseindia.com/api/historical/indicesHistory?indexType={encodedIndex}&from={oneYearAgo}&to={today}"

        response = self.session.get(url=apiUrl)
        data = response.json()
        data = data['data']['indexCloseOnlineRecords']
        dt, closing = [], []
        for day in data:
            d = datetime.strptime(day['EOD_TIMESTAMP'], '%d-%b-%Y')
            dt.append(d.strftime('%Y-%m-%d'))
            closing.append(day['EOD_CLOSE_INDEX_VAL'])
        data = {
            'Date': dt,
            'Closing Price': closing
        }
        return pd.DataFrame(data)

    def getHistoricalStock(self, symbol):
        today = datetime.now().strftime('%d-%m-%Y')
        oneYearAgo = (datetime.now() - timedelta(days=365)).strftime('%d-%m-%Y')
        apiUrl = f"https://www.nseindia.com/api/historical/securityArchives?from={oneYearAgo}&to={today}&symbol={symbol}&dataType=priceVolume&series=ALL"
        response = self.session.get(url=apiUrl)
        data = response.json()
        data = data['data']
        dt, closing = [], []
        for day in data:
            dt.append(day['CH_TIMESTAMP'])
            closing.append(day['CH_CLOSING_PRICE'])
        data = {
            'Date': dt,
            'Closing Price': closing
        }
        return pd.DataFrame(data)

    def topIndicesToday(self):
        self.all_indices()
        sortedIndices = self.allIndices.sort_values(by='Last Price', ascending=False)
        sortedIndices = sortedIndices.head(10)
        index_names = sortedIndices['Index']
        market_capitalization = sortedIndices['Last Price']  # You can use other relevant data as well

        # Create a bar chart to visualize market capitalization by index
        plt.figure(figsize=(12, 6))
        plt.bar(index_names, market_capitalization, color='skyblue')
        plt.xlabel('Indices')
        plt.ylabel('Market Capitalization (Open)')
        plt.title('Market Overview: Market Capitalization by Index')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Show the chart
        plt.show()

    def topStocksToday(self, eqIndex):
        self.equity(eqIndex)
        df = self.equityShares[eqIndex]
        sortedDf = df.sort_values(by='Last Price', ascending=False)
        sortedDf = sortedDf.head(10)
        symbols = sortedDf['SYMBOL']
        market_capitalization = sortedDf['Last Price']  # You can use other relevant data as well

        # Create a bar chart to visualize market capitalization by index
        plt.figure(figsize=(12, 6))
        plt.bar(symbols, market_capitalization, color='skyblue')
        plt.xlabel('Symbols')
        plt.ylabel('Market Capitalization (Open)')
        plt.title('Market Overview: Market Capitalization by Equity Stock')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Show the chart
        plt.show()

    def equity(self, eqIndex):
        encodedIndex = urllib.parse.quote(eqIndex, safe='')
        apiUrl = "https://www.nseindia.com/api/equity-stockIndices?index="+encodedIndex
        response = self.session.get(url=apiUrl)
        data = response.json()
        data = data['data']
        symbol, lastPrice, change, percentChange, opening, high, low, prevClose, totalTradeVol, totalTradeVal, pChange365 = \
            ([] for i in range(11))
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
            pChange365.append(index['perChange365d'])
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
            'Percent Change/Yr': pChange365
        }
        df = pd.DataFrame(data)
        df = df.drop(0)
        self.equityShares.update({eqIndex: df})

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

    def dailyChart(self, symbol, type='stock', preOpen=False):
        encodedSymbol = urllib.parse.quote(symbol, safe='')
        apiUrl = "https://www.nseindia.com/api/chart-databyindex?index="+encodedSymbol
        if type=='stock':
            apiUrl += 'EQN'
        if preOpen:
            apiUrl += "&preopen=true"
        response = self.session.get(apiUrl)
        data = response.json()
        data = data['grapthData']
        df = pd.DataFrame(data)
        df.columns = ["Timestamp", "Price"]
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms').dt.strftime('%H:%M:%S')
        timeStamps = [datetime.strptime(i, '%H:%M:%S') for i in list(df['Timestamp'])]
        time_difference = timeStamps[-1] - timeStamps[0]

        if time_difference <= timedelta(minutes=30):
            interval = timedelta(minutes=5)
        elif time_difference <= timedelta(hours=4):
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

    def smeToday(self):
        apiUrl = "https://www.nseindia.com/api/live-analysis-emerge"
        response = self.session.get(url=apiUrl)
        data = response.json()['data']
        symbol, lastPrice, openPrice, dayHigh, dayLow, change, pChange, totalTradeVol, totalTradeVal = ([] for i in
                                                                                                        range(9))
        for i in data:
            symbol.append(i['symbol'])
            lastPrice.append(i['lastPrice'])
            openPrice.append(i['open'])
            dayHigh.append(i['dayHigh'])
            dayLow.append(i['dayLow'])
            change.append(i['change'])
            pChange.append(i['pChange'])
            totalTradeVol.append(i['totalTradedVolume'])
            totalTradeVal.append(i['totalTradedValue'])
        self.sme = pd.DataFrame({
            'Symbol': symbol,
            'Last Price': lastPrice,
            'Opening Price': openPrice,
            'Day High Price': dayHigh,
            'Day Low Price': dayLow,
            'Change in value': change,
            'Percentage Change': pChange,
            'Total Traded Volume': totalTradeVol,
            'Total Traded Value': totalTradeVal
        })


if __name__ == '__main__':
    nse = NSE()
    data = nse.getHistoricalStock('TCS')
    print(data)
