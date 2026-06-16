import streamlit as st
import pandas as pd
import re

st.title("📊 Roster Analyzer - Simple Version")

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

        st.write(f"🔍 {sheet_name}")

        for r in range(len(df)):

            cell = str(df.iat[r, 0]).strip()

            # ✅ 找 Team（例如 C, D, E）
            if re.match(r"^[A-Z]$", cell):

                team = f"Team {cell}"

                # ✅ 下一行 = shift
                if r + 1 >= len(df):
                    continue

                shift_row = df.iloc[r + 1, 1:8]

                for i in range(len(shift_row)):

                    shift = shift_row[i]

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

    # ✅ 顯示結果
    for key in results:

        day, team, shift = key

        st.write(f"### 📅 {day}")
        st.write(f"{team} → {shift}")

        st.write(f"SUP: {results[key]['SUP']}")
        st.write(f"SEQO: {results[key]['SEQO']}")
        st.write(f"EQO: {results[key]['EQO']}")
        st.write(f"CHR: {results[key]['CHR']}")

        st.write("---")