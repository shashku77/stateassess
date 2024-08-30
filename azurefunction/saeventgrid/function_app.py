import azure.functions as func
import datetime
import logging
import os
from azure.storage.blob import BlobServiceClient
from langchain_community.document_loaders import AzureBlobStorageContainerLoader
from langchain_community.vectorstores import PGVector
from langchain.indexes import SQLRecordManager, index
from langchain.schema import Document
#from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings
from pydantic import BaseModel, Field
from langchain.text_splitter import RecursiveCharacterTextSplitter
from unstructured.partition.pdf import partition_pdf
app = func.FunctionApp()

BLOB_CONN_STRING = os.getenv("BLOB_CONN_STRING")
CONTAINER_NAME = os.getenv("BLOB_CONTAINER")

CHUNK_SIZE = 1024
CHUNK_OVERLAP = 100

blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STRING)

host = os.getenv("PG_VECTOR_HOST")
user = os.getenv("PG_VECTOR_USER")
password = os.getenv("PG_VECTOR_PASSWORD")
port = os.getenv("PGPORT")
COLLECTION_NAME = os.getenv("PGDATABASE")
CONNECTION_STRING = (
    f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{COLLECTION_NAME}"
)

namespace = f"pgvector/{COLLECTION_NAME}"
record_manager = SQLRecordManager(namespace, db_url=CONNECTION_STRING)
#record_manager.create_schema()

embeddings = OpenAIEmbeddings()
#embeddings=OpenAIEmbeddings(api_key=os.getenv('OPENAI_API_KEY'))

vector_store = PGVector(
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
)

class DocumentIn(BaseModel):
    page_content: str
    metadata: dict = Field(default_factory=dict)


@app.function_name(name="safileevents")
@app.event_grid_trigger(arg_name="event")
def trigEvent(event: func.EventGridEvent):
    logging.info("Enter Event trigger function")
    logging.error(event.event_time)
    
    loader = AzureBlobStorageContainerLoader(conn_str=BLOB_CONN_STRING, container=CONTAINER_NAME)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    split_documents = text_splitter.split_documents(data)
    logging.info(f"Document count: {len(split_documents)}")
    documents_in = [
        {
            "page_content": doc.page_content,
            "metadata": {"source": doc.metadata["source"]},
        }
        for doc in split_documents
    ]
    result = index_documents(documents_in)
    logging.info(result)

def index_documents(documents_in: list[DocumentIn]):
    print(documents_in)
    try:
        documents = [
            Document(page_content=doc.page_content, metadata=doc.metadata)
            for doc in documents_in
        ]
        result = index(
            documents,
            record_manager,
            vector_store,
            cleanup="full",
            source_id_key="source",
        )
        return result
    except Exception as e:
        detail=str(e)
        logging.info(detail)




