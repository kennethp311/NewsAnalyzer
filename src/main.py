from NewsAnalyzer import NewsAnalyzer
from FetchNews import FetchNews
from FetchStock import FetchStock
from Config import db_config, api_keys


def Fetch_News(ticker_symbol):
    FetchNews_obj = FetchNews(db_config, api_keys['News API'], ticker_symbol)    
    FetchNews_obj.FetchNews_DB()

def Fetch_Stocks(ticker_symbol, period):
    FetchStock_obj = FetchStock(db_config, ticker_symbol)
    FetchStock_obj.FetchStock_DB(period)

def Plot_Stocks(ticker_symbol):
    FetchStock_obj = FetchStock(db_config, ticker_symbol)
    FetchStock_obj.plot_close_prices()

def AnalyzeNews(ticker_symbol):
    NewsAnalyzer_obj = NewsAnalyzer(db_config, api_keys['Openai API'], ticker_symbol)
    NewsAnalyzer_obj.analyze_articles_relevancy()
    NewsAnalyzer_obj.analyze_articles_opinion()

def PlotNews(ticker_symbol):
    NewsAnalyzer_obj = NewsAnalyzer(db_config, api_keys['Openai API'], ticker_symbol)
    NewsAnalyzer_obj.PlotResult(NewsAnalyzer_obj.get_results_of_occurences())


def Final_PlotScore(ticker_symbol):
    NewsAnalyzer_obj = NewsAnalyzer(db_config, api_keys['Openai API'], ticker_symbol)

    if NewsAnalyzer_obj.table_exists(NewsAnalyzer_obj.article_table) == False:
        decision1 = input(f"{NewsAnalyzer_obj.article_table} doesn't exist, so would you like to create one? (Y/N): ")
        decision2 = input("Would you also like me to analyze and plot the news too? (Y/N): ")

        if decision1 == 'Y':     
            Fetch_News(ticker_symbol)
        
        if decision2 == 'Y': 
            AnalyzeNews(ticker_symbol)
            PlotNews(ticker_symbol)

    if NewsAnalyzer_obj.table_exists(NewsAnalyzer_obj.stock_table) == False:
        print(f"{NewsAnalyzer_obj.stock_table} doesn't exist, hence we are creating one for a 3mo period.")
        Fetch_Stocks(ticker_symbol, '3mo')

    NewsAnalyzer_obj.plot_news_and_stocks_relationship(NewsAnalyzer_obj.ScoreResult())



def main():
    ticker_symbol = input("Enter Stock Ticker Symbol: ")
    table_name = f'{ticker_symbol.lower()}_article_data'
    # news_search_topic = f'{ticker_symbol} stock performance'

    # Fetch_News(ticker_symbol)
    # AnalyzeNews(ticker_symbol)
    # PlotNews(ticker_symbol)    
    # Fetch_Stocks(ticker_symbol, '3mo')
    # Plot_Stocks(ticker_symbol)
    # Fetch_Stocks(ticker_symbol, '3mo')
    Final_PlotScore(ticker_symbol)



if __name__ == "__main__":
    main()
