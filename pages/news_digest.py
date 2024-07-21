import streamlit as st
from openai import AzureOpenAI
from helpers.news_articles_helpers import *


st.set_page_config(page_title='NewsDigest', page_icon='🗞️', layout='centered')
st.logo('assets/logo.png')
 

# Load credentials
azure_api_key = st.secrets['azure']['AZURE_OPENAI_KEY']
azure_endpoint = st.secrets['azure']['AZURE_OPENAI_ENDPOINT']
azure_version = st.secrets['azure']['AZURE_OPENAI_API_VERSION']
newsapi_key = st.secrets['newsapi']['API_KEY']

# Set environment variables
os.environ["AZURE_OPENAI_API_KEY"] = azure_api_key
os.environ["AZURE_OPENAI_ENDPOINT"] = azure_endpoint

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4"

# Initialize session state keys
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "What environmental topic would you like to look up news on?"}]
if "questions" not in st.session_state:
    st.session_state["questions"] = None
if "previous_keyword" not in st.session_state:
    st.session_state["previous_keyword"] = None
if "summaries" not in st.session_state:
    st.session_state["summaries"] = None


st.header('Enviro-News Digest', divider='rainbow')
st.caption('Key in your environmental topic keyword. Read the summaries. Ask the chatbot to generate questions. Give your answers and view the returned feedback!')
with st.sidebar:
    st.header("About NewsDigest Chatbot")
    st.subheader("Model: GPT-4")
    st.button("➕ New Chat", on_click=lambda: st.session_state.clear())

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# Function to generate a response based on fetched headlines
def generate_response(news_headlines, azure_version, model):
    if news_headlines:
        response = ""
        for idx, headline in enumerate(news_headlines, 1):
            article_content = headline['content'] 
            summary = summarize_articles(article_content, azure_version, model)
            response += f"{idx}. {headline['title']}\n"
            response += f"\nSummary: {summary}\n"
            response += f"\nLink: {headline['url']}\n\n"
        return response
    else:
        return "Sorry, I could not find any news related to that topic."

def check_if_environmental_topic(text, llm_model):
    client = AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=azure_api_key,
        api_version=azure_version
    )
    # Use the AI model to evaluate if the text is related to environmental topics
    completion = client.chat.completions.create(
        model=llm_model,
        messages=[
            {"role": "system", "content": "Check if {text} is related to environmental topics. Return 'yes' or 'no'."},
            {"role": "user", "content": text}
        ],
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content.strip().lower() == "yes"


prompt = st.chat_input("Message...", key="unique_chat_input")
if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check for keywords to generate quiz questions
    if "questions" in prompt.lower():
        summaries = st.session_state.get("summaries", "")
        if summaries:
            questions = get_quiz_questions(summaries, st.session_state["openai_model"], azure_version)
            st.session_state["questions"] = questions
            response = questions
        else:
            response = "No summaries available to generate quiz questions from."

    elif "evaluate" in prompt.lower() or "answers" in prompt.lower():
        summaries = st.session_state.get("summaries", "")
        questions = st.session_state.get("questions", "")
        user_answers = prompt.lower().split("answers: ")[1].strip().split(", ")
        response = evaluate_answers(user_answers, summaries, questions, st.session_state["openai_model"], azure_version)

    else:
        # Check if the user's input is related to the environmental topic
        is_environmental_topic = check_if_environmental_topic(prompt, st.session_state["openai_model"])
        if is_environmental_topic:
            # Fetch news headlines and generate summaries for the new keyword
            st.session_state["previous_keyword"] = prompt
            news_headlines = fetch_articles(prompt, newsapi_key)
            response = generate_response(news_headlines, azure_version, st.session_state["openai_model"])
            st.session_state["summaries"] = response
        else:
            response = f"Sorry, {prompt} is not an environmental topic. Please try again with a relevant environmental keyword."

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})