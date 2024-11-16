### <ins>How to Run Program </ins> 
**(1)**  Setup an virtual environment and 'pip install' the required packages listed within requirements.txt <br />
**(2)**  Use command 'source myenv/bin/activate' to activate the virtual environment. <br />
**(3)**  Within 'src/config.py', fill in the mySQL configuration and the required API keys. <br />
**(4)**  Use command 'python3 src/main.py' to run the program. 


### <ins>Process for Article Analysis and Stock Performance Prediction </ins> 
**Step 1:**  Data Collection and Preprocessing <br />
- **1.1** Gather a dataset of articles containing the following fields: Title, Description, URL, Date. <br /> 
- **1.2** Preprocess this table by removing duplicates and categorizing each article initially as "Relevant" or "Not Relevant." <br />

**Step 2:**  Relevancy Filtering with GPT
- **2.1** Use GPT to analyze the title and description of each article. <br />
- **2.2** Determine if each article is 'Relevant' or 'Not Relevant' to the target company’s stock performance. <br />
- **2.3** Store this determination as a new column, "Relevancy," in the article dataset. <br />

**Step 3:** Web Data Extraction for Relevant Articles <br /> 
- **3.1** For each article flagged as 'Relevant,' extract web data (full text) from the provided URL using web scraping. <br /> 3.2 Clean and preprocess the scraped data for more consistent analysis. <br />

**Step 4:** Sentiment Analysis for Stock Performance Prediction <br /> 
- **4.1** Submit the preprocessed content of each relevant article to GPT, asking it to analyze the potential impact on stock performance. <br /> 
- **4.2** GPT will categorize each article as 'Good News' (potential stock price increase), 'Bad News' (potential stock price decrease), or 'Neutral News' (no clear impact). <br /> 
- **4.3** Record the results in an "Opinion" column for each article. <br />

**Step 5:** Visualization of Sentiment by Date <br /> 
- **5.1** Aggregate the sentiment data (Good, Bad, Neutral) by date. <br /> 
- **5.2** Create a bar graph that displays the count of each opinion type per date to visualize potential trends over time. <br /> 
- **5.3** Save the graph as a report to provide a clear overview of sentiment distribution and potential stock performance trends. <br />


