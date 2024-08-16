from dotenv import load_dotenv, find_dotenv
import streamlit as st
import os
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from operator import itemgetter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
#from langchain.schema.messages import get_buffer_string
from langchain_core.messages import AIMessage, HumanMessage, get_buffer_string
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import format_document
from langchain.schema.runnable import RunnableParallel
from langchain.prompts import ChatPromptTemplate
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from pydantic import BaseModel


load_dotenv(find_dotenv('../.env'))
st.image("./images/QSlogo.png", width = 300)
st.header("State Assessment Session Bot")

host = os.getenv("PG_VECTOR_HOST")
user = os.getenv("PG_VECTOR_USER")
password = os.getenv("PG_VECTOR_PASSWORD")
database = os.getenv("PGDATABASE")
COLLECTION_NAME = os.getenv("PGDATABASE")

CONNECTION_STRING = f"postgresql+psycopg2://{user}:{password}@{host}:5432/{database}"

embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
store = PGVector(
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
    embedding_function=embeddings,
)

#use_jsonb=True,

retriever = store.as_retriever()

model = ChatOpenAI()

class Message(BaseModel):
    role: str
    content: str


class Conversation(BaseModel):
    conversation: list[Message]

clear = st.button("Clear Session")
if clear:
    st.session_state.messages = []
    st.session_state.conversation=[]

#def get_row_count():
#    engine = create_engine(CONNECTION_STRING)
#    with engine.connect() as connection:
#       #logging.error("Running query 1")
#        result = connection.execute(text("SELECT collection_id, document, uuid FROM langchain_pg_embedding LIMIT 1" ))
#        #row_count = result.scalar()
#        #logging.error(f"row_count: {row_count}")
#        #for row in result:
#            #st.write(row)
#    return result

#get_row_count()


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    

if "conversation" not in st.session_state:
    st.session_state.conversation=[
        AIMessage(content="I am a bot, how can I help you?")
    ]
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
ANSWER_PROMPT = ChatPromptTemplate.from_template(template)
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

def _combine_documents(
    docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)

_inputs = RunnableParallel(
    standalone_question=RunnablePassthrough.assign(
        chat_history=lambda x: get_buffer_string(x["chat_history"])
    )
    | CONDENSE_QUESTION_PROMPT
    | ChatOpenAI(temperature=0)
    | StrOutputParser(),
)

_context = {
    "context": itemgetter("standalone_question") | retriever | _combine_documents,
    "question": lambda x: x["standalone_question"],
}

conversational_qa_chain = _inputs | _context | ANSWER_PROMPT | ChatOpenAI() | StrOutputParser()


def ask_question(question: str, conversation: Conversation):
    answer = conversational_qa_chain.invoke(
        {"question": question, "chat_history": conversation},
    )
    return  answer

#text_question = st.text_input("Input: ",key="input")
#submit= st.button("Submit Query")

#if submit:
#    answer = conversational_qa_chain.invoke(
#    {
#        "question": text_question, 
#        "chat_history":[]
#    }
#    )
#    st.write("Response: ", answer)



if prompt := st.chat_input("Submit Query"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        response = ask_question (prompt, st.session_state.conversation)
        st.markdown(response)
        logging.error(prompt)
        logging.error(f"Response: {response}")
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.conversation.append(HumanMessage(content=prompt))
        st.session_state.conversation.append(AIMessage(content=prompt))
       
    

