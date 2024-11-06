from NewsAnalyzer import NewsAnalyzer
from FetchNews import FetchNews
from FetchStock import FetchStock
from Config import db_config, api_keys


def FetchNews(ticker_symbol):
    FetchNews_obj = FetchNews(db_config, api_keys['News API'], ticker_symbol)    
    FetchNews_obj.FetchNews_DB()

def FetchStocks(ticker_symbol, period = "3mo"):
    FetchStock_obj = FetchStock(db_config, ticker_symbol)
    FetchStock_obj.FetchStock_DB(period)

def PlotStocks(ticker_symbol):
    FetchStock_obj = FetchStock(db_config, ticker_symbol)
    FetchStock_obj.plot_close_prices()

def AnalyzeNews(ticker_symbol):
    NewsAnalyzer_obj = NewsAnalyzer(db_config, api_keys['Openai API'], ticker_symbol)
    NewsAnalyzer_obj.analyze_articles_relevancy()
    NewsAnalyzer_obj.analyze_articles_opinion()

def PlotNews(ticker_symbol):
    NewsAnalyzer_obj = NewsAnalyzer(db_config, api_keys['Openai API'], ticker_symbol)
    NewsAnalyzer_obj.PlotNews(NewsAnalyzer_obj.get_results_of_occurences())

def PlotStocksNews(ticker_symbol):
    NewsAnalyzer_obj = NewsAnalyzer(db_config, api_keys['Openai API'], ticker_symbol)
    NewsAnalyzer_obj.show_plot_news_and_stocks_relationship(NewsAnalyzer_obj.ScoreResult())


def RunProgram():
    ticker_symbol = input("Enter Stock Ticker Symbol: ")
    NewsAnalyzer_obj = NewsAnalyzer(db_config, api_keys['Openai API'], ticker_symbol)

    if NewsAnalyzer_obj.table_exists(NewsAnalyzer_obj.article_table) and NewsAnalyzer_obj.table_exists(NewsAnalyzer_obj.stock_table):
        decision0 = input("Would you like to store the News-Stocks plot? (Y/N): ")
        
        if decision0.lower() == 'y':
                NewsAnalyzer_obj.store_plot_news_and_stocks_relationship(NewsAnalyzer_obj.ScoreResult())
                return

        elif decision0.lower() == 'n':
                NewsAnalyzer_obj.show_plot_news_and_stocks_relationship(NewsAnalyzer_obj.ScoreResult())
                return
        else:
            print("Wrong Input [End Program]")
            return

    if NewsAnalyzer_obj.table_exists(NewsAnalyzer_obj.article_table) == False:

        decision1 = input(f"{NewsAnalyzer_obj.article_table} doesn't exist, so would you like to create one? (Y/N): ")
       
        if (decision1.lower() == 'y'):
            decision2 = input(f"Would you also like to analyze and plot {NewsAnalyzer_obj.article_table}? (Y/N): ")
            
            if (decision2.lower() == 'y'):
                FetchNews(ticker_symbol)
                AnalyzeNews(ticker_symbol)
                PlotNews(ticker_symbol)
            
            elif (decision2.lower() == 'n'):
                FetchNews(ticker_symbol)
                return

            else:
                print("Wrong Input [End Program]")
                return

        elif decision1.lower() == 'n': 
            if NewsAnalyzer_obj.table_exists(NewsAnalyzer_obj.stock_table):
                decision4 = input(f"Plot the closed prices over time of stock {ticker_symbol.upper()} (Y/N): ")
                if decision4.lower() == 'y':
                    PlotStocks(ticker_symbol)
                return
            else:
                return
            
        else:
            print("Wrong Input [End Program]")
            return

    if NewsAnalyzer_obj.table_exists(NewsAnalyzer_obj.stock_table) == False:
        print(f"{NewsAnalyzer_obj.stock_table} doesn't exist, hence we are creating one for a 3mo period.")
        FetchStocks(ticker_symbol, '3mo')

    NewsAnalyzer_obj.show_plot_news_and_stocks_relationship(NewsAnalyzer_obj.ScoreResult())



def main():
    RunProgram()
    
    # ticker_symbol = input("Enter Stock Ticker Symbol: ")
    # table_name = f'{ticker_symbol.lower()}_article_data'
    # news_search_topic = f'{ticker_symbol} stock performance'

    # FetchNews(ticker_symbol)
    # AnalyzeNews(ticker_symbol)
    # PlotNews(ticker_symbol)    
    # FetchStocks(ticker_symbol, '3mo')
    # PlotStocks(ticker_symbol)
    # FetchStocks(ticker_symbol, '3mo')
    # PlotStocksNews(ticker_symbol)



if __name__ == "__main__":
    main()











