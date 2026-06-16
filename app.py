import streamlit as st
import pandas as pd
import re

st.set_page_config(layout="wide")

st.title("📊 Roster Auto Analyzer")

uploaded_file = st.file_uploader("拖 Excel 入嚟", type=["xlsx","xlsm"])

def extract_time(cell):
    if isinstance(cell, str):
        match = re.search(r"(\\d{4})-(\\d{4})", cell)
        if match:
            return match.group(1)
    return None

def detect_rank(row_text):
    if "SUP" in row_text:
        return "SUP"
    elif "SEQO" in row_text:
        return "SEQO"
    elif "EQO" in row_text:
        return "EQO"
    elif "CHR" in row_text or "TLR" in row_text:
        return "CHR"
    return None

if uploaded_file:

    df_all = pd.read_excel(uploaded_file, sheet_name=None)

    records = []

    for sheet, df in df_all.items():
        for i, row in df.iterrows():

            row_text = " ".join([str(x) for x in row.values])
            rank = detect_rank(row_text)

            if not rank:
                continue

            for cell in row:
                start = extract_time(cell)

                if start:
                    if any(x in str(cell).upper() for x in ["OFF","AL","TRN","HOLIDAY"]):
                        continue

                    hour = start[:2] + ":00"
                    records.append([hour, rank])

    if records:
        df_result = pd.DataFrame(records, columns=["Time","Rank"])

        pivot = df_result.pivot_table(index="Time",
                                      columns="Rank",
                                      aggfunc=len,
                                      fill_value=0)

        pivot["TOTAL"] = pivot.sum(axis=1)
        pivot = pivot.sort_index()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📋 Result")
            st.dataframe(pivot)

        with col2:
            st.subheader("🔥 Peak Time")
            st.success(pivot["TOTAL"].idxmax())

        st.subheader("📈 Trend")
        st.line_chart(pivot["TOTAL"])

        st.subheader("📊 Rank Distribution")
        st.bar_chart(pivot.drop(columns=["TOTAL"]))

    else:
        st.warning("未讀到有效數據")