from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
from dotenv import load_dotenv, find_dotenv
import streamlit as st
import logging
import json
from PyPDF2 import PdfReader
from langchain_community.vectorstores import PGVector
from langchain.indexes import SQLRecordManager, index
from langchain_community.docstore.document import Document
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from tempfile import NamedTemporaryFile

load_dotenv(find_dotenv('../.env'))

host = os.getenv("PG_VECTOR_HOST")
user = os.getenv("PG_VECTOR_USER")
password = os.getenv("PG_VECTOR_PASSWORD")
port = os.getenv("PGPORT")
COLLECTION_NAME = os.getenv("PGDATABASE")
CONNECTION_STRING = (
    f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{COLLECTION_NAME}"
)
embeddings=OpenAIEmbeddings(api_key=os.environ['OPENAI_API_KEY'])
BLOB_CONN_STRING = os.getenv("BLOB_CONN_STRING")
CONTAINER_NAME = os.getenv("BLOB_CONTAINER")

CHUNK_SIZE = 1024
CHUNK_OVERLAP = 100

blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STRING)

listpagesize = os.getenv("LISTPAGESIZE")
if listpagesize is None:
    listpagesize = 10
    

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

embeddings=OpenAIEmbeddings(api_key=os.environ['OPENAI_API_KEY'])

blob_service_client = BlobServiceClient.from_connection_string(conn_str=BLOB_CONN_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

def list_files(page: int = 1, page_size: int = 2):
    logging.error(f"listing file pagepassed : {page}")
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blob_list = container_client.list_blobs()
    files = [blob.name for blob in blob_list]
    total_files = len(files)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "total_files": total_files,
        "files": files[start:end],
        "page": page,
        "total_pages": (total_files - 1) // page_size + 1,
    }

def list_all():
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blob_list = container_client.list_blobs()
    files = [blob.name for blob in blob_list]
    return files


def upload_files_blobstorage(files):
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    uploaded_files = []

    for file in files:
        blob_client = container_client.get_blob_client(blob=file.name)
        if file.name.lower().endswith('pdf'):
            contents = file.read()
            blob_client.upload_blob(contents, overwrite=True)
            uploaded_files.append(file.name)
            logging.info(file.name)
        else:
            st.write (f"Excluding {file.name} as only PDF are supported")
    return {"uploaded_files": uploaded_files}


def split_documents(docs,fname):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False)

    contents = docs
    if docs and isinstance(docs[0], Document):
        contents = [doc.page_content for doc in docs]

    texts = text_splitter.create_documents(contents)
    for text in texts:
        text.metadata["source"] = fname
    n_chunks = len(texts)
    print(f"Split into {n_chunks} chunks")
    return texts

#def insert_vector_store(text_chunks , filename):
def insert_vector_store(texts):
    if not texts:
        logging.warning("Empty texts passed in to create vector database")
    result = index(
        texts,
        record_manager,
        vector_store,
        cleanup="incremental",
        source_id_key="source",
    )
    #st.write (result)
    print ("insert done")
    return result

def loadandcreateVector(rawfile):
    
    docs = []
    fname = rawfile.name
    if not rawfile.name.lower().endswith('pdf'):
        st.write(f"File {fname} excluded for vector creation")
    title = os.path.basename(fname)
    if rawfile.name.lower().endswith('pdf'):
        pdf_reader = PdfReader(rawfile)
        for num, page in enumerate(pdf_reader.pages):
            page = page.extract_text()
            #doc.metadata["source"] = os.path.basename(doc.metadata["source"])
            doc = Document(page_content=page, metadata={'title': title, 'page': (num + 1), 'source': rawfile.name })
            docs.append(doc)
    
    texts = []
    result = {}
    if docs:
        texts = split_documents(docs,rawfile.name)
        logging.error("created vectors for test")
    if texts:
        result = insert_vector_store(texts)
        logging.error("create text vectors")
    return result


def load_blob_vectors():
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blob_list = container_client.list_blobs()
    docs =[]
    for blob in blob_list:
        fname = blob.name
        blob_client=blob_service_client.get_blob_client(CONTAINER_NAME,fname)
        fileReader  =  json.loads(blob_client.download_blob().readall().decode()
                                  )
        logging.error(f"Blob file is {fname}")
        text = fileReader["content"] + "\n author: " + fileReader["author"] + "\n date: " + fileReader["date"]
        metafileReader = {'source': fileReader["url"],"author":fileReader["author"],"date":fileReader["date"],"category":fileReader["category"],"title":fileReader["title"]}
        if fileReader['content'] != "": 
            doc = Document(page_content=text, metadata=metafileReader)
        docs.append(doc)
        logging.error("created docs")

def reset_vector_store():
    
    page=" "
    doc = Document(page_content=page, metadata={'source': "None" })
    result = index(
        doc,
        record_manager,
        vector_store,
        cleanup="full",
        source_id_key="source",
    )
    return result
    #st.write ("delete done")

def get_row_count():
    engine = create_engine(CONNECTION_STRING)
    with engine.connect() as connection:
        #logging.error("Running query 1")
        result = connection.execute(text("SELECT COUNT(*) FROM langchain_pg_embedding LIMIT 1" ))
        row_count = result.scalar()
        return row_count


def deleteblobfile(files):
    logging.error(f"Files select to detelete are {files}")
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    for file in files:
        blob_client = container_client.get_blob_client(blob=file)
        blob_client.delete_blob(delete_snapshots="include")
        st.session_state.delfilenames.append(file)
 

def loadhtmlandcreatevector (urlval):
    url = ["https://www.quantumsmart.com"]
    if urlval:
        logging.error(f"URL supplied is {urlval}")
        url.append(urlval)
        loader = AsyncChromiumLoader(url)
        html = loader.load()
        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(html)
        logging.error (docs_transformed)
    else:
        st.write("No url specified")
