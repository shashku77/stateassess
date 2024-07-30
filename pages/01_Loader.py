import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
#from langchain_google_genai import GoogleGenerativeAIEmbeddings
#from langchain.embeddings.openai import OpenAIEmbeddings
#import google.generativeai as genai
#from langchain-community import OpenAI
#from langchain.vectorstores import FAISS
#from langchain_google_genai import ChatGoogleGenerativeAI
#from langchain.chains.question_answering import load_qa_chain
#from langchain.prompts import PromptTemplate

st.image("./images/QSLogo.png", width = 300)
st.header("State Assessment File Loader")

def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        pdf_reader= PdfReader(pdf)
        for page in pdf_reader.pages:
            text+= page.extract_text()
    return  text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


#def get_vector_store(text_chunks):
    #embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    #embeddings=OpenAIEmbeddings(api_key=os.environ['OPENAI_API_KEY'])
    #vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    #vector_store.save_local("faiss_index")

pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)
if st.button("Submit & Process"):
    with st.spinner("Processing..."):
        raw_text = get_pdf_text(pdf_docs)
        text_chunks = get_text_chunks(raw_text)
        #get_vector_store(text_chunks)
        st.success("Done")