import streamlit as st


st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="stSidebarHeader"] {display: none;}
    </style>
""", unsafe_allow_html=True)

if "df_original" not in st.session_state:
    st.session_state.df_original = None
if "df_working" not in st.session_state:
    st.session_state.df_working = None
if "transform_log" not in st.session_state:
    st.session_state.transform_log = []
if "file_name" not in st.session_state:
    st.session_state.file_name = None

st.sidebar.title("Data Wrangler")

page = st.sidebar.radio("Navigation", [
    "Upload & Overview",
    "Cleaning Studio",
    "Visualization Builder",
    "Export & Report"
])

if st.session_state.get("df_working") is not None:
    df = st.session_state.df_working
    st.sidebar.success("Dataset loaded")
    st.sidebar.caption(f" {st.session_state.file_name}")
    st.sidebar.caption(f"{df.shape[0]:,} rows × {df.shape[1]} cols")
    st.sidebar.caption(f"{len(st.session_state.transform_log)} transform(s) applied")
else:
    st.sidebar.caption("Go to Page A to upload a file.")

if page == "Upload & Overview":
    import pages.upload as page_module
elif page == "Cleaning Studio":
    import pages.cleaning as page_module
elif page == "Visualization Builder":
    import pages.visualization as page_module
elif page == "Export & Report":
    import pages.export as page_module

page_module.show()