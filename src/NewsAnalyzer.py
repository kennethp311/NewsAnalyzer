import mysql.connector
import requests
from openai import OpenAI
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator     # only used to make y-axis lines as integers
import numpy as np
from datetime import date, timedelta
from collections import Counter
import os
import plotly.graph_objects as go


class NewsAnalyzer:
    def __init__(self, db_config, gpt_key, ticker_symbol):
        self.db_config = db_config
        self.gpt_client = OpenAI(api_key = gpt_key)
        self.conn = self.connect_to_db()
        self.cursor = self.conn.cursor(dictionary=True)
        self.ticker_symbol = ticker_symbol
        self.article_table = f"{ticker_symbol.lower()}_article_data"
        self.stock_table = f"{ticker_symbol.lower()}_stock_data"
        self.urlcontent_charlimit = 1500

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
            query = f"SELECT * FROM {self.article_table}"
            self.cursor.execute(query)
            return self.cursor.fetchall()

        except mysql.connector.Error as err:
            print(f"Error in fetch_table(): {err}")
            return []


    def table_exists(self, table_name):
        self.cursor.execute("SHOW TABLES LIKE %s", (table_name,))
        result = self.cursor.fetchone()
        return result is not None



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
                query = f"UPDATE {self.article_table} SET GPT_Relevancy = %s WHERE title = %s"
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
                self.cursor.execute(f"UPDATE {self.article_table} set GPT_Opinion = NULL WHERE GPT_Relevancy = 'Not Relevant';")

        try:
            for url, gpt_opinion in dict_url_to_opinion.items():
                query = f"UPDATE {self.article_table} SET GPT_Opinion = %s WHERE URL = %s"
                self.cursor.execute(query, (gpt_opinion, url))
        
        except mysql.connector.Error as err:
            print(f"Error in scrap_relevant_url_data(): {err}")
        
        finally:
            if self.conn and self.conn.is_connected():
                self.conn.commit()



    def get_results_of_occurences(self): # Returns a dictionary with each key=date holding a dictionary of the number of occurences of Good, Bad, or Neutral news
        my_dict = {}
        dict_count = {}

        query = f"SELECT Date, GPT_Opinion FROM {self.article_table} WHERE GPT_Relevancy = 'Relevant' AND GPT_Opinion = 'Good News' OR GPT_Opinion = 'Bad News' OR GPT_Opinion ='Neutral News' ORDER BY Date ASC"
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




    def ScoreResult(self):
        dict_score = {} 
        dict_count = self.get_results_of_occurences()

        for date in dict_count:
            dict_score[date] = dict_count[date]['Good News'] - dict_count[date]['Bad News']
        
        return dict_score




    def PlotNews(self):
        dict_count = self.get_results_of_occurences()
        # Get the parent directory of the current file's directory
        parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Define the path for the 'other' subfolder within 'plots'
        ticker_symbol_folder = os.path.join(parent_directory, "plots", self.ticker_symbol.upper())
       
        # Ensure the 'plots/other' directory exists
        os.makedirs(ticker_symbol_folder, exist_ok=True)

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

        # Define the output path for the plot in the 'plots/other' subfolder
        output_path_other = os.path.join(ticker_symbol_folder, f"{self.ticker_symbol}_news_sentiment.png")
        plt.savefig(output_path_other)
        plt.show()




    def fetch_url_content(self, url):
        try:
            response = requests.get(url)  # Send an HTTP GET request to the given URL
            
            if response.status_code == 200:  # If request was successful
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Gather text from multiple tags
                text_content = ' '.join([
                    element.get_text() for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'span', 'div'])
                ])
                
                # Limit the total character count
                content = text_content[:self.urlcontent_charlimit]
                return content + ('...' if len(text_content) > self.urlcontent_charlimit else '')

            else:
                return f"Failed to retrieve content. Status code: {response.status_code}"
        
        except Exception as e:
            return f"Error: {e}"


    def show_plot_news_and_stocks_relationship(self):
        dict_score = self.ScoreResult()
        # Get stock data date range
        query = f"SELECT MIN(Date) AS min_date, MAX(Date) AS max_date FROM {self.article_table};"
        self.cursor.execute(query)
        stock_dates = self.cursor.fetchall()
        for datetime in stock_dates:
            start_date = datetime.get('min_date').date()
            end_date = datetime.get('max_date').date()
        
        # Retrieve closing prices within the date range
        query = f"SELECT Date, Close FROM {self.stock_table} WHERE Date BETWEEN %s AND %s ORDER BY Date ASC;"
        self.cursor.execute(query, (start_date, end_date))
        result = self.cursor.fetchall()
        
        # Extract dates and closing prices
        dates = [row['Date'] for row in result]
        close_prices = [row['Close'] for row in result]

        # Identify missing dates in stock data that have scores in dict_score
        missing_dates = [date for date in dict_score if date not in dates]
        extended_dates = dates + missing_dates
        extended_dates.sort()  # Sort dates to maintain chronological order

        # Generate interpolated closing prices for missing dates
        extended_close_prices = []
        date_price_dict = {date: close for date, close in zip(dates, close_prices)}
        for date in extended_dates:
            if date in date_price_dict:
                extended_close_prices.append(date_price_dict[date])
            else:
                # Interpolate using nearest available prices
                prev_date = max(d for d in dates if d < date)
                next_date = min(d for d in dates if d > date)
                prev_close = date_price_dict[prev_date]
                next_close = date_price_dict[next_date]
                interpolated_close = prev_close + (next_close - prev_close) * (
                    (date - prev_date).days / (next_date - prev_date).days
                )
                extended_close_prices.append(interpolated_close)

        # Determine marker colors, sizes, and opacities for all dates
        max_score = max(dict_score.values()) if dict_score else None
        min_score = min(dict_score.values()) if dict_score else None
        is_unique_max = list(dict_score.values()).count(max_score) == 1 if max_score is not None else False
        is_unique_min = list(dict_score.values()).count(min_score) == 1 if min_score is not None else False

        marker_colors = [
            "rgba(211, 211, 211, 1)" if date not in dict_score else  # Light gray if no score
                
            'red' if dict_score[date] < 0 and dict_score.get(date) == min_score and is_unique_min else
            'rgba(200, 100, 100, 1)' if dict_score[date] < 0 else

            'green' if dict_score[date] > 0 and dict_score.get(date) == max_score and is_unique_max else
            'rgba(150, 230, 150, 1)' if dict_score[date] > 0 else
                
            'blue' if dict_score[date] == 0 else 'black'
            for date in extended_dates
        ]

        marker_sizes = [
            ((1 ** dict_score.get(date, 0)) * 10) + ((dict_score.get(date, 0) - 1) * 3) if dict_score.get(date, 0) > 0 else 
            ((1 ** dict_score.get(date, 0)) * 10) + ((dict_score.get(date, 0) + 1) * -3) if dict_score.get(date, 0) < 0 else 
            10
            for date in extended_dates
        ]

        marker_opacities = [
            0.4 if date in missing_dates else 1
            for date in extended_dates
        ]

        # Custom tooltip text with weekday abbreviation for all dates
        tooltip_texts = []
        for date, close in zip(extended_dates, extended_close_prices):
            weekday_label = date.strftime("%a")  # Get abbreviated day name (e.g., Mon, Tue)
            date_with_weekday = f"{date} ({weekday_label})"
            if date in missing_dates:
                tooltip_texts.append(f"<b>Date:</b> {date_with_weekday}<br><b>Close:</b> No Trading <br><b>Score:</b> {dict_score.get(date, 'N/A')}")
            else:
                tooltip_texts.append(f"<b>Date:</b> {date_with_weekday}<br><b>Close:</b> {close:.2f}<br><b>Score:</b> {dict_score.get(date, 'N/A')}")

        # Create the scatter plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=extended_dates,
            y=extended_close_prices,
            mode='lines+markers',
            name='Close Price',
            line=dict(color="rgba(0, 0, 0, 0.5)"),  # Black line with 70% opacity
            marker=dict(size=marker_sizes, color=marker_colors, opacity=marker_opacities),  # Apply different opacities
            text=tooltip_texts,  # Tooltip text with score and day label
            hoverinfo='text'
        ))

        # Set title and labels
        fig.update_layout(
            title=f"<b>{self.ticker_symbol.upper()}:</b> Closing Prices over Time with its respective News Sentiment",
            xaxis_title="Date",
            yaxis_title="Close Price",
            template="plotly_white"
        )

        # Display the plot
        fig.show()



    def store_plot_news_and_stocks_relationship(self):
        dict_score = self.ScoreResult()
        parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ticker_symbol_folder = os.path.join(parent_directory, "plots", self.ticker_symbol.upper())
        os.makedirs(ticker_symbol_folder, exist_ok=True)  # Ensure the 'plots/ticker_symbol' directory exists

        # Get stock data date range
        query = f"SELECT MIN(Date) AS min_date, MAX(Date) AS max_date FROM {self.article_table};"
        self.cursor.execute(query)
        stock_dates = self.cursor.fetchall()
        for datetime in stock_dates:
            start_date = datetime.get('min_date').date()
            end_date = datetime.get('max_date').date()
        
        # Retrieve closing prices within the date range
        query = f"SELECT Date, Close FROM {self.stock_table} WHERE Date BETWEEN %s AND %s ORDER BY Date ASC;"
        self.cursor.execute(query, (start_date, end_date))
        result = self.cursor.fetchall()
        
        # Extract dates and closing prices
        dates = [row['Date'] for row in result]
        close_prices = [row['Close'] for row in result]

        # Identify missing dates in stock data that have scores in dict_score
        missing_dates = [date for date in dict_score if date not in dates]
        extended_dates = dates + missing_dates
        extended_dates.sort()  # Sort dates to maintain chronological order

        # Generate interpolated closing prices for missing dates
        extended_close_prices = []
        date_price_dict = {date: close for date, close in zip(dates, close_prices)}
        for date in extended_dates:
            if date in date_price_dict:
                extended_close_prices.append(date_price_dict[date])
            else:
                # Interpolate using nearest available prices
                prev_date = max(d for d in dates if d < date)
                next_date = min(d for d in dates if d > date)
                prev_close = date_price_dict[prev_date]
                next_close = date_price_dict[next_date]
                interpolated_close = prev_close + (next_close - prev_close) * (
                    (date - prev_date).days / (next_date - prev_date).days
                )
                extended_close_prices.append(interpolated_close)

        # Determine marker colors, sizes, and opacities for all dates
        max_score = max(dict_score.values()) if dict_score else None
        min_score = min(dict_score.values()) if dict_score else None
        is_unique_max = list(dict_score.values()).count(max_score) == 1 if max_score is not None else False
        is_unique_min = list(dict_score.values()).count(min_score) == 1 if min_score is not None else False

        marker_colors = [
            "rgba(211, 211, 211, 1)" if date not in dict_score else  # Light gray if no score
            'red' if dict_score[date] < 0 and dict_score.get(date) == min_score and is_unique_min else
            'rgba(200, 100, 100, 1)' if dict_score[date] < 0 else
            'green' if dict_score[date] > 0 and dict_score.get(date) == max_score and is_unique_max else
            'rgba(150, 230, 150, 1)' if dict_score[date] > 0 else
            'blue' if dict_score[date] == 0 else 'black'
            for date in extended_dates
        ]

        marker_sizes = [
            ((1 ** dict_score.get(date, 0)) * 10) + ((dict_score.get(date, 0) - 1) * 3) if dict_score.get(date, 0) > 0 else 
            ((1 ** dict_score.get(date, 0)) * 10) + ((dict_score.get(date, 0) + 1) * -3) if dict_score.get(date, 0) < 0 else 
            10
            for date in extended_dates
        ]

        marker_opacities = [
            0.4 if date in missing_dates else 1
            for date in extended_dates
        ]

        # Custom tooltip text with weekday abbreviation for all dates
        tooltip_texts = []
        for date, close in zip(extended_dates, extended_close_prices):
            weekday_label = date.strftime("%a")  # Get abbreviated day name (e.g., Mon, Tue)
            date_with_weekday = f"{date} ({weekday_label})"
            if date in missing_dates:
                tooltip_texts.append(f"<b>Date:</b> {date_with_weekday}<br><b>Close:</b> No Trading <br><b>Score:</b> {dict_score.get(date, 'N/A')}")
            else:
                tooltip_texts.append(f"<b>Date:</b> {date_with_weekday}<br><b>Close:</b> {close:.2f}<br><b>Score:</b> {dict_score.get(date, 'N/A')}")

        # Create the scatter plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=extended_dates,
            y=extended_close_prices,
            mode='lines+markers',
            name='Close Price',
            line=dict(color="rgba(0, 0, 0, 0.5)"),  # Black line with 70% opacity
            marker=dict(size=marker_sizes, color=marker_colors, opacity=marker_opacities),  # Apply different opacities
            text=tooltip_texts,  # Tooltip text with score and day label
            hoverinfo='text'
        ))

        # Set title and labels
        fig.update_layout(
            title=f"<b>{self.ticker_symbol.upper()}:</b> Closing Prices over Time with its respective News Sentiment",
            xaxis_title="Date",
            yaxis_title="Close Price",
            template="plotly_white"
        )

        # Save the plot as an image and HTML
        image_path = os.path.join(ticker_symbol_folder, "plot_image.png")
        html_path = os.path.join(ticker_symbol_folder, "plot.html")
        fig.write_image(image_path)  # Saves as PNG
        fig.write_html(html_path)    # Saves as interactive HTML

        # Display the plot
        fig.show()





