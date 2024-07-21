import streamlit as st

st.set_page_config(page_title='Ecospeaks', page_icon='🌿', layout='wide')
st.logo('assets/logo.png')

st.columns([2,3,1])[1].title('EcoSpeaks.ai')
aboutText = "EcoSpeak is an LLM-powered web application to educate individuals on sustainability issues and guide them to reach their personalized sustainable goals."
st.columns([0.5,3,0.5])[1].success(aboutText, icon="🌿")

st.subheader("Navigate App Features")

# Creating three columns for the feature sections
left_col, middle_col, right_col = st.columns([2, 2, 2])

# Adding content to the left column
with left_col:
    with st.container():
        st.page_link(label="News Digest 🗞️", page="pages/news_digest.py", use_container_width=True)
        st.info(icon='ℹ️', body="Summarises your latest environmental news and prepares quizzes for you!")

# Adding content to the middle column
with middle_col:
    with st.container():
        st.page_link(label="FAQ Assistant 🎓", page="pages/faq_assistant.py", use_container_width=True)
        st.info(icon='ℹ️', body="Understand your (long) text documents more quickly and effectively!")

# Adding content to the right column
with right_col:
    with st.container():
        st.page_link(label="Calculate footprint 👣", page="pages/emission_calculator.py", use_container_width=True)
        st.info(icon='ℹ️', body="Use the emissions calculator tool to calculate your estimated daily emission!")

st.divider()
# YouTube Demo section
st.subheader("View Youtube demo")
VIDEO_URL = "https://youtu.be/v0YE9YDY5ts"
st.video(data=VIDEO_URL)
        
