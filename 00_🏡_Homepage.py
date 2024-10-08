# Demo Chatbot

#from langchain_openai import OpenAI
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv() # take environment variables from .env
import streamlit as st
import os
import getpass

if "open_api_key" in st.session_state and not "open_api_key" :
    client = OpenAI(api_key=st.session_state.open_api_key)
else:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])



if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

#def get_openai_response(question):
#    llm=OpenAI( openai_api_key=os.environ["OPENAI_API_KEY"],temperature=0.5)
#    #llm=OpenAI(openai_api_key="",temperature=0.5)
#    response=llm(question)
#    return response


#initializing streamlit

st.set_page_config(page_title="State Assessment")
st.image("./images/QSlogo.png", width = 300)
st.header("State Assessment application")

if "mesg" not in st.session_state:
    st.session_state.mesg = []

for mg in st.session_state.mesg:
    with st.chat_message(mg["role"]):
        st.markdown(mg["content"])

#input = st.text_input("Input: ",key="input")
#response= get_openai_response(input)

if prompt := st.chat_input("I am a AI Bot. How can i help ?"):
    st.session_state.mesg.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.mesg
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.mesg.append({"role": "assistant", "content": response})

#testval = getpass.getpass("Enter your OpenAI API key: ")
st.sidebar.success("Select option above")
with st.sidebar:
    if "open_api_key" not in st.session_state:
        open_api_key = st.text_input ("Please provide open api key and press enter")
        if open_api_key:
            "Thanks for providing the key."
            st.success("Done")
        
    