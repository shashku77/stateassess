
import os
from dotenv import load_dotenv, find_dotenv
import streamlit as st
import logging
from modules.fileload import (list_files,list_all,upload_files_blobstorage,deleteblobfile,get_row_count)
from modules.auth import get_auth, get_role


load_dotenv(find_dotenv('../.env'))
st.image("./images/QSlogo.png", width = 300)
st.header("StateAssessment Manage Files")

listpagesize = os.getenv("LISTPAGESIZE")
if listpagesize is None:
    listpagesize = 10
    

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




if "delfilenames" not in st.session_state:
        st.session_state.delfilenames = []

def del_blob_file(files):
    if not files:
        st.session_state.action = ""
    else:
        deleteblobfile(files) 
  


def set_page(pageval):
    st.session_state.pageinfo = pageval



if "action" not in st.session_state:
        st.session_state.action = ""

if "pageinfo" not in st.session_state:
        st.session_state.pageinfo = 1

if st.session_state["authentication_status"]:
    cred = get_role(st.session_state.username)
    if cred == 'admin':
        disableuserstate = False
        disableadminstate = False
    elif cred == "user":
        disableuserstate = False
        disableadminstate = True
else:
    disableuserstate = True
    disableadminstate = True
    st.write ("Please login using Authentication page on sidebar to activate functions")


    
col1, col2 ,col3,col4, col5 = st.columns([1,1,1,1,1])
with col1:
    listf = st.button("List File", disabled=disableuserstate)
    if listf:
        st.session_state.action = "listf"
with col2:
    upld = st.button("Upload File",disabled=disableadminstate)
    if upld:
        st.session_state.action = "upld"
with col3:
    wecrawler = st.button("Upload url", disabled=disableuserstate)
    if wecrawler:
        st.session_state.action = "wecrawler"
with col4:
    deletef = st.button("Delete File",disabled=disableadminstate)
    if deletef:
        st.session_state.action = "deletef"
with col5:
    countVecRow = st.button("Rowcount",disabled=disableuserstate)
    if countVecRow:
        st.session_state.action = "countVecRow"


if st.session_state.action == "listf":
    if st.session_state.pageinfo == 0:
        st.session_state.pageinfo = 1
    fileinfo = list_files(st.session_state.pageinfo,2)
    logging.error(fileinfo)
    for f in fileinfo["files"]:
        st.write(f)
    col1, col2 = st.columns([1,1])
    with col1:
        if fileinfo["page"] > 1:
            buttonstate = False
        else: 
            buttonstate = True
        st.button(key ="Prev" , label="Prev", disabled=buttonstate, on_click=set_page , args = [fileinfo["page"] - 1] )
        
            
    with col2:
        if fileinfo["page"] >= fileinfo["total_pages"]:
            nxtstate = True
        else:
            nxtstate = False
        st.button(key ="Next", label="Next", disabled=nxtstate, on_click=set_page , args = [fileinfo["page"] + 1] ) 
        
            
elif st.session_state.action == "deletef":
    st.subheader("Select file(s) and press confirm to delete")
    result = list_all()
    options = st.multiselect(
    "Files to delete",
    result
    )
    st.button("Confirm Removal", on_click=deleteblobfile ,args = [options])
    if len(st.session_state.delfilenames) > 0:
        st.write(f"Deleted files:{st.session_state.delfilenames} ")
        st.session_state.delfilenames = []
    

elif st.session_state.action == "countVecRow":
    st.subheader(f"Total Vector Embeddings Count: {get_row_count()}")
  
elif st.session_state.action == "upld" :
    filesupd = st.file_uploader("Upload your Files ", accept_multiple_files=True)
    if st.button("Process and Load Vectors"):
        uploaded_files = upload_files_blobstorage(filesupd)
        st.write(f"uploaded into blob: {uploaded_files}")
        #for fi in filesupd:
        #    st.write("going to load and createvector")
        #    st.write(f"file: detail: {fi}")
        #    result = loadandcreateVector(fi)
        #    st.write (result) """



