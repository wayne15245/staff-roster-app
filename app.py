import streamlit as st
import pandas as pd
import re

st.title("Roster Analyzer (Step 1)")

uploaded_file = st.file_uploader("Upload Excel", type=["xlsx","xlsm"])


# ✅ 抽取 shift（關鍵）
def extract_shift(text):
    text = str(text)
    m = re.search(r"(\d{3,4}-\d{3,4})", text)
    if m:
        return m.group(1)
    return None


if uploaded_file:

    df = pd.read_excel(uploaded_file, header=None)

    results = []

    for r in range(len(df)):

        cell = str(df.iat[r, 0]).strip().upper()

        # ✅ 找 team（第一個字）
        if len(cell) > 0 and cell[0] in ["C","D","E","F"]:

            team = f"Team {cell[0]}"

            if r+1 >= len(df):
                continue

            shift_row = df.iloc[r+1, 1:8]

            for i in range(len(shift_row)):

                raw_shift = shift_row.iloc[i]
                shift = extract_shift(raw_shift)

                if shift:
                    results.append({
                        "Team": team,
                        "Shift": shift,
                        "Day": f"{22+i}/6"
                    })

    df_result = pd.DataFrame(results)

    st.subheader("✅ Step 1: Shift Detection")
    st.dataframe(df_result)