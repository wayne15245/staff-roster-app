import streamlit as st
import pandas as pd
import re

st.set_page_config(layout="wide")
st.title("📊 Roster Auto Analyzer")

uploaded_file = st.file_uploader("拖 Excel 入嚟", type=["xlsx","xlsm"])

def extract_time(cell):
    if isinstance(cell, str):
        m = re.search(r"(\\d{4})-(\\d{4})", cell)
        if m:
            return m.group(1)
    return None

def detect_rank(text):
    text = str(text).upper()
    if "SUP" in text:
        return "SUP"
    elif "SEQO" in text:
        return "SEQO"
    elif "EQO" in text:
        return "EQO"
    elif "CHR" in text or "TLR" in text:
        return "CHR"
    return None

def find_rank_upwards(df, row_idx, col_idx):
    # ✅ 向上找 rank
    for i in range(row_idx, -1, -1):
        val = df.iat[i, col_idx]
        r = detect_rank(val)
        if r:
            return r
    return None

if uploaded_file:

    df_all = pd.read_excel(uploaded_file, sheet_name=None, header=None)

    records = []

    for sheet_name, df in df_all.items():

        rows, cols = df.shape

        for r in range(rows):
            for c in range(cols):

                cell = df.iat[r, c]

                start = extract_time(cell)

                if start:
                    cell_text = str(cell).upper()

                    if any(x in cell_text for x in ["OFF","AL","TRN","HOLIDAY","S/HOLIDAY"]):
                        continue

                    rank = find_rank_upwards(df, r, c)

                    if not rank:
                        continue

                    hour = start[:2] + ":00"

                    records.append([hour, rank])

    if records:
        result = pd.DataFrame(records, columns=["Time","Rank"])

        pivot = result.pivot_table(index="Time",
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
            st.subheader("🔥 Peak")
            st.success(pivot["TOTAL"].idxmax())

        st.subheader("📈 Trend")
