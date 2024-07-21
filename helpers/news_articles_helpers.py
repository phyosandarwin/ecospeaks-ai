import requests
import os
import streamlit as st


def fetch_articles(keyword, newsapi_key):
    url = f'https://newsapi.org/v2/everything?q={keyword}&pageSize=3&searchIn=title&sortBy=relevancy,publishedAt&apiKey={newsapi_key}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        articles = data['articles']
        headlines = []
        
        for article in articles:
            source_name = article['source']['name']
            article_title = article['title']
            article_content = article['content']
            
            if source_name != '[Removed]' and article_title != '[Removed]' and article_content:
                headline = {
                    'title': article_title,
                    'url': article['url'],
                    'content': article_content
                }
                headlines.append(headline)
                if len(headlines) >= 1:
                    break
        print(headlines)
        return headlines
    else:
        print(f"Error fetching news: {response.status_code}")
        return None


def summarize_articles(article_content, model):
    print(article_content)
    messages = [
        (
            "system",
            "You are a helpful news article summarizer that summarizes article content into one concise paragraph of strictly not more than 100 words. Summarize the user's article content.",
        ),
        ("human", article_content),
    ]
    result = model.invoke(messages)
    return result.content

def get_quiz_questions(summary, model):
    template = f"""
                You are a helpful assistant programmed to generate questions based on the summaries provided. 
                Generate a tricky quiz question based on these summaries: {summary}
                The question will be accompanied by 3 possible answers: one correct answer and two incorrect ones.
                Your output for each question MUST be shaped according to this template:
                
                    Question: <question>\n
                    A: <first option>\n
                    B: <second option>\n
                    C: <third option>
                """
    messages = [
        ("system", template),
        ("human", summary),
    ]
    return model.invoke(messages).content

## answer evaluation
def evaluate_answers(user_answer, summary, question, model):
    template = f"""
    Use the {summary} to evaluate the {user_answer} to the question in {question}. 
    Explicitly state if the user's answer is correct or not. 
    If the user's answer is wrong, then explain what should be the correct answer. 
    If the user's answer is correct, congratulate the user.
    """
    messages =[
        ("system", template),
        ("human", user_answer)
    ]

    return model.invoke(messages).content
    
