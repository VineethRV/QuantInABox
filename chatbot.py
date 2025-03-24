import os
import re
import requests
import yfinance as yf
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


genai.configure(api_key=GEMINI_API_KEY)


# to fetch stock price from Yahoo Finance
def get_stock_price_yahoo(ticker):
    try:
        stock = yf.Ticker(ticker)
        
        # fetching price from history
        hist = stock.history(period="1d")
        if not hist.empty:
            price = hist["Close"].iloc[-1]
        else:
            price = stock.fast_info["last_price"]

        return f"The latest stock price of {ticker} (Yahoo Finance) is {price:.2f}."
    
    except Exception as e:
        return f"Error fetching stock price from Yahoo Finance: {str(e)}"


# to fetch stock price from Alpha Vantage API
def get_stock_price_alpha(ticker):
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url).json()
        price = response["Global Quote"]["05. price"]
        return f"The latest stock price of {ticker} (Alpha Vantage) is {price}."
    except Exception as e:
        return f"Error fetching stock price from Alpha Vantage: {str(e)}"

#to determine which API to use for stock data
def get_stock_price(ticker):
    yahoo_response = get_stock_price_yahoo(ticker)
    if "Error" not in yahoo_response:
        return yahoo_response 
    
    alpha_response = get_stock_price_alpha(ticker)
    if "Error" not in alpha_response:
        return alpha_response 
    
    return "Sorry, I couldn't fetch the stock price from any source."

#to query Gemini AI
def generate_gemini_response(user_input):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash") 
        custom_prompt = """
        You are a stock market assistant with deep knowledge of finance, investments, and trading.
        Answer the user's question in a clear and precise manner with relevant financial insights.
        """

        full_prompt = f"{custom_prompt}\n\nUser Query: {user_input}"

        generation_config = genai.GenerationConfig(
            temperature=0.7, top_p=0.95, top_k=40, max_output_tokens=8192
        )

        response = model.generate_content(full_prompt, generation_config=generation_config)
        return response.text.strip()
    
    except Exception as e:
        return f"Error with Gemini: {str(e)}"

#LLM for intent detection
def detect_intent(user_input):
    try:
        prompt = f"""
        Classify the following user query into one of two categories: 
        1. "stock_price" only if the user is explicitly asking for the latest stock price of any particular stock.
        2. "general_query" if the user is asking a general finance-related question.
        Only return one of the two labels as output (either "stock_price" or "general_query").
        
        User query: "{user_input}"
        """
        return generate_gemini_response(prompt)
    except Exception as e:
        return "general_query"  #default if gemini fails

#to extract stock ticker using Gemini LLM
def extract_ticker(user_input):
    try:
        #LLM to detect stock ticker
        prompt = f"""
        Identify the stock ticker symbol for the company mentioned in the following user query. 
        If no valid ticker is found, return "None". 
        Only return the ticker symbol (e.g., "AAPL" for Apple Inc.).
        
        User query: "{user_input}"
        """

        ticker = generate_gemini_response(prompt).strip()
        print(ticker)
        if ticker and ticker.upper() != "NONE":
            return ticker.upper()  # Return LLM-extracted ticker

        # use yahoo finance search but this isn't working
        search_results = yf.search_tickers(user_input)

        if search_results and "quotes" in search_results and len(search_results["quotes"]) > 0:
            return search_results["quotes"][0]["symbol"]

        return None

    except Exception as e:
        return None 



def main():
    print("\nAI Stock Market Assistant - Chatbot")
    print("Type 'exit' to stop chatting.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                print("AI: Please enter a question or command.")
                continue
                
            if user_input.lower() == "exit":
                print("\nBye")
                break

            # Detect intent using Gemini
            intent = detect_intent(user_input).lower()

            if intent == "stock_price":
                ticker = extract_ticker(user_input)
                if ticker:
                    response = get_stock_price(ticker)
                else:
                    response = "I couldn't find a valid stock ticker in your query. Please try again with a stock symbol (e.g., 'TSLA', 'AAPL')."
            else:
                response = generate_gemini_response(user_input)  # Uses Gemini for general queries
            
            print("AI:", response)

        except KeyboardInterrupt:
            print("\nBye")
            break
        except Exception as e:
            print(f"AI: An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
