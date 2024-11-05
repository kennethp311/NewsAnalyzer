import yfinance as yf
import matplotlib.pyplot as plt
import mysql.connector
import pandas as pd
import pytz
import plotly.graph_objects as go

class FetchStock:
    def __init__(self, db_config, ticker_symbol):
        self.db_config = db_config
        self.conn = self.connect_to_db()
        self.cursor = self.conn.cursor(dictionary=True)
        self.ticker_symbol = ticker_symbol
        self.table_name = f"{ticker_symbol.lower()}_stock_data"

    def __del__(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()

    def connect_to_db(self):
        try:
            conn = mysql.connector.connect(
                host=self.db_config.host,
                user=self.db_config.user,
                password=self.db_config.password,
                database=self.db_config.db_name
            )
            return conn

        except mysql.connector.Error as err:
            print(f"Error in FetchNews() => connect_to_db(): {err}")
            return None
   

    def FetchStock_DB(self, period):

        stock_data = yf.Ticker(self.ticker_symbol)         # Retrieve stock data using yfinance for the specified period
        stock_history = stock_data.history(period=period)  # Get historical stock data for the given period
        stock_history.reset_index(inplace=True)            # Reset index to make 'Date' a column

        # Convert 'Date' column to Pacific Time (Los Angeles), Since it's already timezone-aware, use tz_convert directly
        stock_history['Date'] = stock_history['Date'].dt.tz_convert('America/Los_Angeles').dt.date

        self.cursor.execute(f"DROP TABLE IF EXISTS {self.table_name};")

        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            Date DATE PRIMARY KEY,
            Open FLOAT NOT NULL,
            High FLOAT NOT NULL,
            Low FLOAT NOT NULL,
            Close FLOAT NOT NULL,
            Volume BIGINT NOT NULL,
            Dividends FLOAT NOT NULL,
            Stock_Splits FLOAT NOT NULL
        )
        ''')
        
        for index, row in stock_history.iterrows():
            self.cursor.execute(f'''
            INSERT INTO {self.table_name}(Date, Open, High, Low, Close, Volume, Dividends, Stock_Splits) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            Open=VALUES(Open), High=VALUES(High), Low=VALUES(Low), Close=VALUES(Close),
            Volume=VALUES(Volume), Dividends=VALUES(Dividends), Stock_Splits=VALUES(Stock_Splits)
            ''', (row['Date'], row['Open'], row['High'], row['Low'], row['Close'], row['Volume'], row['Dividends'], row['Stock Splits']))
        
        self.conn.commit()

        print(f"Stock data for {self.ticker_symbol} has been stored successfully as a table named {self.table_name} in MySQL for the period: {period}.")


    # def plot_close_prices(self):
    #     # Fetch data from the database
    #     self.cursor.execute(f"SELECT Date, Close FROM {self.ticker_symbol.lower()}_stock_data ORDER BY Date ASC")
    #     result = self.cursor.fetchall()

    #     # Extract dates and closing prices
    #     dates = [row['Date'] for row in result]
    #     close_prices = [row['Close'] for row in result]

    #     # Plotting with dots at each data point
    #     plt.figure(figsize=(10, 6))
    #     plt.plot(dates, close_prices, label="Close Price", marker='o')  # Add marker='o' to plot dots at each point
    #     plt.xlabel("Date")
    #     plt.ylabel("Close Price")
    #     plt.title(f"{self.ticker_symbol} Closing Prices Over Time")
    #     plt.legend()
    #     plt.grid(True)
        
    #     # Set all dates on x-axis
    #     plt.xticks(dates, rotation=45)  # This will set each date as a tick label and rotate them for better readability

    #     plt.tight_layout()
    #     plt.show()


    def plot_close_prices(self):
        # Fetch data from the database
        self.cursor.execute(f"SELECT Date, Close FROM {self.table_name} ORDER BY Date ASC")
        result = self.cursor.fetchall()

        # Extract dates and closing prices
        dates = [row['Date'] for row in result]
        close_prices = [row['Close'] for row in result]

        # Create a scatter plot with Plotly
        fig = go.Figure()

        # Add a scatter trace with date and close price
        fig.add_trace(go.Scatter(
            x=dates,
            y=close_prices,
            mode='lines+markers',  # Line plot with markers
            name='Close Price',
            marker=dict(size=6),
            text=[f"Date: {date}<br>Close: {close}" for date, close in zip(dates, close_prices)],  # Tooltip text
            hoverinfo='text'  # Show custom text on hover
        ))

        # Set title and labels
        fig.update_layout(
            title=f"{self.ticker_symbol} Closing Prices Over Time",
            xaxis_title="Date",
            yaxis_title="Close Price",
            template="plotly_white"
        )

        # Display the plot
        fig.show()
