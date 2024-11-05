import yfinance as yf
import mysql.connector
import pandas as pd
import pytz


class FetchStock:
    def __init__(self, db_config, ticker_symbol):
        self.db_config = db_config
        self.conn = self.connect_to_db()
        self.cursor = self.conn.cursor(dictionary=True)
        self.ticker_symbol = ticker_symbol

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

        self.cursor.execute(f"DROP TABLE IF EXISTS {self.ticker_symbol.lower()}_stock_data;")

        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {self.ticker_symbol.lower()}_stock_data (
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
            INSERT INTO {self.ticker_symbol.lower()}_stock_data (Date, Open, High, Low, Close, Volume, Dividends, Stock_Splits) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            Open=VALUES(Open), High=VALUES(High), Low=VALUES(Low), Close=VALUES(Close),
            Volume=VALUES(Volume), Dividends=VALUES(Dividends), Stock_Splits=VALUES(Stock_Splits)
            ''', (row['Date'], row['Open'], row['High'], row['Low'], row['Close'], row['Volume'], row['Dividends'], row['Stock Splits']))
        
        self.conn.commit()

        print(f"Stock data for {self.ticker_symbol} has been stored successfully in MySQL for the period: {period}.")

