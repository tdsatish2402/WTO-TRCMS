import streamlit as st
import pandas as pd

st.title("Trade Concerns Dashboard")

df = pd.read_excel("TrCM_Master_Database_v2.xlsx")

st.write("Number of records:", len(df))

st.dataframe(df.head())
