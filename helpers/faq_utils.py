import os
import tempfile
import streamlit as st
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def classify_text_with_llm(text, model):
    # Use LLM to classify if the text is related to environmental topics.
    text_prompt = f"Classify the following text as related to environmental topics or not:\n\n{text}\n\nIs this text related to environmental topics? Answer with 'Yes' or 'No'."
    response = model.invoke(text_prompt)
    return response.content.lower() == 'yes'

def process_document(source_doc):
    """
    Process the uploaded document (PDF or TXT) and return the text content.
    """
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(source_doc.read())
        tmp_file_path = tmp_file.name

    if source_doc.type == "application/pdf":
        loader = PyPDFLoader(tmp_file_path)
        documents = loader.load()
        context = "\n\n".join([str(page.page_content) for page in documents])
    elif source_doc.type == "text/plain":
        with open(tmp_file_path, 'r') as file:
            context = file.read()

    os.remove(tmp_file_path)
    return context


def create_vector_database(chunks):
    """
    Create and return a vector database from the text chunks.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectordb = Chroma.from_texts(chunks, embeddings)
    return vectordb


def create_qa_chain(vectordb, query, model):
    """
    Create and return a question-answering chain.
    """
    prompt = hub.pull("rlm/rag-prompt")

    qa_chain = (
        {
            "context": vectordb.as_retriever() | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | model
        | StrOutputParser()
    )

    response = qa_chain.invoke(query)
    return response