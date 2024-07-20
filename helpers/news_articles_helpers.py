import os
import requests
import streamlit as st
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables 
azure_api_key = st.secrets['azure']['AZURE_OPENAI_KEY']
azure_endpoint = st.secrets['azure']['AZURE_OPENAI_ENDPOINT']

def fetch_articles(keyword, newsapi_key):
    url = f'https://newsapi.org/v2/everything?q={keyword}&pageSize=5&searchIn=title&sortBy=relevancy,publishedAt&apiKey={newsapi_key}'
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
                if len(headlines) >= 3:
                    break
        
        return headlines
    else:
        print(f"Error fetching news: {response.status_code}")
        return None

def summarize_articles(article_content, azure_version, model):
    
    summary_llm = AzureChatOpenAI(
        azure_deployment=model,
        api_version=azure_version,
        temperature=0.2,
        max_tokens=None,
        timeout=None,
        max_retries=2)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful news article summarizer that summarizes this {article_content} into a concise paragraph of **less than 100 words**."),
            ("human", article_content),
        ]
    )

    chain = prompt | summary_llm
    result = chain.invoke(
        {
            "article_content": article_content
        }
    )
    return result.content

def get_quiz_questions(summaries, model, azure_version):

    template = f"""
                You are a helpful assistant programmed to generate questions based on the summaries provided. 
                Generate 3 quiz questions based on these summaries: {summaries}
                Each of these questions will be accompanied by 3 possible answers: one correct answer and two incorrect ones.
                Your output for each question MUST be shaped according to this template:
                
                    Question 1: <question>\n
                    A: <first option>\n
                    B: <second option>\n
                    C: <third option>
                """
    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", summaries)
    ])

    quiz_llm = AzureChatOpenAI(
        azure_deployment=model,
        api_version=azure_version,
        temperature=0.3,
        max_tokens=None,
        timeout=None,
        max_retries=2)
    
    chain = prompt | quiz_llm
    result = chain.invoke(
        {
            "summaries": summaries
        }
    )
    return result.content

## answer evaluation
def evaluate_answers(user_answers, summaries, questions, model, azure_version):
    template = f"""
    Use the {summaries} to evaluate the {user_answers} to each of the questions in {questions}. 
    Explicitly state if the user's answer is correct or not. 
    If the user's answer is wrong, then explain what should be the correct answer. 
    If the user's answer is correct, congratulate the user.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("user", user_answers)
    ])

    reasoning_llm = AzureChatOpenAI(
        azure_deployment=model,
        api_version=azure_version,
        temperature=0.2,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )

    chain = prompt | reasoning_llm
    result = chain.invoke(
        {
            "user_answers": user_answers,
            "summaries": summaries,
            "questions": questions
        }
    )
    return result.content
    
