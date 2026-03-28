import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("🤖 AI Excel Data Cleaner")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "csv"])

if uploaded_file:

    # -------- READ FILE --------
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    original_df = df.copy().astype(str)

    # -------- CLEANING --------
    df = original_df.copy()

    formatting_count = 0
    standard_count = 0

    for col in df.columns:
        for i in range(len(df)):
            old = df.iloc[i][col]

            # formatting
            new = old.strip()
            if "email" in col.lower():
                new = new.lower()

            if old != new:
                formatting_count += 1

            # standardization
            final = new.title()
            if new != final:
                standard_count += 1

            df.at[df.index[i], col] = final

    # -------- DUPLICATES --------
    before_rows = df.shape[0]
    df = df.drop_duplicates()
    duplicates_removed = before_rows - df.shape[0]

    # -------- SCORE (CORRECT LOGIC) --------
    def count_issues(data):
        issues = 0
        data = data.astype(str)

        for col in data.columns:
            # spaces
            issues += sum(data[col] != data[col].str.strip())

            # case issues
            issues += sum(data[col] != data[col].str.title())

        return issues

    # Count issues
    before_issues = count_issues(original_df)
    after_issues = count_issues(df)

    total_cells = original_df.shape[0] * original_df.shape[1]

    # Calculate scores
    if total_cells == 0:
        before_score = 100
        after_score = 100
    else:
        before_score = round((1 - before_issues / total_cells) * 100, 2)
        after_score = round((1 - after_issues / total_cells) * 100, 2)

    # Safety
    before_score = max(0, min(100, before_score))
    after_score = max(0, min(100, after_score))

    # -------- DISPLAY --------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 Original Data")
        st.dataframe(original_df, height=200)

    with col2:
        st.subheader("📤 Cleaned Data")
        st.dataframe(df, height=200)

    # -------- CHANGES (SIMPLE & CLEAN) --------
    st.subheader("🛠 Summary of Changes")

    st.write(f"🔁 Duplicates Removed: {duplicates_removed}")
    st.write(f"🧹 Formatting Fixes: {formatting_count}")
    st.write(f"✨ Standardizations: {standard_count}")
    st.write(f"📊 Before Score: {before_score}")
    st.write(f"📈 After Score: {after_score}")

    # -------- DOWNLOAD --------
    st.download_button(
        "📥 Download Cleaned File",
        df.to_csv(index=False),
        file_name="cleaned_data.csv",
        mime="text/csv"
    )
