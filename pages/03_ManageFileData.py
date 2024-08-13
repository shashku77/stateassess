from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
from dotenv import load_dotenv, find_dotenv
import streamlit as st
import logging

load_dotenv(find_dotenv('../.env'))
st.image("./images/QSLogo.png", width = 300)
st.header("StateAssessment Manage Files")

def set_bg_hack_url():
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.
    '''
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url("https://dm0qx8t0i9gc9.cloudfront.net/watermarks/image/rDtN98Qoishumwih/white-on-white-paper-light-background-vector-website-template_G1WzLxvu_SB_PM.jpg");
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
set_bg_hack_url()
conn_str=os.getenv("BLOB_CONN_STRING")
container_name = os.getenv("BLOB_CONTAINER")


blob_service_client = BlobServiceClient.from_connection_string(conn_str=conn_str)
container_client = blob_service_client.get_container_client(container_name)

def list_files(page: int = 1, page_size: int = 10):
    container_client = blob_service_client.get_container_client(container_name)
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

def upload_files(files):
    container_client = blob_service_client.get_container_client(container_name)
    uploaded_files = []

    for file in files:
        blob_client = container_client.get_blob_client(blob=file.name)

        contents = file.read()
        blob_client.upload_blob(contents, overwrite=True)
        uploaded_files.append(file.name)

    return {"uploaded_files": uploaded_files}

col1, col2 = st.columns([1,1])
with col1:
    listf = st.button("List File")
with col2:
    upld = st.button("Upload")

if listf:
    fileinfo = list_files()
    logging.error(fileinfo)
    for f in fileinfo["files"]:
        col1, col2 = st.columns([1,1])
        with col1:
            st.write(f)
        with col2:
            st.button('Delete File',key = f)

else:
    docs = st.file_uploader("Upload your Files ", accept_multiple_files=True)
    if st.button("Process"):
        st.write(docs[0].name)
        resultfile = upload_files(docs)
        logging.error(resultfile)