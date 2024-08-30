import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import logging
import os
import math
import numpy as np

st.image("./images/QSlogo.png", width = 300)
st.header("StateAssessment Target State Analysis")

df = pd.read_csv("./data/targetstate.csv")
listcategory= df['Category'].unique()
categoryoption = st.selectbox("Select Category 👇",listcategory)
df1 = df.loc[df["Category"]==categoryoption]
listsubcategory = df1 ["Subcategory"].unique()
subcategoryoption = st.selectbox("Select Subcategory 👇",listsubcategory)

st.write(f"Which statement is true for {subcategoryoption} in below table?")
df2 = df[['Statement','Current State','Future State']][(df['Category']==categoryoption) & (df['Subcategory']==subcategoryoption)]

editeddf = st.data_editor(
    df2,
    column_config={
        "Statement": "Statement",
        "Current": st.column_config.CheckboxColumn(
            "Current",
            help="select if statement already satisfied",
            default=False,
        ),
        "Future": st.column_config.CheckboxColumn(
            "Future",
            help="select if desired state",
            default=False,
        ),
    },
    hide_index=True,
)
st.write ("Note :Please select checkbox approproately in above table")

szval = editeddf.shape[0]
sdf = editeddf.loc[editeddf["Current State"] == True].shape[0]
prog = 0
prog = math.ceil(sdf*100/szval)
st.markdown("### State Score ###")
st.progress (prog, f"{categoryoption} , {subcategoryoption}: {prog}")



if "scorekeeper" not in st.session_state:
    st.session_state.scorekeeper = pd.DataFrame ({"category": [],"subcategory":[],"score":[]})
    st.session_state.scorekeeper = pd.concat([ st.session_state.scorekeeper,
                                             pd.DataFrame(
                                                { "category":[categoryoption],
                                                 "subcategory":[subcategoryoption],
                                                 "score":[prog] 
                                                 }
                                             )],
                                             ignore_index=True,
                                             )
else:
    d = st.session_state.scorekeeper.loc[(st.session_state.scorekeeper['category']==categoryoption) & (st.session_state.scorekeeper['subcategory']==subcategoryoption)]
    if d.empty:
        st.session_state.scorekeeper = pd.concat (
            [
                st.session_state.scorekeeper,
                pd.DataFrame(
                    { 
                        "category":[categoryoption],
                        "subcategory":[subcategoryoption],
                        "score":[prog] 
                    }
                ) ],
                ignore_index=True,
           
        )
    else:
        st.session_state.scorekeeper.loc[(st.session_state.scorekeeper['category']==categoryoption) & (st.session_state.scorekeeper['subcategory']==subcategoryoption),"score"]=prog
    
if st.checkbox("Show updated Score card"):
    st.session_state.scorekeeper