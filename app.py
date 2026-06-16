import streamlit as st
import pandas as pd
import re

st.title("📊 Roster Analyzer (FINAL SUCCESS VERSION)")

uploaded_file = st.file_uploader("拖 Excel 入嚟", type=["xlsx","xlsm"])

# ✅ detect rank
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

# ✅ detect date columns
def detect_date_cols(df):
    cols = {}
    for c in range(df.shape[1]):
        for r in range(5):
            val = str(df.iat[r, c])
            if re.search(r"\d{1,2}-[A-Za-z]{3}-\d{2}", val):
                cols[c] = val
    return cols

# ✅ extract shift
def extract_shift(text):
    m = re.search(r"(\d{3,4})-(\d{3,4})", str(text))
    if m:
        return m.group(1).zfill(4), m.group(2).zfill(4)
    return None, None

# ✅ split time
def split_hours(start, end):
    s = int(start[:2])
    e = int(end[:2])
    if e < s:
        e += 24
    return [f"{h%24:02d}:00" for h in range(s, e)]

if uploaded_file:

    df_all = pd.read_excel(uploaded_file, sheet_name=None, header=None)

    records = []

    for sheet_name, df in df_all.items():

        st.subheader(f"🔍 Sheet: {sheet_name}")

        date_cols = detect_date_cols(df)

        if not date_cols:
            continue

        st.write(f"📅 日期欄位: {date_cols}")

        rows, cols = df.shape

        for r in range(rows):

            row_text = " ".join([str(x) for x in df.iloc[r].values])

            rank = detect_rank(row_text)

            if not rank:
                continue

            # ✅ 向下找 shift（最關鍵）
            for offset in range(1, 4):

                if r + offset >= rows:
                    continue

                next_row = df.iloc[r + offset]

                for c in date_cols:

                    cell = next_row[c]

                    if str(cell).strip() == "":
                        continue

                    if any(x in str(cell).upper() for x in ["OFF","AL","TRN","HOLIDAY","S/HOLIDAY"]):
                        continue

                    start, end = extract_shift(cell)

                    if not start:
                        continue

                    hours = split_hours(start, end)

                    for h in hours:
                        records.append([h, rank])

                    st.write(f"✅ {cell} → {hours} ({rank})")

    st.write(f"📊 Total records: {len(records)}")

    if records:
        df_result = pd.DataFrame(records, columns=["Time","Rank"])

        pivot = df_result.pivot_table(index="Time",
                                      columns="Rank",
                                      aggfunc=len,
                                      fill_value=0)

        pivot["TOTAL"] = pivot.sum(axis=1)
        pivot = pivot.sort_index()

        st.subheader("📋 人手分析")
        st.dataframe(pivot)

        st.subheader("📈 趨勢")
        st.line_chart(pivot["TOTAL"])

        st.subheader("🔥 高峰")
        st.success(pivot["TOTAL"].idxmax())

    else:
        st.error("❗ 如果仲係0，我可以幫你做到完全 custom 版（最後1%）")