import streamlit as st
import pandas as pd
import re

st.title("📊 Roster Analyzer (Phase 1 Dashboard)")

uploaded_file = st.file_uploader("拖 Excel 入嚟", type=["xlsx","xlsm"])


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
    else:
        return None


if uploaded_file:

    all_sheets = pd.read_excel(uploaded_file, sheet_name=None, header=None)

    results = {}

    for sheet_name, df in all_sheets.items():

        st.write(f"🔍 分析 Sheet: {sheet_name}")

        for r in range(len(df)):

            cell = str(df.iat[r, 0]).strip()

            # ✅ 找 Team（A, B, C...）
            if re.match(r"^[A-Z]$", cell):

                team = f"Team {cell}"

                if r + 1 >= len(df):
                    continue

                shift_row = df.iloc[r + 1, 1:8]

                for i in range(len(shift_row)):

                    shift = shift_row.iloc[i]

                    if pd.isna(shift):
                        continue

                    shift = str(shift)

                    if "OFF" in shift:
                        continue

                    day = f"{22+i}/6"

                    key = (day, team, shift)

                    if key not in results:
                        results[key] = {
                            "SUP": 0,
                            "SEQO": 0,
                            "EQO": 0,
                            "CHR": 0
                        }

                    # ✅ 向下掃 Column I
                    for rr in range(r+2, min(r+40, len(df))):

                        val = str(df.iat[rr, 8])

                        rank = classify_rank(val)

                        if rank:
                            results[key][rank] += 1

    # =========================
    # ✅ Phase 1 升級開始
    # =========================

    data = []

    for (day, team, shift), counts in results.items():

        total = counts["SUP"] + counts["SEQO"] + counts["EQO"] + counts["CHR"]

        data.append({
            "Date": day,
            "Team": team,
            "Shift": shift,
            "SUP": counts["SUP"],
            "SEQO": counts["SEQO"],
            "EQO": counts["EQO"],
            "CHR": counts["CHR"],
            "TOTAL": total
        })

    df_result = pd.DataFrame(data)

    if len(df_result) == 0:
        st.error("❗ 未找到數據")
    else:

        # ✅ 顯示全部表
        st.subheader("📊 全數據表")
        st.dataframe(df_result)

        # ✅ Filter
        st.subheader("🎯 篩選")

        selected_day = st.selectbox("選擇日期", sorted(df_result["Date"].unique()))
        selected_team = st.selectbox("選擇 Team", sorted(df_result["Team"].unique()))

        filtered_df = df_result[
            (df_result["Date"] == selected_day) &
            (df_result["Team"] == selected_team)
        ]

        st.dataframe(filtered_df)

        # ✅ Summary
        summary = df_result.groupby("Date")["TOTAL"].sum().reset_index()

        st.subheader("📈 每日總人手")
        st.dataframe(summary)

        st.line_chart(summary.set_index("Date"))
