# Demo Chatbot

from langchain_openai import OpenAI
from dotenv import load_dotenv
load_dotenv() # take environment variables from .env
import streamlit as st
import os

def get_openai_response(question):
    llm=OpenAI( openai_api_key=os.environ["OPENAI_API_KEY"],temperature=0.5)
    response=llm(question)
    return response


#initializing streamlit

st.set_page_config(page_title="Demo")
st.header("Langchain application")

input = st.text_input("Input: ",key="input")
response= get_openai_response(input)

submit= st.button("Please ask the Question")

if submit:
    st.subheader("Response is")
    st.write(response)
