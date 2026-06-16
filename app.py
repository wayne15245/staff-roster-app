import streamlit as st
import pandas as pd
import re

st.title("📊 Roster Analyzer (PRO Version)")

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


def detect_date_headers(df):

    date_cols = {}

    for r in range(5):  # 掃前幾行
        for c in range(df.shape[1]):
            val = str(df.iat[r, c])

            # match 22-Jun-26
            if re.search(r"\\d{1,2}-[A-Za-z]{3}-\\d{2}", val):
                date_cols[c] = val

    return date_cols


def extract_shift(text):

    text = str(text)

    m = re.search(r"(\\d{3,4})-(\\d{3,4})", text)
    if m:
        start = m.group(1).zfill(4)
        end = m.group(2).zfill(4)
        return start, end

    return None, None


def split_hours(start, end):

    start_h = int(start[:2])
    end_h = int(end[:2])

    hours = []

    if end_h < start_h:  # 跨日
        end_h += 24

    for h in range(start_h, end_h):
        hours.append(f"{h % 24:02d}:00")

    return hours


if uploaded_file:

    df_all = pd.read_excel(uploaded_file, sheet_name=None, header=None)

    records = []

    for sheet_name, df in df_all.items():

        st.subheader(f"🔍 Sheet: {sheet_name}")

        date_cols = detect_date_headers(df)

        if len(date_cols) == 0:
            continue

        st.write(f"📅 日期欄位: {date_cols}")

        for r in range(df.shape[0]):

            row = df.iloc[r].fillna("")
            row_text = " ".join(row.values)

            rank = detect_rank(row_text)

            if not rank:
                continue

            for c in date_cols:

                cell = row[c]

                if str(cell).strip() == "":
                    continue

                text = str(cell).upper()

                if any(x in text for x in ["OFF","AL","TRN","HOLIDAY","S/HOLIDAY"]):
                    continue

                start, end = extract_shift(text)

                if not start:
                    continue

                hours = split_hours(start, end)

                for h in hours:
                    records.append([h, rank])

                st.write(f"✅ {text} → {hours} ({rank})")

    st.write(f"📊 Total records: {len(records)}")

    if len(records) == 0:
        st.error("❗ 無法解析 → 但已非常接近成功")
    else:
        result = pd.DataFrame(records, columns=["Time","Rank"])

        pivot = result.pivot_table(index="Time",
                                   columns="Rank",
                                   aggfunc=len,
                                   fill_value=0)

        pivot["TOTAL"] = pivot.sum(axis=1)
        pivot = pivot.sort_index()

        st.subheader("📋 人手表")
        st.dataframe(pivot)

        st.subheader("📈 人手趨勢")
        st.line_chart(pivot["TOTAL"])

        st.subheader("🔥 高峰時間")
        st.success(pivot["TOTAL"].idxmax())