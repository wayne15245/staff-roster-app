import streamlit as st
import pandas as pd
import re

st.title("📊 Roster Auto Analyzer")

uploaded_file = st.file_uploader("拖 Excel 入嚟", type=["xlsx","xlsm"])

def extract_time_any(text):

    text = str(text)

    # ✅ 1. 0730-1630
    m = re.search(r"(\\d{3,4})\\s*-\\s*(\\d{3,4})", text)
    if m:
        return m.group(1).zfill(4)

    # ✅ 2. 07:30
    m2 = re.search(r"(\\d{1,2}):(\\d{2})", text)
    if m2:
        return m2.group(1).zfill(2) + "00"

    # ✅ 3. 單獨時間（730 / 0730）
    m3 = re.search(r"\\b(\\d{3,4})\\b", text)
    if m3:
        val = m3.group(1)
        if 3 <= len(val) <= 4:
            return val.zfill(4)

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


if uploaded_file:

    df_all = pd.read_excel(uploaded_file, sheet_name=None, header=None, dtype=str)

    records = []

    for sheet_name, df in df_all.items():

        st.write(f"🔍 分析 Sheet: {sheet_name}")

        for r in range(df.shape[0]):

            row = df.iloc[r].fillna("")
            row_text = " ".join(row.values)

            rank = detect_rank(row_text)

            if not rank:
                continue

            # ✅ 🔥 關鍵改動：掃整行文字（唔逐cell）
            start = extract_time_any(row_text)

            if start:

                hour = start[:2] + ":00"
                records.append([hour, rank])

                st.write(f"✅ {row_text[:50]} → {hour} ({rank})")

    st.write(f"📊 records: {len(records)}")

    if len(records) == 0:
        st.error("❗ 呢份 roster 用非常特殊格式（可能係 merge + display only）")
    else:
        result = pd.DataFrame(records, columns=["Time","Rank"])

        pivot = result.pivot_table(index="Time",
                                   columns="Rank",
                                   aggfunc=len,
                                   fill_value=0)

        pivot["TOTAL"] = pivot.sum(axis=1)
        pivot = pivot.sort_index()

        st.subheader("📋 Result")
        st.dataframe(pivot)

        st.subheader("📈 Trend")
        st.line_chart(pivot["TOTAL"])

        st.subheader("🔥 Peak")
        st.success(pivot["TOTAL"].idxmax())
