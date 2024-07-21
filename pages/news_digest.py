import streamlit as st
import os
from helpers.news_articles_helpers import *
from langchain_google_genai import ChatGoogleGenerativeAI


st.set_page_config(page_title='NewsDigest', page_icon='🗞️', layout='centered')
st.logo('assets/logo.png')
 

# Load credentials
gemini_key = st.secrets["google"]["GOOGLE_API_KEY"]
newsapi_key = st.secrets['newsapi']['API_KEY']

# Set environment variables
os.environ["GOOGLE_API_KEY"] = gemini_key

# initialise model
llm_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)

# Initialize session state keys
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "What environmental topic would you like to look up news on?"}]
if "question" not in st.session_state:
    st.session_state["question"] = None
if "previous_keyword" not in st.session_state:
    st.session_state["previous_keyword"] = None
if "summary" not in st.session_state:
    st.session_state["summary"] = None


st.header('Enviro-News Digest', divider='rainbow')
with st.sidebar:
    st.subheader("NewsDigest Chatbot (Gemini 1.5 Pro)")
    st.button("➕ New Chat", on_click=lambda: st.session_state.clear(), use_container_width=True)
    with st.expander("How does it work?", icon="❔"):
        st.markdown('Input environmental topic. Read the `summary` and ask the chatbot to `generate quiz questions`. Give your `answers` to receive quiz feedback!')


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def check_if_environmental_topic(text):
    text_prompt = (
        f"Classify the following text as related to environmental or nature topics or not:\n\n"
        f"Text: {text}\n\n"
        f"Is this text related to environmental and nature topics? Please answer with a single word: 'Yes' or 'No'."
    )
    response = llm_model.invoke(text_prompt)
    print("Model response:", response.content)
    return response.content.strip().lower() == 'yes'

# Function to generate a response based on fetched headlines
def generate_response(news_headlines):
    if news_headlines:
        response = ""
        for idx, headline in enumerate(news_headlines, 1):
            article_content = headline['content']
            print(article_content)
            summary = summarize_articles(article_content, llm_model)
            response += f"{idx}. {headline['title']}\n"
            response += f"\nSummary: {summary}\n"
            response += f"\nLink: {headline['url']}\n\n"
        return response
    else:
        return "Sorry, I could not find any news related to that topic."

prompt = st.chat_input("Message...", key="unique_chat_input")
if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user",avatar="🤔"):
        st.markdown(prompt)

    # Check for keywords to generate quiz questions
    if "question" in prompt.lower():
        summary = st.session_state.get("summary", "")
        if summary:
            question = get_quiz_questions(summary, llm_model)
            st.session_state["question"] = question
            response = question
        else:
            response = "No summary available to generate quiz question from."

    elif "answer" in prompt.lower():
        summary = st.session_state.get("summary", "")
        question = st.session_state.get("question", "")
        user_answers = prompt.lower().split("answer: ")[1].strip().split(", ")
        response = evaluate_answers(user_answers, summary, question, llm_model)

    else:
        # Check if the user's input is related to the environmental topic
        is_environmental_topic = check_if_environmental_topic(prompt)
        if is_environmental_topic:
            # Fetch news headlines and generate summaries for the new keyword
            st.session_state["previous_keyword"] = prompt
            news_headlines = fetch_articles(prompt, newsapi_key)
            response = generate_response(news_headlines)
            st.session_state["summary"] = response
        else:
            response = f"Sorry, {prompt} is not an environmental topic. Please try again with a relevant environmental keyword."

    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})