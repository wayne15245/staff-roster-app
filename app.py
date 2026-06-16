import streamlit as st
import pandas as pd
import re

st.title("📊 Roster Analyzer (Final Mapping Version)")

uploaded_file = st.file_uploader("拖 Excel 入嚟", type=["xlsx","xlsm"])

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

def detect_time_headers(df):

    header_map = {}

    for r in range(min(20, df.shape[0])):  # 掃前20行
        for c in range(df.shape[1]):

            val = str(df.iat[r, c])

            # ✅ match 07:30 / 0730
            m = re.search(r"(\\d{1,2}):(\\d{2})", val)
            if m:
                hour = m.group(1).zfill(2)
                header_map[c] = hour + ":00"

            m2 = re.match(r"^\\d{3,4}$", val.strip())
            if m2:
                hour = val[:2].zfill(2)
                header_map[c] = hour + ":00"

    return header_map


if uploaded_file:

    df_all = pd.read_excel(uploaded_file, sheet_name=None, header=None)

    records = []

    for sheet_name, df in df_all.items():

        st.write(f"🔍 分析 Sheet: {sheet_name}")

        header_map = detect_time_headers(df)

        if len(header_map) == 0:
            continue

        st.write(f"⏰ 偵測到時間欄位：{header_map}")

        for r in range(df.shape[0]):

            row = df.iloc[r].fillna("")
            row_text = " ".join(row.values)

            rank = detect_rank(row_text)

            if not rank:
                continue

            for c in header_map:

                cell = row[c]

                if str(cell).strip() == "":
                    continue

                text = str(cell).upper()

                if any(x in text for x in ["OFF","AL","TRN","HOLIDAY","S/HOLIDAY"]):
                    continue

                hour = header_map[c]

                records.append([hour, rank])

                st.write(f"✅ Row {r} Col {c} → {hour} ({rank})")

    st.write(f"📊 records: {len(records)}")

    if len(records) == 0:
        st.error("❗ 未成功配對 → 需要再針對你個Excel調 headers")
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

        st.subheader("📈 人手趨勢")
        st.line_chart(pivot["TOTAL"])

        st.subheader("🔥 高峰時間")
        st.success(pivot["TOTAL"].idxmax())
