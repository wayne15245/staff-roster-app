import streamlit as st
import pandas as pd
import re

st.title("📊 Roster Auto Analyzer")

uploaded_file = st.file_uploader("拖 Excel 入嚟", type=["xlsx","xlsm"])

def extract_time(cell):

    # ✅ 1. 原始值
    text = str(cell)

    # ✅ 2. 嘗試抓完整 datetime
    m_dt = re.search(r"(\\d{1,2}):(\\d{2})", text)
    if m_dt:
        hour = m_dt.group(1).zfill(2)
        return hour + "00"

    # ✅ 3. 抓 0730-1630
    m = re.search(r"(\\d{3,4})-(\\d{3,4})", text)
    if m:
        return m.group(1).zfill(4)

    # ✅ 4. 抓純數字 730 / 0730
    m2 = re.match(r"^\\d{3,4}$", text.strip())
    if m2:
        return m2.group().zfill(4)

    return None


def detect_rank(row_text):
    row_text = str(row_text).upper()

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

    df_all = pd.read_excel(uploaded_file, sheet_name=None, header=None)

    records = []

    for sheet_name, df in df_all.items():

        st.write(f"🔍 分析 Sheet: {sheet_name}")

        for r in range(df.shape[0]):

            row = df.iloc[r]
            row_text = " ".join([str(x) for x in row.values])

            rank = detect_rank(row_text)

            if not rank:
                continue

            for c in range(df.shape[1]):

                cell = df.iat[r, c]
                start = extract_time(cell)

                if start:

                    text = str(cell).upper()

