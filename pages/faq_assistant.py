import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from helpers.faq_utils import classify_text_with_llm, process_document, create_vector_database, create_qa_chain

os.environ['GOOGLE_API_KEY'] = st.secrets["google"]['GOOGLE_API_KEY']

st.set_page_config(
    page_title="Gemini FAQ",
    page_icon="🤖",
    layout='wide'
)
st.logo('assets/logo.png')

### streamlit UI ###
st.subheader('🤖 Environmental FAQ Chat')
st.caption("Currently only supporting PDF and TXT files. Powered by Langchain and Gemini Pro")

st.markdown(f''':red[Upload your document before submitting your query]''')
source_doc = st.file_uploader(label="Upload your environmental-related document", type=["pdf", "txt"])

query = st.text_input("Enter your query:")

if st.button("Submit"):
    # Validate inputs
    if not source_doc or not query:
        st.warning("Please upload the document and provide the missing fields.")
    else:
        try:
            # process according to file type
            context = process_document(source_doc)
            # Initialize the LLM for classification
            model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.2)


            # Check if the text is related to the environment using LLM
            if classify_text_with_llm(context, model):
                st.success("The document content is related to environmental topics.")
                
                # Split the text
                splitter = RecursiveCharacterTextSplitter(chunk_size=15000, chunk_overlap=0)
                chunks = splitter.split_text(context)

                # create vector database
                vectordb = create_vector_database(chunks)

                # Perform question-answering using the new approach
                answer = create_qa_chain(vectordb, query, model)
                st.info(answer)

            else:
                st.warning("The document content does not seem to be related to environmental topics. Please upload a more relevant document")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
