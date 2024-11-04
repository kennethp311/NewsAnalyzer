import yfinance as yf
import mysql.connector
import pandas as pd
import pytz


class DatabaseConfig:
    def __init__(self, host, user, password, db_name):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name


def store_stock_data_in_mysql(ticker_symbol, db_config, period):

    # Step 1: Retrieve stock data using yfinance for the specified period
    stock_data = yf.Ticker(ticker_symbol)
    
    # Get historical stock data for the given period
    stock_history = stock_data.history(period=period)
    
    # Reset index to make 'Date' a column
    stock_history.reset_index(inplace=True)

    # Convert 'Date' column to Pacific Time (Los Angeles)
    # Since it's already timezone-aware, use tz_convert directly
    stock_history['Date'] = stock_history['Date'].dt.tz_convert('America/Los_Angeles').dt.date

    # Step 2: Connect to MySQL database using the database configuration from db_config
    conn = mysql.connector.connect(
        host=db_config.host,
        user=db_config.user,
        password=db_config.password,
        database=db_config.db_name
    )
    cursor = conn.cursor()
    
    # Step 3: Create the table if it doesn't exist or if it does drop it and make a new empty table
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {ticker_symbol.lower()}_stock_data;")
        # print(f"Table '{ticker_symbol.lower()}_stock_data' dropped successfully.")
        
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {ticker_symbol.lower()}_stock_data (
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
    
    except mysql.connector.Error as err:
        print(f"Error creating Table: {err}")
    

    # Step 4: Insert data into the MySQL table
    for index, row in stock_history.iterrows():
        cursor.execute(f'''
        INSERT INTO {ticker_symbol.lower()}_stock_data (Date, Open, High, Low, Close, Volume, Dividends, Stock_Splits) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        Open=VALUES(Open), High=VALUES(High), Low=VALUES(Low), Close=VALUES(Close),
        Volume=VALUES(Volume), Dividends=VALUES(Dividends), Stock_Splits=VALUES(Stock_Splits)
        ''', (row['Date'], row['Open'], row['High'], row['Low'], row['Close'], row['Volume'], row['Dividends'], row['Stock Splits']))
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
    print(f"Stock data for {ticker_symbol} has been stored successfully in MySQL for the period: {period}.")


# Example usage:
# db_config = DatabaseConfig(host='localhost', user='root', password='', db_name='stock_data_db')
# store_stock_data_in_mysql('AMD', db_config, '1y')


db_config = DatabaseConfig(
    host = 'localhost',
    user = 'root',
    password = '',
    db_name = 'stock_data_db'
)

store_stock_data_in_mysql(
    ticker_symbol = 'AMD',
    db_config = db_config,
    period = '1mo'  
)