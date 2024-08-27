import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv, find_dotenv
#from langchain_google_genai import GoogleGenerativeAIEmbeddings
#from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
#import google.generativeai as genai
#from langchain-community import OpenAI
#from langchain.vectorstores import FAISS
#from langchain_google_genai import ChatGoogleGenerativeAI
#from langchain.chains.question_answering import load_qa_chain
#from langchain.prompts import PromptTemplate
#from langchain_openai.embeddings import OpenAIEmbeddings
#from langchain.vectorstores.pgvector import PGVector
from langchain_community.vectorstores import PGVector
from langchain.indexes import SQLRecordManager, index
from langchain.docstore.document import Document

load_dotenv(find_dotenv('../.env'))
st.image("./images/QSlogo.png", width = 300)
st.header("State Assessment File Loader")

host = os.getenv("PG_VECTOR_HOST")
user = os.getenv("PG_VECTOR_USER")
password = os.getenv("PG_VECTOR_PASSWORD")
database = os.getenv("PGDATABASE")
#COLLECTION_NAME = "langchain_NIST_docs"
COLLECTION_NAME= os.getenv("PGDATABASE")
CONNECTION_STRING = f"postgresql+psycopg2://{user}:{password}@{host}:5432/{database}"
#print(CONNECTION_STRING)
embeddings=OpenAIEmbeddings(api_key=os.environ['OPENAI_API_KEY'])
vector_store = PGVector(
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
    use_jsonb=True,
)

namespace = f"pgvector/{COLLECTION_NAME}"
record_manager = SQLRecordManager(
    namespace, db_url=CONNECTION_STRING
)

record_manager.create_schema()

def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        pdf_reader= PdfReader(pdf)
        for page in pdf_reader.pages:
            text+= page.extract_text()
    return  text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)
    #chunks = text_splitter.split_text(text)
    docs = []
    for chunk in text_splitter.split_text(text):
        docs.append(Document(page_content=chunk, metadata={"source": "NIST", "path":"custompath", "others":"others"}))
    #docs = text_splitter.create_documents(text)
    st.write(len(docs))

    #return chunks
    return docs

#def insert_vector_store(text_chunks , filename):
def insert_vector_store(docs):
    result = index(
        docs,
        record_manager,
        vector_store,
        cleanup="incremental",
        source_id_key="source",
    )
    st.write (result)
    print ("insert done")

pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)
if st.button("Submit & Process"):
    st.write(pdf_docs[0].name)    
    with st.spinner("Processing..."):
        raw_text = get_pdf_text(pdf_docs)
        #text_chunks = get_text_chunks(raw_text)
        docs = get_text_chunks(raw_text)
        #insert_vector_store(text_chunks,pdf_docs[0].name)
        insert_vector_store(docs)
        st.success ("Done")