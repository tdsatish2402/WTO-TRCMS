import streamlit as st
import pandas as pd

st.title("Trade Concerns Dashboard")

df = pd.read_excel("TrCM_Master_Database.xlsx")

st.write("Number of records:", len(df))

st.dataframe(df.head())
