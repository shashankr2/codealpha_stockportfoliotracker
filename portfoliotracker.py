import requests
import json
import time

class Portfolio:
    def __init__(self):
        self.stocks = []
        
    def add_stock(self, symbol, shares, purchase_price):
        """Add a stock to the portfolio"""
        self.stocks.append({
            'symbol': symbol.upper(),
            'shares': float(shares),
            'purchase_price': float(purchase_price)
        })
    
    def remove_stock(self, symbol):
        """Remove all shares of a specific stock"""
        symbol = symbol.upper()
        initial_count = len(self.stocks)
        self.stocks = [s for s in self.stocks if s['symbol'] != symbol]
        return len(self.stocks) != initial_count
    
    def fetch_prices(self, api_key):
        """Fetch current prices for all stocks in the portfolio"""
        prices = {}
        unique_symbols = list(set([s['symbol'] for s in self.stocks]))
        
        for symbol in unique_symbols:
            try:
                url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
                response = requests.get(url)
                data = response.json()
                
                if 'Global Quote' in data and '05. price' in data['Global Quote']:
                    prices[symbol] = float(data['Global Quote']['05. price'])
                else:
                    print(f"Could not fetch price for {symbol}")
                    prices[symbol] = None
                
                # Respect API rate limit of 5 requests per minute
                time.sleep(12)
                
            except Exception as e:
                print(f"Error fetching price for {symbol}: {str(e)}")
                prices[symbol] = None
                
        return prices
    
    def display(self, api_key):
        """Display portfolio performance"""
        if not self.stocks:
            print("Your portfolio is empty!")
            return
            
        prices = self.fetch_prices(api_key)
        
        total_invested = 0
        total_current = 0
        total_profit_loss = 0
        
        print("\nPortfolio Summary:")
        print("-" * 85)
        print(f"{'Symbol':<8}{'Shares':<12}{'Avg Cost':<12}{'Cur Price':<12}"
              f"{'Invested':<12}{'Cur Value':<12}{'P/L':<12}")
        print("-" * 85)
        
        for stock in self.stocks:
            symbol = stock['symbol']
            shares = stock['shares']
            avg_cost = stock['purchase_price']
            current_price = prices.get(symbol, 0)
            
            invested = shares * avg_cost
            current_value = shares * current_price if current_price else 0
            profit_loss = current_value - invested
            
            total_invested += invested
            total_current += current_value
            total_profit_loss += profit_loss
            
            print(f"{symbol:<8}{shares:<12.2f}${avg_cost:<11.2f}"
                  f"${current_price:<11.2f}${invested:<11.2f}"
                  f"${current_value:<11.2f}${profit_loss:<+11.2f}")
        
        print("-" * 85)
        print(f"Total:{'':<32}${total_invested:<11.2f}${total_current:<11.2f}${total_profit_loss:<+11.2f}\n")

def load_api_key():
    try:
        with open('apikey.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: API key file not found (create 'apikey.txt' with your Alpha Vantage API key)")
        return None

def main_menu():
    print("\nStock Portfolio Tracker")
    print("1. Add Stock")
    print("2. Remove Stock")
    print("3. View Portfolio")
    print("4. Exit")

def main():
    api_key = load_api_key()
    if not api_key:
        return
    
    portfolio = Portfolio()
    
    while True:
        main_menu()
        choice = input("Enter your choice: ")
        
        if choice == '1':
            symbol = input("Enter stock symbol: ").strip().upper()
            shares = input("Enter number of shares: ")
            cost = input("Enter purchase price per share: ")
            
            try:
                portfolio.add_stock(symbol, shares, cost)
                print(f"Added {shares} shares of {symbol} to portfolio")
            except ValueError:
                print("Invalid input! Please enter numeric values for shares and price")
        
        elif choice == '2':
            symbol = input("Enter stock symbol to remove: ").strip().upper()
            if portfolio.remove_stock(symbol):
                print(f"Removed all shares of {symbol} from portfolio")
            else:
                print(f"{symbol} not found in portfolio")
        
        elif choice == '3':
            portfolio.display(api_key)
        
        elif choice == '4':
            print("Exiting program...")
            break
        
        else:
            print("Invalid choice! Please select 1-4")

if __name__ == "__main__":
    main()