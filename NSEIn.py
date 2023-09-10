import requests
import urllib.parse


class NSE:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }
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

    def equity(self, index):
        index = urllib.parse.quote(index, safe='')
        url = "https://www.nseindia.com/api/equity-stockIndices?index="+index
        response = self.session.get(url=url)
        data = response.json()['data']
        symbol, lastPrice, change, percentChange, opening, high, low, prevClose, totalTradeVol, totalTradeVal = \
            [], [], [], [] , [], [], [], [] ,[] ,[]
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
        self.equityShares = {
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


if __name__ == '__main__':
    nse = NSE()
    nse.equity('NIFTY 50')
    print(nse.equityShares)
