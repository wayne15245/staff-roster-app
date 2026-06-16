import streamlit as st
import pandas as pd

st.title("Roster Analyzer (Clean Start)")

uploaded_file = st.file_uploader("Upload Excel", type=["xlsx","xlsm"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None)

    st.subheader("Preview Data")
    st.dataframe(df.head())