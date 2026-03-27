import streamlit as st
import pandas as pd
import io

def show():
    st.title("Upload & Overview")
    st.markdown("Upload your dataset to get started. Supported: **CSV**, **Excel (.xlsx)**, **JSON**")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx", "json"]
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        ext = uploaded_file.name.split(".")[-1].lower()

        with st.spinner("Loading the dataset..."):
            try:
                if ext == "csv":
                    df = pd.read_csv(io.BytesIO(file_bytes))
                elif ext == "xlsx":
                    df = pd.read_excel(io.BytesIO(file_bytes))
                elif ext == "json":
                    df = pd.read_json(io.BytesIO(file_bytes))

                st.session_state.df_original = df.copy()
                st.session_state.df_working = df.copy()
                st.session_state.file_name = uploaded_file.name
            except Exception as e:
                st.error(f"Could not read file: {e}")
                return

    if st.session_state.df_working is None:
        st.info("Upload a file above to begin.")
        return

    df = st.session_state.df_working
    st.success(f"Loaded **{st.session_state.file_name}** — {df.shape[0]:,} rows × {df.shape[1]} columns")

    st.markdown("# Column Names & Types")
    col_info = pd.DataFrame({
        "Column": df.columns,
        "Type": df.dtypes.values.astype(str),
        "Non-Null Count": df.notnull().sum().values,
        "Missing (%)": (df.isnull().mean() * 100).round(2).values,
        "Unique Values": df.nunique().values,
    })
    st.dataframe(col_info, width='stretch', hide_index=True)

    st.markdown("# Summary Statistics")
    tab1, tab2 = st.tabs(["Numeric columns", "Categorical columns"])

    with tab1:
        st.dataframe(df.describe(include="number").T, width='stretch')

    with tab2:
        st.dataframe(df.describe(include="object").T, width='stretch')

    st.markdown("# Data Preview")
    st.dataframe(df.head(50), width='stretch')

    if st.button("Reset Session"):
        st.session_state.df_original = None
        st.session_state.df_working = None
        st.session_state.file_name = None
        st.session_state.transform_log = []
        st.rerun()