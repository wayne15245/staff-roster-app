import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.title("📊 Roster Analyzer (Hourly Version)")

uploaded_file = st.file_uploader("拖 Excel 入嚟", type=["xlsx","xlsm"])

# ✅ 分類職級
def classify_rank(text):
    text = str(text).upper()

    if "SUP" in text:
        return "SUP"
    elif "SEQO" in text:
        return "SEQO"
    elif "EQO" in text:
        return "EQO"
    elif "CHR" in text:
        return "CHR"

    return None

# ✅ 判斷 shift
def is_shift(text):
    return bool(re.search(r"\d{3,4}-\d{3,4}", str(text)))

# ✅ 拆時間
def split_hours(shift):

    m = re.search(r"(\d{3,4})-(\d{3,4})", shift)

    if not m:
        return []

    start = m.group(1).zfill(4)
    end = m.group(2).zfill(4)

    sh = int(start[:2])
    eh = int(end[:2])

    hours = []

    if eh < sh:
        eh += 24  # 跨日

    for h in range(sh, eh):
        hours.append(f"{h%24:02d}:00")

    return hours

if uploaded_file:

    df = pd.read_excel(uploaded_file, sheet_name="Team C-F", header=None)

    results = []
    hourly_records = []

    rows = len(df)

    for r in range(rows):

        cell = str(df.iat[r, 0]).strip()

        if re.match(r"^[CDEF]$", cell):

            team = f"Team {cell}"

            shift_row = df.iloc[r+1, 1:8]

            # ✅ count team 人數
            counts = {
                "SUP": 0,
                "SEQO": 0,
                "EQO": 0,
                "CHR": 0
            }

            for rr in range(r+2, rows):

                next_cell = str(df.iat[rr, 0]).strip()

                if re.match(r"^[CDEF]$", next_cell):
                    break

                val = str(df.iat[rr, 8])
                rank = classify_rank(val)

                if rank:
                    counts[rank] += 1

            # ✅ 每日 shift
            for i in range(len(shift_row)):

                shift = shift_row.iloc[i]

                if not is_shift(shift):
                    continue

                day = f"{22+i}/6"

                total = sum(counts.values())

                results.append({
                    "Date": day,
                    "Team": team,
                    "Shift": shift,
                    "SUP": counts["SUP"],
                    "SEQO": counts["SEQO"],
                    "EQO": counts["EQO"],
                    "CHR": counts["CHR"],
                    "TOTAL": total
                })

                # ✅ 🔥 每小時分拆
                hours = split_hours(shift)

                for h in hours:
                    hourly_records.append({
                        "Date": day,
                        "Hour": h,
                        "Manpower": total
                    })

    df_result = pd.DataFrame(results)
    df_hourly = pd.DataFrame(hourly_records)

    # ✅ 顯示主表
    st.subheader("📊 Team 分析")
    st.dataframe(df_result)

    # ✅ 每小時合計
    hourly_summary = df_hourly.groupby(["Date","Hour"])["Manpower"].sum().reset_index()

    st.subheader("⏰ 每小時人手")
    st.dataframe(hourly_summary)

    # ✅ 畫圖
    pivot = hourly_summary.pivot(index="Hour", columns="Date", values="Manpower")

    st.subheader("📈 每小時趨勢")
    st.line_chart(pivot)

    # ✅ Peak
    peak = hourly_summary.loc[hourly_summary["Manpower"].idxmax()]

    st.subheader("🔥 高峰時段")
    st.success(f"{peak['Date']} {peak['Hour']} → {peak['Manpower']}人")

    # ✅ 匯出
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_result.to_excel(writer, index=False, sheet_name="Team")
        hourly_summary.to_excel(writer, index=False, sheet_name="Hourly")

    st.download_button(
        "📥 下載 Excel",
        data=output.getvalue(),
        file_name="Roster_Hourly.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )