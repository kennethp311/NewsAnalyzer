from NewsAnalyzer import NewsAnalyzer
from FetchNews import FetchNews
from Config import db_config, api_keys



def Fetch_News(table_name, news_search_topic):
    FetchNews_obj = FetchNews(db_config, api_keys['News API'], table_name)

    for day in range(3, 31):
        date_str = f"2024-10-{day:02d}"    
        articles = FetchNews_obj.fetch_news_at_date(news_search_topic, date_str)
        FetchNews_obj.store_articles_in_mysql(articles)
    #FetchNews_obj.Cleanup_table()


def AnalyzeNews(table_name, stock_name):
    NewsAnalyzer_obj = NewsAnalyzer(db_config, api_keys['Openai API'], table_name, stock_name)
    NewsAnalyzer_obj.analyze_articles_relevancy()
    NewsAnalyzer_obj.analyze_articles_opinion()


def PlotNews(table_name, stock_name):
    NewsAnalyzer_obj = NewsAnalyzer(db_config, api_keys['Openai API'], table_name, stock_name)
    NewsAnalyzer_obj.Plot_Result(NewsAnalyzer_obj.get_results_of_occurences())



def main():
    # stock_name = "AMD"  # Example stock name
    stock_name = input("Enter Stock Ticker Symbol: ")
    table_name = f'{stock_name.lower()}_article_data'
    news_search_topic = f'{stock_name} stock performance'

    # Fetch_News(table_name, news_search_topic)
    # AnalyzeNews(table_name, stock_name)
    # PlotNews(table_name, stock_name)    



if __name__ == "__main__":
    main()
