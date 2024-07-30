# Demo Chatbot

from langchain_openai import OpenAI
from dotenv import load_dotenv
load_dotenv() # take environment variables from .env
import streamlit as st
import os



def get_openai_response(question):
    llm=OpenAI( openai_api_key=os.environ["OPENAI_API_KEY"],temperature=0.5)
    #llm=OpenAI(openai_api_key="",temperature=0.5)
    response=llm(question)
    return response


#initializing streamlit

st.set_page_config(page_title="State Assessment")
st.image("./images/QSLogo.png", width = 300)
st.header("State Assessment application")

input = st.text_input("Input: ",key="input")
response= get_openai_response(input)

submit= st.button("Please ask the Question")

if submit:
    st.subheader("Response is")
    st.write(response)


st.sidebar.success("Select option above")
    