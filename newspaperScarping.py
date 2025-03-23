import newspaper 
from googlesearch import search as SEARCHH
import os
import google.generativeai as genai

key= os.environ.get('GOOGLE_API_KEY')
# # Set up your API key
genai.configure(api_key=key)

# # Select the Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")



def sentimentAnalysis(query):
    num=0
    results=""
    for j in SEARCHH(query,num_results=10):
        num+=1
        if(num>2):
            try:
                article=newspaper.Article(j)
                article.download()
                article.parse()
                print(article.text)
                results+=article.text
                print("---------------------------------------------------")
            except(newspaper.article.ArticleException):
                print("cant access the article")

    # generate("Perform sentiment analysis on this: \n"+results)
    response = model.generate_content("Perform sentiment analysis:\n"+results+"\n return bullish neutral or bearish, just 1 word")
    # return response
    return response.text

message=input("enter which company ka sentiment analysis: ")
print(sentimentAnalysis("news about stocks of "+message))

