## Quant in a box
Quantitave analysis based Financial advice assistant powered by Google Gemini.

Interface: Desktop app written in edgekit webview 
html/css + htmx --> pythonic backend for interfacing LLMs and machine learning models.
Firebase tools for the site (brownie points)
Simple and intuitive dahboard
# Goals of this tool:

## Two modes:

### 1. Newbie (more emphasis on this since, primary goal is this):
- Chatbot that answers market / investment related questions (with grounding access).
- Find beginner stocks and srategies(with reasoning / thinking)
- Gives financial tips and warnings
- Super basic social media sentiment analysis for stock prediction
- "market mood indicator" - an indicator that gives the overall nature of the market right now (bullish, bearish, neutral)
- Generate pre built potfolios for easier onboarding

### 2. Veteran (The real deal)
- All the above features
- Market analysis from news and social media
- Satellite imagery and supply chain management tracking APIs
- Regression and other predctive models for analysis of stock based on current global situations and past patterns
- Volatility prediction and other quant driven AI srategies (mostly AI models for financial data)
- Whale tracker and fraud detection
- Not only investment but shorting options as well
- Cryptocurrency monitoring support
- And finally to top it off, an automated trading bot on the zerodha platform

# Why I think this would work
- We don't have to reinvent the wheel, these tools exist independently, our goal is to bring them all together with the LLM binding it. Plus this shouldn't take much time to setup and apart from the AI part I'm sure everyone knows python and basic html/css.
- We gotta sell it is a "democratization of access to the market", why should only people with MBAs and degrees in data science be able to understand and participate in the market.

# Things to do
 It's easy to do, but there's a lot of shit to do so here's the plan
 - **Vineeth and Satvika**: Everything in the newbie section
	  - Chatbot is pretty easily doable
	  - Use other market data API
	  - Enable grounding and find best stocks for users to invest into via Gemini
	  - ~~Use reddit, X API and newspapers3k paired with google's programmable search engine to fetch URLs and scrape websites for sentiment analysis (via gemini, if gemini is running out of tokens or you ran out of grounding credits, write the grounding logic from cratch and use groq (gemma from google))~~
	  - Ask gemini for structured ouput to analyse everything and return one of the three indications.
	  - Use a template and ask gemini to create a portfolio for the us, make it interactive so the user can add or remove whatever they want and Gemini can take their input to make decisions as well.
	- Deliverables: Terminal script for all this, no UI required, use PEP guidelines for writing clean and safe python.

- Me:
	- Look into all the AI and quant models implementation and get that done
	- Write the frontend for everything 
	- Data fusion of all the various APIs into our dashboard
- Akhil:
	- Only one job for the goat, learn how to interface Zerodha API for trading, then we'll work together for infusing the AI algoithms and the bot.


 