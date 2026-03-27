import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime

def show():
    st.title("Export & Report")

    if st.session_state.get("df_working") is None:
        st.warning("No dataset loaded. Go to Page A first.")
        return

    df = st.session_state.df_working
    log = st.session_state.transform_log

    st.markdown(f"**Current dataset:** {df.shape[0]:,} rows × {df.shape[1]} columns")
    st.markdown(f"**Transformations applied:** {len(log)}")

    st.markdown("### Download Cleaned Dataset")
    col1, col2 = st.columns(2)

    with col1:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download as CSV",
            data=csv_bytes,
            file_name=f"cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    with col2:
        excel_buf = io.BytesIO()
        with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Cleaned Data")
        st.download_button(
            "Download as Excel",
            data=excel_buf.getvalue(),
            file_name=f"cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.markdown("### Transformation Report")

    if not log:
        st.info("No transformations logged yet. Apply some cleaning steps in Page B first.")
    else:
        report = {
            "generated_at": datetime.now().isoformat(),
            "source_file": st.session_state.file_name,
            "total_steps": len(log),
            "steps": log
        }

        log_df = pd.DataFrame(log)
        st.dataframe(log_df, width='stretch')

        recipe_json = json.dumps(report, indent=2, default=str)
        st.download_button(
            " Download JSON Recipe",
            data=recipe_json.encode("utf-8"),
            file_name=f"recipe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

        with st.expander("View raw JSON"):
            st.code(recipe_json, language="json")

    st.markdown("### Cleaned Data Preview")
    st.dataframe(df.head(50), width='stretch')