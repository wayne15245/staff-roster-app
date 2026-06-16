import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.title("📊 Roster Analyzer (KPI Version)")

uploaded_file = st.file_uploader("拖 Excel 入嚟", type=["xlsx","xlsm"])

# ✅ 職級分類
def classify_rank(text):
    text = str(text).upper()
    if "SUP" in text: return "SUP"
    elif "SEQO" in text: return "SEQO"
    elif "EQO" in text: return "EQO"
    elif "CHR" in text: return "CHR"
    return None

# ✅ ✅ Shift標準化（關鍵）
def extract_shift(text):
    text = str(text)
    m = re.search(r"(\d{3,4}-\d{3,4})", text)
    return m.group(1) if m else None

# ✅ Shift分類
def classify_shift_type(shift):
    start = int(shift.split("-")[0].zfill(4)[:2])
    if 5 <= start < 12:
        return "Morning"
    elif 12 <= start < 18:
        return "Afternoon"
    else:
        return "Night"

# ✅ 拆小時
def split_hours(shift):
    m = re.search(r"(\d{3,4})-(\d{3,4})", shift)
    if not m: return []
    start = int(m.group(1).zfill(4)[:2])
    end = int(m.group(2).zfill(4)[:2])
    if end < start: end += 24
    return [f"{h%24:02d}:00" for h in range(start, end)]

if uploaded_file:

    df = pd.read_excel(uploaded_file, sheet_name="Team C-F", header=None)

    results = []
    hourly_records = []
    alerts = []

    rows = len(df)

    for r in range(rows):

        cell = str(df.iat[r, 0]).strip()

        if re.match(r"^[CDEF]$", cell):

            team = f"Team {cell}"
            shift_row = df.iloc[r+1, 1:8]

            counts = {"SUP":0, "SEQO":0, "EQO":0, "CHR":0}

            for rr in range(r+2, rows):

                next_cell = str(df.iat[rr, 0]).strip()
                if re.match(r"^[CDEF]$", next_cell):
                    break

                rank = classify_rank(df.iat[rr, 8])
                if rank:
                    counts[rank] += 1

            total = sum(counts.values())

            for i in range(len(shift_row)):

                raw_shift = shift_row.iloc[i]
                shift = extract_shift(raw_shift)

                if not shift:
                    continue

                day = f"{22+i}/6"
                shift_type = classify_shift_type(shift)

                # ✅ KPI檢查
                if counts["SUP"] < 2:
                    alerts.append(f"🔴 {team} {shift} SUP不足")

                if total < 6:
                    alerts.append(f"🟠 {team} {shift} 總人手不足")

                results.append({
                    "Date": day,
                    "Team": team,
                    "Shift": shift,
                    "Type": shift_type,
                    "SUP": counts["SUP"],
                    "SEQO": counts["SEQO"],
                    "EQO": counts["EQO"],
                    "CHR": counts["CHR"],
                    "TOTAL": total
                })

                # ✅ 每小時
                for h in split_hours(shift):
                    hourly_records.append({
                        "Date": day,
                        "Hour": h,
                        "SUP": counts["SUP"],
                        "SEQO": counts["SEQO"],
                        "EQO": counts["EQO"],
                        "CHR": counts["CHR"],
                        "TOTAL": total
                    })

    df_result = pd.DataFrame(results)
    df_hourly = pd.DataFrame(hourly_records)

    st.subheader("📊 Team 分析")
    st.dataframe(df_result)

    # ✅ KPI Alert顯示
    st.subheader("🚨 KPI Alerts")

    if alerts:
        for a in alerts:
            st.error(a)
    else:
        st.success("✅ 全部正常")

    # ✅ Hourly
    if len(df_hourly) > 0:

        hourly_summary = df_hourly.groupby(["Date","Hour"]).sum().reset_index()

        st.subheader("⏰ 每小時人手")
        st.dataframe(hourly_summary)

        st.line_chart(hourly_summary.pivot(index="Hour", columns="Date", values="TOTAL"))

    else:
        st.warning("冇 hourly 數據")

    # ✅ 匯出
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_result.to_excel(writer, index=False, sheet_name="Team")
        hourly_summary.to_excel(writer, index=False, sheet_name="Hourly")

    st.download_button(
        "📥 下載 Excel",
        data=output.getvalue(),
        file_name="Roster_KPI.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
``