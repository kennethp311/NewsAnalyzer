import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator     # only used to make y-axis lines as integers


import mysql.connector
from datetime import date
from collections import Counter


class DatabaseConfig:
    def __init__(self, host, user, password, db_name):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name


class Plot_News:
    def __init__(self, db_config, table_name):
        self.db_config = db_config
        self.table_name = table_name
        self.conn = self.connect_to_db()
        self.cursor = self.conn.cursor(dictionary=True)


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



    def fetch_table(self):
        try:
            query = f"SELECT Date, GPT_Opinion FROM {self.table_name} WHERE GPT_Relevancy = 'Relevant' AND GPT_Opinion = 'Good News' OR GPT_Opinion = 'Bad News' OR GPT_Opinion ='Neutral News' ORDER BY Date ASC"
            self.cursor.execute(query)
            return self.cursor.fetchall()

        except mysql.connector.Error as err:
            print(f"Error in fetch_table(): {err}")
            return []
            


    def get_results_of_occurences(self): # Returns a dictionary with each key=date holding a dictionary of the number of occurences of Good, Bad, or Neutral news
        my_dict = {}
        dict_count = {}

        my_table = self.fetch_table()

        for opinion in my_table: # Creates Dictionary with each key = date, and each key holding a list of opinions
            my_datetime = opinion.get('Date')
            my_GPT_Opinion = opinion.get('GPT_Opinion')

            my_date = my_datetime.date() # convert DATETIME to DATE

            my_dict.setdefault(my_date, []).append(my_GPT_Opinion)

        # print(my_dict[date(2024, 10, 10)])

        for date in my_dict.keys(): # Dictionary with each key(date) holding a dictionary 
            counter = Counter(my_dict[date])

            if date not in dict_count:
                    dict_count[date] = {}

            dict_count[date]['Good News'] = counter.get('Good News', 0)
            dict_count[date]['Bad News'] = counter.get('Bad News', 0)
            dict_count[date]['Neutral News'] = counter.get('Neutral News', 0)
            # print(date, dict_count[date])

        return dict_count




    # def Plot_Result(self, dict_count):
    #     # Separate dates and counts
    #     dates = list(dict_count.keys())
    #     # Add a small height of 0.05 for bars with a count of 0 to ensure they display
    #     min_bar_height = 0.05
    #     good_news = [count["Good News"] if count["Good News"] > 0 else min_bar_height for count in dict_count.values()]
    #     bad_news = [count["Bad News"] if count["Bad News"] > 0 else min_bar_height for count in dict_count.values()]
    #     neutral_news = [count["Neutral News"] if count["Neutral News"] > 0 else min_bar_height for count in dict_count.values()]

    #     # Define bar width and positions
    #     bar_width = 0.25
    #     r1 = np.arange(len(dates)) - bar_width  # shift left
    #     r2 = np.arange(len(dates))              # center
    #     r3 = np.arange(len(dates)) + bar_width  # shift right

    #     # Plotting
    #     plt.figure(figsize=(12, 6))
    #     plt.bar(r1, good_news, color='g', width=bar_width, edgecolor='grey', label='Good News', alpha=0.8)
    #     plt.bar(r2, bad_news, color='r', width=bar_width, edgecolor='grey', label='Bad News', alpha=0.8)
    #     plt.bar(r3, neutral_news, color='b', width=bar_width, edgecolor='grey', label='Neutral News', alpha=0.8)

    #     # Add labels and title
    #     plt.xlabel('Date', fontweight='bold')
    #     plt.ylabel('Count', fontweight='bold')
    #     plt.title('News Sentiment Counts by Date')
    #     plt.xticks(np.arange(len(dates)), dates, rotation=45, ha='right')

    #     # Add legend
    #     plt.legend()
    #     plt.tight_layout()
    #     plt.show()


    def Plot_Result(self, dict_count):
        # Separate dates and counts
        dates = list(dict_count.keys())
        # Add a small height of 0.05 for bars with a count of 0 to ensure they display
        min_bar_height = 0.05
        good_news = [count["Good News"] if count["Good News"] > 0 else min_bar_height for count in dict_count.values()]
        bad_news = [count["Bad News"] if count["Bad News"] > 0 else min_bar_height for count in dict_count.values()]
        neutral_news = [count["Neutral News"] if count["Neutral News"] > 0 else min_bar_height for count in dict_count.values()]

        # Define bar width and positions
        bar_width = 0.25
        r1 = np.arange(len(dates)) - bar_width  # shift left
        r2 = np.arange(len(dates))              # center
        r3 = np.arange(len(dates)) + bar_width  # shift right

        # Plotting
        plt.figure(figsize=(12, 6))
        plt.bar(r1, good_news, color='g', width=bar_width, edgecolor='grey', label='Good News', alpha=0.8)
        plt.bar(r2, bad_news, color='r', width=bar_width, edgecolor='grey', label='Bad News', alpha=0.8)
        plt.bar(r3, neutral_news, color='b', width=bar_width, edgecolor='grey', label='Neutral News', alpha=0.8)

        # Add labels and title
        plt.xlabel('Date', fontweight='bold')
        plt.ylabel('Count', fontweight='bold')
        plt.title(f'{self.company_name}: News Sentiment Counts by Date', fontweight='bold')
        
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True)) # used to make y-axis lines as integers
        plt.xticks(np.arange(len(dates)), dates, rotation=45, ha='right')

        # Add legend
        plt.legend()
        plt.tight_layout()
        plt.show()




db_config = DatabaseConfig(
    host='localhost',
    user='root',
    password='fill in',
    db_name='stock_data_db'
)


Plotnews_obj = Plot_News(db_config, 'amd_article_data')

Plotnews_obj.Plot_Result(Plotnews_obj.get_results_of_occurences())
