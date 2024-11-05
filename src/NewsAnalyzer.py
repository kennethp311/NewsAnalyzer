import mysql.connector
import requests
from openai import OpenAI
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator     # only used to make y-axis lines as integers
import numpy as np
from datetime import date
from collections import Counter
import os

class NewsAnalyzer:
    def __init__(self, db_config, gpt_key, table_name, ticker_symbol):
        self.db_config = db_config
        self.gpt_client = OpenAI(api_key = gpt_key)
        self.conn = self.connect_to_db()
        self.cursor = self.conn.cursor(dictionary=True)
        self.table_name = table_name
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
            print(f"Error in connect_to_db(): {err}")
            return None



    def fetch_table(self):  # Helper Function
        try:
            query = f"SELECT * FROM {self.table_name}"
            self.cursor.execute(query)
            return self.cursor.fetchall()

        except mysql.connector.Error as err:
            print(f"Error in fetch_table(): {err}")
            return []
            



    def generate_relevancy(self, description, title):  # Helper Function
        try:
            response = self.gpt_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": (
                        f"You are a news analyst that determines if a news article about company {self.ticker_symbol} is 'Relevant' for understanding its financial performance or stock behavior."
                        f"A news is 'Relevant' if there is any little potential for an article to showcase Good News or Bad News about company {self.ticker_symbol} in relation to its stock price."
                        f"Examples of attributes of Good News for {self.ticker_symbol} in relation to its stock price: Revenue and Profit Growth, New Product launches or Innovations, Market Expansion and Partnerships, Positive market Positioning, Analyst Upgrades or Increase Price Targets, Cost Reductions and Efficiency Gains, Macroeconomic tailwinds"
                        f"Examples of attributes of Bad News for {self.ticker_symbol} in relation to its stock price: Earnings Misses or Lowered Revenue/Profit Guidance, Product Delays or Failures, Loss of Market Share, Weak Macroeconomic Conditions, Analyst Downgrades or Lowered Price Targets, Negative Partnership or Customers News, High Costs or Margin Compression , Legal or Regulatory Issues"
                        "Any news about deals of a product from Amazon or other stores, are not relevant news"
                        "It takes too much time to read each article's content, so it is your job to determine whether am article's brief description and title is enough to warrant further analysis."
                    )},
                    {
                        "role": "user",
                        "content": (
                            f"Here is the article's title: '{title}'. "
                            f"Here is the article's description: '{description}'. "
                            f"Based on the brief description and title, does this article have the potential to showcase any Good, Bad, or Neutral news about company {self.ticker_symbol} after further analysis into the contents of the articles url?"
                            "Make sure to respond only with 'Relevant' or 'Not Relevant'"
                    )}],
                max_tokens=150,
                n=1,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error in generate_relevancy(): {e}")
            return "Error in generate_relevancy()"




    def generate_opinion(self, url_content):  # Helper Function
        try:
            response = self.gpt_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": (
                        # f"You are a news analyst that determines if a news article about company {self.company_name} is 'Good News', 'Bad News', or 'Neutral News' for its finacial performance or stock behavior."
                        # "IMPORTANT RULE: you can only respond with 'Good News', 'Bad News', 'Neutral News'"
                        # f"Example of attributes of Good News for {self.company_name} in relation to its stock price: Revenue and Profit Growth, New Product launches or Innovations, Market Expansion and Partnerships, Positive market Positioning, Analyst Upgrades or Increase Price Targets, Cost Reductions and Efficiency Gains, Macroeconomic tailwinds"
                        # f"Example of attributes of Bad News for {self.company_name} in relation to its stock price: Earnings Misses or Lowered Revenue/Profit Guidance, Product Delays or Failures, Loss of Market Share, Weak Macroeconomic Conditions, Analyst Downgrades or Lowered Price Targets, Negative Partnership or Customers News, High Costs or Margin Compression , Legal or Regulatory Issues"
                        # f"Example of attributes of Neutral News for {self.company_name} in relation to its stock price: Discounts or Promotions by Retail Partners, Product or Service Announcements without market impact, brand mentions without financial implications, Minor operational updates, status quo regulatory news, routine leadership comments or guidance confirmation, general industry trends without specific impact"

                        f"You are a news analyst tasked with determining the impact of news articles about company {self.ticker_symbol} on its stock performance, categorizing them as 'Good News', 'Bad News', or 'Neutral News'."
                        "IMPORTANT RULE: Respond only with 'Good News', 'Bad News', 'Neutral News', 'Useless/Error'. Definitions and examples are as follows:"
                        " - 'Good News' includes news expected to lead to an increase in the stock price."
                        "'Good News' Examples: Robust quarterly earnings that exceed market expectations, successful launch of innovative products, strategic expansions into new markets, securing high-value partnerships, and receiving favorable regulatory decisions."
                        " - 'Bad News' includes news expected to cause a decrease in the stock price."
                        "'Bad News' Examples: Significant financial underperformance such as earnings misses, major product recalls or safety issues, substantial loss of market share to competitors, negative legal rulings, and adverse analyst downgrades."
                        " - 'Neutral News' includes news that typically has no significant immediate impact on the stock price."
                        "'Neutral News' Examples: Standard promotional campaigns, routine product updates that maintain current market dynamics, generic corporate announcements without significant financial implications, and operational status reports that do not suggest major changes."
                        "Example of 'Useless/Error' News: if there is no content of the article given, then its consider 'Useless/Error'."
                    )},
                    {
                        "role": "user",
                        "content": (
                            # "IMPORTANT RULE: you can only respond with 'Good News', 'Bad News', 'Neutral News'"
                            # f"Here is the article's content: '{url_content}'. "
                            # f"Based on this content, is the article saying any good or bad news about {self.company_name}? for its finacial/stock performance or stock behavior. "

                            "IMPORTANT RULE: Respond only with 'Good News', 'Bad News', 'Neutral News', or 'Useless/Error'."
                            f"Review the following content from the article: '{url_content}'. "
                            f"Based on this content, categorize the news about {self.ticker_symbol} in terms of its impact on financial performance or stock behavior."
                        )
                    }
                ],
                max_tokens=150,
                n=1,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error in generate_opinion(): {e}")
            return "Error in generate_opinion()"



    def analyze_articles_relevancy(self):
        articles = self.fetch_table()
        dict_relevancy = {}

        if not articles:
            print("No articles found or unable to connect to the database.")
            return

        for article in articles:
            title = article.get('Title', 'No Title')
            description = article.get('Description', 'No description')

            dict_relevancy[title] = self.generate_relevancy(description, title)
            # print(dict_relevancy[title])

        try:
            for title, gpt_relevancy in dict_relevancy.items():
                query = f"UPDATE {self.table_name} SET GPT_Relevancy = %s WHERE title = %s"
                self.cursor.execute(query, (gpt_relevancy, title))
        
        except mysql.connector.Error as err:
            print(f"Error in analyze_articles_relevancy() sql issues: {err}")
        
        finally:
            if self.conn and self.conn.is_connected():
                self.conn.commit()




    def analyze_articles_opinion(self):
        articles = self.fetch_table()
        dict_url_to_opinion = {}

        if not articles:
            print("analyze_articles_opinion(): No articles found")
            return

        for article in articles:
            my_url = article.get('URL')
            my_gpt_relevancy = article.get('GPT_Relevancy')

            if my_gpt_relevancy == 'Relevant':         
                my_content = self.fetch_url_content(my_url)
                dict_url_to_opinion[my_url] = self.generate_opinion(my_content)
                # print(dict_url_to_opinion[my_url], '\n')

            elif my_gpt_relevancy == 'Not Relevant' and article.get('GPT_Opinion') is not None: 
                self.cursor.execute(f"UPDATE {self.table_name} set GPT_Opinion = NULL WHERE GPT_Relevancy = 'Not Relevant';")

        try:
            for url, gpt_opinion in dict_url_to_opinion.items():
                query = f"UPDATE {self.table_name} SET GPT_Opinion = %s WHERE URL = %s"
                self.cursor.execute(query, (gpt_opinion, url))
        
        except mysql.connector.Error as err:
            print(f"Error in scrap_relevant_url_data(): {err}")
        
        finally:
            if self.conn and self.conn.is_connected():
                self.conn.commit()



    def get_results_of_occurences(self): # Returns a dictionary with each key=date holding a dictionary of the number of occurences of Good, Bad, or Neutral news
        my_dict = {}
        dict_count = {}

        query = f"SELECT Date, GPT_Opinion FROM {self.table_name} WHERE GPT_Relevancy = 'Relevant' AND GPT_Opinion = 'Good News' OR GPT_Opinion = 'Bad News' OR GPT_Opinion ='Neutral News' ORDER BY Date ASC"
        self.cursor.execute(query)
        my_table = self.cursor.fetchall()


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



    def Plot_Result(self, dict_count):
        # Define the output folder path in the parent directory
        parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_folder = os.path.join(parent_directory, "plots")  # 2nd call of same plot and name will replace the the original image 
        os.makedirs(output_folder, exist_ok=True)  # Create the folder if it doesn't exist

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
        plt.title(f'{self.ticker_symbol}: News Sentiment Counts by Date', fontweight='bold')
        
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True)) # used to make y-axis lines as integers
        plt.xticks(np.arange(len(dates)), dates, rotation=45, ha='right')

        # Add legend
        plt.legend()
        plt.tight_layout()

        # Save the plot
        output_path = os.path.join(output_folder, f"{self.ticker_symbol}_news_sentiment.png")
        plt.savefig(output_path, format='png')
        
        plt.show()



    def fetch_url_content(self, url, char_limit=1500):
        try:
            response = requests.get(url)  # Send an HTTP GET request to the given URL
            
            if response.status_code == 200:  # If request was successful
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Gather text from multiple tags
                text_content = ' '.join([
                    element.get_text() for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'span', 'div'])
                ])
                
                # Limit the total character count
                content = text_content[:char_limit]
                return content + ('...' if len(text_content) > char_limit else '')

            else:
                return f"Failed to retrieve content. Status code: {response.status_code}"
        
        except Exception as e:
            return f"Error: {e}"

