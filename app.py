import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.title("📊 Roster Analyzer (Final Working Version)")

uploaded_file = st.file_uploader("拖 Excel 入嚟", type=["xlsx","xlsm"])

# ✅ 職級分類
def classify_rank(text):
    text = str(text).upper()
    if "SUP" in text: return "SUP"
    elif "SEQO" in text: return "SEQO"
    elif "EQO" in text: return "EQO"
    elif "CHR" in text: return "CHR"
    return None

# ✅ 抽取 shift（任何亂格式都識）
def extract_shift(text):
    text = str(text)
    m = re.search(r"(\d{3,4}-\d{3,4})", text)
    return m.group(1) if m else None

# ✅ 拆每小時
def split_hours(shift):
    m = re.search(r"(\d{3,4})-(\d{3,4})", shift)
    if not m: return []

    start = int(m.group(1).zfill(4)[:2])
    end = int(m.group(2).zfill(4)[:2])

    if end < start:
        end += 24

    return [f"{h%24:02d}:00" for h in range(start, end)]

if uploaded_file:

    df = pd.read_excel(uploaded_file, sheet_name=None, header=None)

    results = []
    hourly_records = []
    alerts = []

    for sheet_name, df in df.items():

        rows = len(df)

        for r in range(rows):

            raw_cell = str(df.iat[r, 0])
            cell = raw_cell.strip().upper()

            # ✅ ✅ ✅ 最強Team detection
            if len(cell) == 0:
                continue

            team_char = cell[0]

            if team_char not in ["C", "D", "E", "F"]:
                continue

            team = f"Team {team_char}"

            # ✅ shift row
            if r+1 >= rows:
                continue

            shift_row = df.iloc[r+1, 1:8]

            # ✅ 計人數（block-based）
            counts = {"SUP":0, "SEQO":0, "EQO":0, "CHR":0}

            for rr in range(r+2, rows):

                next_raw = str(df.iat[rr, 0])
                next_cell = next_raw.strip().upper()

                if len(next_cell) > 0:
                    next_char = next_cell[0]

                    if next_char in ["C","D","E","F"]:
                        break

                rank = classify_rank(df.iat[rr, 8])

                if rank:
                    counts[rank] += 1

            total = sum(counts.values())

            # ✅ 每日處理
            for i in range(len(shift_row)):

                raw_shift = shift_row.iloc[i]
                shift = extract_shift(raw_shift)

                if not shift:
                    continue

                day = f"{22+i}/6"

                # ✅ KPI
                if counts["SUP"] < 2:
                    alerts.append(f"🔴 {day} {team} {shift} SUP不足")

                if total < 6:
                    alerts.append(f"🟠 {day} {team} 人手不足")

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

                # ✅ 每小時
                for h in split_hours(shift):
                    hourly_records.append({
                        "Date": day,
                        "Hour": h,
                        "TOTAL": total
                    })

    df_result = pd.DataFrame(results)
    df_hourly = pd.DataFrame(hourly_records)

    # ✅ Debug（重要！）
    st.write("DEBUG rows in result:", len(df_result))

    st.subheader("📊 Team 分析")
    st.dataframe(df_result)

    # ✅ KPI
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

        st.line_chart(
            hourly_summary.pivot(index="Hour", columns="Date", values="TOTAL")
        )
    else:
        st.warning("❗ 未能產生每小時數據")

    # ✅ Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_result.to_excel(writer, index=False, sheet_name="Team")

        if len(df_hourly) > 0:
            hourly_summary.to_excel(writer, index=False, sheet_name="Hourly")

    st.download_button(
        "📥 下載 Excel",
        data=output.getvalue(),
        file_name="Roster_Final_Working.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
``