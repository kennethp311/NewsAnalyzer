import mysql.connector
import requests
from openai import OpenAI
from bs4 import BeautifulSoup


class DatabaseConfig:
    def __init__(self, host, user, password, db_name):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name

    

class NewsAnalyzer:
    def __init__(self, db_config, gpt_client, table_name, company_name):
        self.db_config = db_config
        self.gpt_client = gpt_client
        self.conn = self.connect_to_db()
        self.cursor = self.conn.cursor(dictionary=True)
        self.table_name = table_name
        self.company_name = company_name

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
                        f"You are a news analyst that determines if a news article about company {self.company_name} is 'Relevant' for understanding its financial performance or stock behavior."
                        f"A news is 'Relevant' if there is any little potential for an article to showcase Good News or Bad News about company {self.company_name} in relation to its stock price."
                        f"Examples of attributes of Good News for {self.company_name} in relation to its stock price: Revenue and Profit Growth, New Product launches or Innovations, Market Expansion and Partnerships, Positive market Positioning, Analyst Upgrades or Increase Price Targets, Cost Reductions and Efficiency Gains, Macroeconomic tailwinds"
                        f"Examples of attributes of Bad News for {self.company_name} in relation to its stock price: Earnings Misses or Lowered Revenue/Profit Guidance, Product Delays or Failures, Loss of Market Share, Weak Macroeconomic Conditions, Analyst Downgrades or Lowered Price Targets, Negative Partnership or Customers News, High Costs or Margin Compression , Legal or Regulatory Issues"
                        "Any news about deals of a product from Amazon or other stores, are not relevant news"
                        "It takes too much time to read each article's content, so it is your job to determine whether am article's brief description and title is enough to warrant further analysis."
                    )},
                    {
                        "role": "user",
                        "content": (
                            f"Here is the article's title: '{title}'. "
                            f"Here is the article's description: '{description}'. "
                            f"Based on the brief description and title, does this article have the potential to showcase any Good, Bad, or Neutral news about company {self.company_name} after further analysis into the contents of the articles url?"
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

                        f"You are a news analyst tasked with determining the impact of news articles about company {self.company_name} on its stock performance, categorizing them as 'Good News', 'Bad News', or 'Neutral News'."
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
                            f"Based on this content, categorize the news about {self.company_name} in terms of its impact on financial performance or stock behavior."
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
                my_content = fetch_url_content(my_url)
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

        


def fetch_url_content(url, char_limit=1500):
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
