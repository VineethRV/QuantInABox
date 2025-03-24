import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
def generate_investment_portfolio(investment_amount, sectors):
    """
    Generates an investment portfolio based on user-provided amount and sectors using Gemini.

    Args:
        investment_amount (float): The total amount to be invested.
        sectors (list): A list of sectors to invest in.

    Returns:
        str: A JSON string containing the portfolio recommendations.
    """

    model = genai.GenerativeModel('gemini-2.0-flash')

    prompt = f"""
    Given an investment amount of ${investment_amount} and the following sectors: {', '.join(sectors)}, 
    generate a diversified investment portfolio. 
    Provide the best stock market combinations for each sector, the percentage of the total investment for each stock, 
    and a brief reason for each recommendation.

    Return the results just the json with the following structure:

    {{
        "portfolio": [
            {{
                "sector": "Sector Name",
                "stock": "Stock Ticker (Company Name)",
                "percentage": "Percentage of total investment",
                "reason": "Brief explanation"
            }},
            // ... more stocks
        ]
    }}
    """

    try:
        response = model.generate_content(prompt)
        json_output = response.text.strip()
        return json_output
    except Exception as e:
        return f"Error generating portfolio: {e}"



def generate_investment_portfolio_edit(existing_portfolio,prompt):

    model = genai.GenerativeModel('gemini-2.0-flash')

    promptpassed = f"""
    Given an existing portfolio,\n{existing_portfolio}
    
    edit it based on the following request from user,reevaluate the combination of stock investments and return it in JSON format.

    request: {prompt}
    """

    try:
        response = model.generate_content(promptpassed)
        json_output = response.text.strip()
        return json_output
    except Exception as e:
        return f"Error generating portfolio: {e}"

def main():
    """
    Main function to interact with the user and generate the portfolio.
    """

    try:
        investment_amount = float(input("Enter the amount you want to invest: $"))
        sectors_input = input("Enter the sectors you want to invest in (separate using ','): ")
        sectors = [sector.strip() for sector in sectors_input.split(',')]

        portfolio_json = generate_investment_portfolio(investment_amount, sectors)
        print(portfolio_json)
        prompt=input("Enter what changes do you want?")
        portfolio_json=generate_investment_portfolio_edit(portfolio_json,prompt)
        print(portfolio_json)

    except ValueError:
        print("Invalid input. Please enter a valid number for the investment amount.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()