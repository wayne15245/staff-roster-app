import streamlit as st
import pandas as pd
import re

st.title("📊 Simple Team Shift Analyzer")

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
    return None


if uploaded_file:

    df = pd.read_excel(uploaded_file, sheet_name="Team C-F", header=None)

    results = {}

    for r in range(len(df)):

        cell = str(df.iat[r, 0])  # column A

        # ✅ 發現 Team C / D
        if re.match(r"^[CDEF]$", cell.strip()):

            team = f"Team {cell.strip()}"

            # ✅ shift 在下一行
            shift_row = r + 1
            shifts = df.iloc[shift_row, 1:8].values  # B-H

            for i, shift in enumerate(shifts):

                if pd.isna(shift):
                    continue

                shift = str(shift)

                if "OFF" in shift:
                    continue

                day = f"{22+i}/6"

                key = (day, team, shift)

                if key not in results:
                    results[key] = {
                        "SUP":0,
                        "SEQO":0,
                        "EQO":0,
                        "CHR":0
                    }

                # ✅ 向下掃人員
                for rr in range(r+2, r+20):

                    val = str(df.iat[rr, 8])  # Column I

                    rank = classify_rank(val)

                    if rank:
                        results[key][rank] += 1

    # ✅ 顯示結果
    for (day, team, shift), counts in results.items():

        st.write(f"### 📅 {day}")
        st.write(f"{team} → {shift}")

        st.write(f"SUP: {counts['SUP']}")
        st.write(f"SEQO: {counts['SEQO']}")
        st.write(f"EQO: {counts['EQO']}")
        st.write(f"CHR: {counts['CHR']}")

        st.write("---")
``