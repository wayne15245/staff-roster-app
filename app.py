import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.title("📊 Roster Analyzer (Hourly + Rank Version)")

uploaded_file = st.file_uploader("拖 Excel 入嚟", type=["xlsx","xlsm"])

# ✅ 職級分類
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

# ✅ Shift 判斷（純時間）
def is_shift(text):
    text = str(text).strip()
    return bool(re.match(r"^\d{3,4}-\d{3,4}$", text))

# ✅ 拆時間
def split_hours(shift):

    m = re.search(r"(\d{3,4})-(\d{3,4})", shift)
    if not m:
        return []

    start = m.group(1).zfill(4)
    end = m.group(2).zfill(4)

    sh = int(start[:2])
    eh = int(end[:2])

    if eh < sh:
        eh += 24  # ✅ 跨日

    hours = []
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

            # ✅ 計人數（block）
            counts = {"SUP":0, "SEQO":0, "EQO":0, "CHR":0}

            for rr in range(r+2, rows):

                next_cell = str(df.iat[rr, 0]).strip()

                if re.match(r"^[CDEF]$", next_cell):
                    break

                val = str(df.iat[rr, 8])
                rank = classify_rank(val)

                if rank:
                    counts[rank] += 1

            total = sum(counts.values())

            # ✅ 每日處理
            for i in range(len(shift_row)):

                shift = shift_row.iloc[i]

                if not is_shift(shift):
                    continue

                day = f"{22+i}/6"

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

                # ✅ 每小時拆分（🔥分職級）
                hours = split_hours(shift)

                for h in hours:
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

    # ✅ 主表
    st.subheader("📊 Team 分析")
    st.dataframe(df_result)

    # =========================
    # ✅ Hourly（分職級）
    # =========================
    if len(df_hourly) > 0:

        hourly_summary = df_hourly.groupby(["Date","Hour"]).sum().reset_index()

        st.subheader("⏰ 每小時人手（分職級）")
        st.dataframe(hourly_summary)

        # ✅ 圖（TOTAL）
        pivot_total = hourly_summary.pivot(index="Hour", columns="Date", values="TOTAL")
        st.subheader("📈 每小時總人手")
        st.line_chart(pivot_total)

        # ✅ SUP chart（例）
        pivot_sup = hourly_summary.pivot(index="Hour", columns="Date", values="SUP")
        st.subheader("📈 SUP 每小時")
        st.line_chart(pivot_sup)

        # ✅ Peak
        peak = hourly_summary.loc[hourly_summary["TOTAL"].idxmax()]
        st.success(f"🔥 高峰：{peak['Date']} {peak['Hour']} → {peak['TOTAL']}人")

    else:
        st.error("❗ 未能產生每小時數據")
        hourly_summary = pd.DataFrame()

    # ✅ Excel 匯出
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_result.to_excel(writer, index=False, sheet_name="Team")
        hourly_summary.to_excel(writer, index=False, sheet_name="Hourly")

    st.download_button(
        "📥 下載 Excel",
        data=output.getvalue(),
        file_name="Roster_Final_With_Hourly.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )