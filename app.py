import streamlit as st
import pandas as pd
import re

st.title("📊 Roster Auto Analyzer")

uploaded_file = st.file_uploader("拖 Excel 入嚟", type=["xlsx","xlsm"])

def extract_time(cell):
    text = str(cell)

    # ✅ 放鬆匹配（只要有4位數字-4位數字）
    m = re.search(r"(\\d{3,4})\\s*-\\s*(\\d{3,4})", text)
    if m:
        return m.group(1).zfill(4)  # 補0 → 730變0730

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

            for cell in row:

                start = extract_time(cell)

                if start:

                    text = str(cell).upper()

                    if any(x in text for x in ["OFF","AL","TRN","HOLIDAY","S/HOLIDAY"]):
                        continue

                    hour = start[:2] + ":00"

                    records.append([hour, rank])

                    # ✅ debug：顯示讀到嘅shift
                    st.write(f"✅ 找到: {cell} → {hour} ({rank})")

    st.write(f"📊 總 records: {len(records)}")

    if len(records) == 0:
        st.error("❌ 完全匹配不到 shift → 需要再微調格式規則")
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