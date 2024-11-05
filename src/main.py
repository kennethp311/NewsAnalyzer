from NewsAnalyzer import NewsAnalyzer
from FetchNews import FetchNews
from FetchStock import FetchStock
from Config import db_config, api_keys


def Fetch_News(table_name, news_search_topic):
    FetchNews_obj = FetchNews(db_config, api_keys['News API'], table_name)    
    FetchNews_obj.FetchNews_DB(news_search_topic)

def Fetch_Stocks(ticker_symbol, period):
    FetchStock_obj = FetchStock(db_config, ticker_symbol)
    FetchStock_obj.FetchStock_DB(period)

def Plot_Stocks(ticker_symbol):
    FetchStock_obj = FetchStock(db_config, ticker_symbol)
    FetchStock_obj.plot_close_prices()

def AnalyzeNews(table_name, stock_name):
    NewsAnalyzer_obj = NewsAnalyzer(db_config, api_keys['Openai API'], table_name, stock_name)
    NewsAnalyzer_obj.analyze_articles_relevancy()
    NewsAnalyzer_obj.analyze_articles_opinion()


def PlotNews(table_name, stock_name):
    NewsAnalyzer_obj = NewsAnalyzer(db_config, api_keys['Openai API'], table_name, stock_name)
    NewsAnalyzer_obj.PlotResult(NewsAnalyzer_obj.get_results_of_occurences())




def main():
    ticker_symbol = input("Enter Stock Ticker Symbol: ")
    table_name = f'{ticker_symbol.lower()}_article_data'
    news_search_topic = f'{ticker_symbol} stock performance'

    # Fetch_News(table_name, news_search_topic)
    # AnalyzeNews(table_name, ticker_symbol)
    # PlotNews(table_name, ticker_symbol)    
    # Fetch_Stocks(ticker_symbol, '1mo')
    # Plot_Stocks(ticker_symbol)



if __name__ == "__main__":
    main()








# from datetime import datetime, timedelta
# def Fetch_News(table_name, news_search_topic):
#     today = datetime.today()
#     dates_30_days_prior = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]    
#     FetchNews_obj = FetchNews(db_config, api_keys['News API'], table_name)

#     for day in dates_30_days_prior:
#         articles = FetchNews_obj.fetch_news_at_date(news_search_topic, day)
#         FetchNews_obj.store_articles_in_mysql(articles)
#         #FetchNews_obj.Cleanup_table()
