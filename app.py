import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.title("📊 Roster Auto Analyzer")

uploaded_file = st.file_uploader("拖 Excel 入嚟", type=["xlsx","xlsm"])

def extract_time(cell):
    # ✅ 1. 處理 datetime / time類型
    if isinstance(cell, (pd.Timestamp, datetime)):
        return cell.strftime("%H%M")

    # ✅ 2. 強制轉字串
    text = str(cell)

    # ✅ 3. match 0730-1630
    m = re.search(r"(\\d{3,4})\\s*-\\s*(\\d{3,4})", text)
    if m:
        return m.group(1).zfill(4)

    # ✅ 4. match 07:30
    m2 = re.search(r"(\\d{1,2}):(\\d{2})", text)
    if m2:
        h = m2.group(1).zfill(2)
        return h + "00"

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

                    if any(x in text for x in ["OFF","AL","TRN","HOLIDAY","S/HOLIDAY"]):
                        continue

                    hour = start[:2] + ":00"

                    records.append([hour, rank])

                    st.write(f"✅ {cell} → {hour} ({rank})")  # debug

    st.write(f"📊 records: {len(records)}")

    if len(records) == 0:
        st.error("❗ 這份 Excel 用另一種格式（需要最後調整）")
    else:
        result = pd.DataFrame(records, columns=["Time","Rank"])

        pivot = result.pivot_table(index="Time",
                                   columns="Rank",
                                   aggfunc=len,
                                   fill_value=0)

