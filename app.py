import streamlit as st
import pandas as pd

st.title("📊 Roster Analyzer (Final Stable Version)")

uploaded_file = st.file_uploader("拖 Excel 入嚟", type=["xlsx","xlsm"])

# ✅ 固定時間段（你公司實際）
TIME_SLOTS = [
    "07:00","08:00","09:00","10:00","11:00","12:00",
    "13:00","14:00","15:00","16:00","17:00","18:00",
    "19:00","20:00","21:00","22:00","23:00","00:00"
]

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

    df_all = pd.read_excel(uploaded_file, sheet_name=None, header=None)

    records = []

    for sheet_name, df in df_all.items():

        st.write(f"🔍 分析 Sheet: {sheet_name}")

        for r in range(df.shape[0]):

            row = df.iloc[r].fillna("")
            row_text = " ".join(row.values)

            rank = detect_rank(row_text)

            if not rank:
                continue

            # ✅ 假設班表從第3欄開始（可之後微調）
            for c in range(2, min(2+len(TIME_SLOTS), df.shape[1])):

                cell = row[c]

                if str(cell).strip() == "":
                    continue

                text = str(cell).upper()

                if any(x in text for x in ["OFF","AL","TRN","HOLIDAY","S/HOLIDAY"]):
                    continue

                hour = TIME_SLOTS[c-2]

                records.append([hour, rank])

                st.write(f"✅ Row {r} Col {c} → {hour} ({rank})")

    st.write(f"📊 records: {len(records)}")

    if len(records) == 0:
        st.error("❗ 需要微調起始欄位（但已接近成功）")
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