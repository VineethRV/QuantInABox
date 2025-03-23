import praw
import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

key= os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=key)


reddit=praw.Reddit(
    client_id=os.environ.get('client_id'),
    client_secret=os.environ.get('client_secret'),
    user_agent=os.environ.get('user_agent'),
    username=os.environ.get('username'),
    password=os.environ.get('password')
    )

model = genai.GenerativeModel("gemini-2.0-flash")


def companySentiment(company_name, limit=3,comment_limit=2):
    subreddits = ["stocks", "investing", "business", "wallstreetbets", "technology"]
    results = []
    for subreddit in subreddits:
        # Search for posts related to the company
        for post in reddit.subreddit(subreddit).search(company_name, limit=limit):
            # post.comments.replace_more(limit=0)  # Remove "load more comments" placeholders
            
            # Get the top 'comment_limit' comments
            top_comments = [comment.body for comment in post.comments.list()]
            
            results.append(
                f"title: {post.title}\n"
                f"body: {post.selftext[:500]}\n"  # Limit body text to 500 characters
                f"top_comments: {top_comments}\n\n"
            )
    
    response = model.generate_content("Perform sentiment analysis:\n"+results+"\n return bullish neutral or bearish, just 1 word")
    return response.text

print(companySentiment("Tesla"))