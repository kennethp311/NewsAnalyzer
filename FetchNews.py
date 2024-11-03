import requests
from datetime import datetime
import pytz
import mysql.connector
import pandas as pd


class DatabaseConfig:
    def __init__(self, host, user, password, db_name):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name


class Fetch_News:
    def __init__(self, db_config, news_api_key):
        self.db_config = db_config
        self.conn = self.connect_to_db()
        self.cursor = self.conn.cursor(dictionary=True)
        self.news_api_key = news_api_key

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
            print(f"Error in connect_to_db(): {err}")
            return None



    def convert_to_pacific_time(self, utc_date_str):
        utc_date = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%SZ")
        utc_date = utc_date.replace(tzinfo=pytz.utc)
        pacific_time = utc_date.astimezone(pytz.timezone('America/Los_Angeles'))
        return pacific_time.strftime("%Y-%m-%d %H:%M:%S")  # Adjusted to MySQL-compatible format



    def fetch_news_at_date(self, news_topic, date_str, num_of_articles = 20):
        # Base URL for the News API with a limit of 50 articles
        url = f'https://newsapi.org/v2/everything?q={news_topic}&language=en&pageSize=50&apiKey={self.news_api_key}'
        
        # Append the date filter if provided
        if date_str:
            url += f'&from={date_str}&to={date_str}'

        # Fetch news from the API
        response = requests.get(url)
        news_data = response.json()

        if news_data.get('status') == 'ok':
            articles = news_data['articles']
            return articles[:num_of_articles] # Limit the number of articles
        else:
            print("Error fetching news:", news_data)
            return []



    def store_articles_in_mysql(self, articles, table_name):
        if not articles:
            print("No articles found.")
            return


        #self.cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            
        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            Title TEXT NOT NULL,
            Description TEXT NOT NULL,
            Date DATETIME NOT NULL,
            URL VARCHAR(255) NOT NULL,
            GPT_Relevancy VARCHAR(255) DEFAULT NULL,
            GPT_Opinion VARCHAR(255) DEFAULT NULL
        )
        ''')

        insert_query = f'''
        INSERT INTO {table_name} (Title, Description, Date, URL)
        VALUES (%s, %s, %s, %s)
        '''

        # Insert each article into the table
        for article in articles:
            title = article.get('title', 'No title')
            description = article.get('description', 'No description')
            published_at = article.get('publishedAt')
            url = article.get('url', 'No URL')

            if published_at:
                pacific_date = self.convert_to_pacific_time(published_at)
                try:
                    self.cursor.execute(insert_query, (title, description, pacific_date, url))
                    
                except mysql.connector.Error as err:
                    print(f"Error inserting article: {err}")

        self.conn.commit()
        print(f"Data for {table_name} has been stored successfully in MySQL.")



    def Cleanup_table(self, table_name):
        query = f"DELETE FROM {table_name} WHERE Title = '[removed]' OR Description = '[removed]' OR URL LIKE '%removed.com'"
        self.cursor.execute(query)
        self.conn.commit()
