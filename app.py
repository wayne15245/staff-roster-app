import streamlit as st
import pandas as pd
import re

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

if uploaded_file:

    try:
        df_all = pd.read_excel(uploaded_file, sheet_name=None, header=None)

        records = []

        for sheet_name, df in df_all.items():

            st.write(f"🔍 正在分析 Sheet: {sheet_name}")

            for r in range(df.shape[0]):
                for c in range(df.shape[1]):

                    cell = df.iat[r, c]

                    start = extract_time(cell)

                    if start:
                        cell_text = str(cell).upper()

                        if any(x in cell_text for x in ["OFF","AL","TRN","HOLIDAY","S/HOLIDAY"]):
                            continue

                        # ✅ 用 row context 判斷 rank
                        row_text = " ".join([str(x) for x in df.iloc[r].values])
                        rank = detect_rank(row_text)

                        if not rank:
                            continue

                        hour = start[:2] + ":00"

                        records.append([hour, rank])

        st.write(f"✅ 找到 records: {len(records)}")   # 🔥 debug

        if len(records) == 0:
            st.error("⚠️ 讀到 Excel，但找不到任何 shift（格式未match）")
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

    except Exception as e:
        st.error(f"❌ 出錯：{e}")