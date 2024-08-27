import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from st_circular_progress import CircularProgress
import logging
import os
import math

st.image("./images/QSlogo.png", width = 300)
st.header("StateAssessment Business and Technology Current State Analysis")

def updatebcprog(val):
    #logging.error(f"value change: {val}")
    val = math.ceil(val)
    bc.update_value(progress=val)

def updatedmprog(val):
    #logging.error(f"value change: {val}")
    val = math.ceil(val)
    dm.update_value(progress=val)

def updatetcprog(val):
    #logging.error(f"value change: {val}")
    val = math.ceil(val)
    tc.update_value(progress=val)
    

df = pd.read_csv("./data/currstate.csv")

col1, col2, col3 = st.columns(3)
with col1:
    bc = CircularProgress(
        value=0,
        label="Business Capability Score",
        size="Medium",
        key="bctot",
    )
    bc.st_circular_progress()
with col2:
    dm = CircularProgress(
        value=0,
        label="Digital Maturity Score ",
        size="Medium",
        key="dmtot",
    )
    dm.st_circular_progress()

with col3:
    tc = CircularProgress(
        value=0,
        label="Technical Capability Score",
        size="Medium",
        key="tctot",
    )
    tc.st_circular_progress()


#st.write(df)
bcreport = df.loc[(df["Objective"]=="Business Capability"),['Description','Rating']]
#st.write(bcreport)
st.subheader ("Business Capability Quick Score")
editbcrepot = st.data_editor(
    bcreport,
    column_config={
        "Description": "Business Value",
        "Rating": st.column_config.NumberColumn(
            "Your rating",
            help="Please rate capability (1-10)?",
            min_value=1,
            max_value=10,
            step=1,
            format="%d ⭐",
        ),
    },
    hide_index=True,
)

score = editbcrepot["Rating"].sum()
tot = editbcrepot.size*10
if score is not None and score > 0:
    percentval = (score*100)/tot
    updatebcprog(percentval)

dmreport = df.loc[(df["Objective"]=="Digital Maturity"),['Description','Rating']]
#st.write(bcreport)
st.subheader ("Digital Maturity Quick Score")
editdmreport = st.data_editor(
    dmreport,
    column_config={
        "Description": "Digital Competency",
        "Rating": st.column_config.NumberColumn(
            "Your rating",
            help="Please rate capability (1-10)?",
            min_value=1,
            max_value=10,
            step=1,
            format="%d ⭐",
        ),
    },
    hide_index=True,
)

score1 = editdmreport["Rating"].sum()
tot1 = editdmreport.size*10
if score1 is not None and score1 > 0:
    percentval1 = (score1*100)/tot1
    updatedmprog(percentval1)

tcreport = df.loc[(df["Objective"]=="Technology Capability"),['Description','Rating']]
st.subheader ("Technology Capability Quick Score")
edittcreport = st.data_editor(
    tcreport,
    column_config={
        "Description": "Technical Readiness",
        "Rating": st.column_config.NumberColumn(
            "Your rating",
            help="Please rate capability (1-10)?",
            min_value=1,
            max_value=10,
            step=1,
            format="%d ⭐",
        ),
    },
    hide_index=True,
)

score2 = edittcreport["Rating"].sum()
tot2 = edittcreport.size*10
if score2 is not None and score2 > 0:
    percentval2 = (score2*100)/tot2
    updatetcprog(percentval2)

if (st.checkbox("Show Pie charts")):
    
    c1,c2,c3 = st.columns(3)
    
    with c1:
        sizes = [score,140-score]
        la = ["Business Capability Quick Score", " "]
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=la,autopct='%1.1f%%', textprops={'fontsize': 4})
        ax.axis('equal')
        fig.set_figheight(0.8)
        fig.set_figwidth(0.8)
        st.pyplot(fig)

    with c2:
        sizes1 = [score1,140-score1]
        la1 = ["Digital Maturity Quick Score", " "]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes1, labels=la1,autopct='%1.1f%%', textprops={'fontsize': 4})
        ax1.axis('equal')
        fig1.set_figheight(0.8)
        fig1.set_figwidth(0.8)
        st.pyplot(fig1)
    

    with c3:
        sizes2 = [score2,140-score2]
        la2 = ["Technical Capability Quick Score", " "]
        fig2, ax2 = plt.subplots()
        ax2.pie(sizes2, labels=la2,autopct='%1.1f%%', textprops={'fontsize': 4})
        ax2.axis('equal')
        fig2.set_figheight(0.8)
        fig2.set_figwidth(0.8)
        st.pyplot(fig2)