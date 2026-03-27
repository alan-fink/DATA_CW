import streamlit as st
import pandas as pd
import numpy as np

def show():
    st.title("Cleaning & Preparation Studio")

    if st.session_state.get("df_working") is None:
        st.warning("Dataset hasn't been loaded. Go to Page A first and upload your file.")
        return

    df = st.session_state.df_working
    st.success(f"Working on: **{st.session_state.file_name}** — {df.shape[0]:,} rows × {df.shape[1]} cols")

    section = st.selectbox("Choose cleaning operation", [
        "4.1 — Missing Values",
        "4.2 — Duplicates",
        "4.3 — Data Types",
        "4.4 — Categorical Tools",
        "4.5 — Numeric Cleaning",
        "4.6 — Normalization",
        "4.7 — Column Operations",
        "4.8 — Data Validation",
    ])

    st.markdown("---")

    # ── 4.1
    if section == "4.1 — Missing Values":
        st.markdown("### 4.1 — Missing Values")
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if missing.empty:
            st.success("✅ No missing values in this dataset!")
        else:
            st.dataframe(missing.reset_index().rename(
                columns={"index": "Column", 0: "Missing Count"}
            ), width='stretch')
        st.markdown("#### Fix missing values")
        col = st.selectbox("Select column", df.columns.tolist(), key="mv_col")
        action = st.radio("Action", [
            "Drop rows with missing values",
            "Fill with mean",
            "Fill with median",
            "Fill with mode",
            "Fill with constant value",
            "Forward fill",
            "Backward fill"
        ], key="mv_action")
        if action == "Fill with constant value":
            constant = st.text_input("Enter constant value", key="mv_const")
        before = df[col].isnull().sum()
        st.caption(f"Currently missing in **{col}**: {before} rows")
        if st.button("✅ Apply", key="mv_apply"):
            df_new = df.copy()
            try:
                if action == "Drop rows with missing values":
                    df_new = df_new.dropna(subset=[col])
                elif action == "Fill with mean":
                    df_new[col] = df_new[col].fillna(df_new[col].mean())
                elif action == "Fill with median":
                    df_new[col] = df_new[col].fillna(df_new[col].median())
                elif action == "Fill with mode":
                    df_new[col] = df_new[col].fillna(df_new[col].mode()[0])
                elif action == "Fill with constant value":
                    df_new[col] = df_new[col].fillna(constant)
                elif action == "Forward fill":
                    df_new[col] = df_new[col].ffill()
                elif action == "Backward fill":
                    df_new[col] = df_new[col].bfill()
                after = df_new[col].isnull().sum()
                st.session_state.df_working = df_new
                st.session_state.transform_log.append({"operation": "Missing Values", "column": col, "action": action})
                st.success(f"Done! Missing in **{col}**: {before} → {after}")
            except Exception as e:
                st.error(f"Error: {e}")

    # ── 4.2
    elif section == "4.2 — Duplicates":
        st.markdown("### 4.2 — Duplicates")
        total_dups = df.duplicated().sum()
        st.metric("Full duplicate rows", total_dups)
        mode = st.radio("Check duplicates by",
            ["All columns", "Subset of columns"], key="dup_mode", horizontal=True)
        subset = None
        if mode == "Subset of columns":
            subset = st.multiselect("Select key columns", df.columns.tolist(), key="dup_cols")
        if subset is not None and len(subset) > 0:
            st.metric("Duplicates by selected columns", df.duplicated(subset=subset).sum())
        if st.checkbox("Show duplicate rows", key="dup_show"):
            dup_subset = subset if subset and len(subset) > 0 else None
            st.dataframe(df[df.duplicated(subset=dup_subset, keep=False)].head(50), width='stretch')
        keep = st.radio("When removing, keep which?", ["first", "last"], key="dup_keep", horizontal=True)
        if st.button("Remove duplicates", key="dup_apply"):
            before = len(df)
            dup_subset = subset if subset and len(subset) > 0 else None
            df_new = df.drop_duplicates(subset=dup_subset, keep=keep)
            st.session_state.df_working = df_new
            st.session_state.transform_log.append({"operation": "Remove Duplicates", "subset": str(dup_subset), "keep": keep})
            st.success(f"Removed {before - len(df_new)} rows. {len(df_new):,} rows remaining.")

    # ── 4.3
    elif section == "4.3 — Data Types":
        st.markdown("### 4.3 — Data Types & Parsing")
        st.dataframe(
            pd.DataFrame({"Column": df.columns, "Current Type": df.dtypes.values.astype(str)}),
            width='stretch', hide_index=True
        )
        col = st.selectbox("Select column to convert", df.columns.tolist(), key="dt_col")
        target = st.selectbox("Convert to", ["numeric", "categorical", "datetime", "string"], key="dt_target")
        fmt = ""
        if target == "datetime":
            fmt = st.text_input("Date format (leave blank for auto)", placeholder="%Y-%m-%d", key="dt_fmt")
        if target == "numeric":
            st.caption("💡 Dirty strings like '$1,000' will be cleaned automatically.")
        if st.button("🔄 Convert", key="dt_apply"):
            df_new = df.copy()
            try:
                if target == "numeric":
                    df_new[col] = df_new[col].astype(str).str.replace(r"[^\d.\-]", "", regex=True)
                    df_new[col] = pd.to_numeric(df_new[col], errors="coerce")
                elif target == "categorical":
                    df_new[col] = df_new[col].astype("category")
                elif target == "datetime":
                    fmt_val = fmt.strip() if fmt.strip() else None
                    df_new[col] = pd.to_datetime(df_new[col], format=fmt_val, errors="coerce")
                elif target == "string":
                    df_new[col] = df_new[col].astype(str)
                st.session_state.df_working = df_new
                st.session_state.transform_log.append({"operation": "Type Conversion", "column": col, "to": target})
                st.success(f"✅ **{col}** converted to {target}!")
            except Exception as e:
                st.error(f"Error: {e}")

    # ── 4.4
    elif section == "4.4 — Categorical Tools":
        st.markdown("### 4.4 — Categorical Tools")
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        if not cat_cols:
            st.info("No categorical columns found.")
        else:
            col = st.selectbox("Select column", cat_cols, key="cat_col")
            action = st.selectbox("Action", [
                "Trim whitespace & standardize case",
                "Value mapping / replacement",
                "Group rare categories into Other",
                "One-hot encode"
            ], key="cat_action")

            if action == "Trim whitespace & standardize case":
                case = st.radio("Case", ["lowercase", "UPPERCASE", "Title Case"], key="cat_case", horizontal=True)
                if st.button("Apply", key="cat_apply1"):
                    df_new = df.copy()
                    df_new[col] = df_new[col].astype(str).str.strip()
                    if case == "lowercase":
                        df_new[col] = df_new[col].str.lower()
                    elif case == "UPPERCASE":
                        df_new[col] = df_new[col].str.upper()
                    else:
                        df_new[col] = df_new[col].str.title()
                    st.session_state.df_working = df_new
                    st.session_state.transform_log.append({"operation": "Standardize Case", "column": col, "case": case})
                    st.success("Done!")

            elif action == "Value mapping / replacement":
                st.caption("Enter old → new value pairs:")
                n = st.number_input("Number of mappings", 1, 20, 2, key="cat_n")
                mapping = {}
                for i in range(int(n)):
                    c1, c2 = st.columns(2)
                    old = c1.text_input(f"Old value {i+1}", key=f"old_{i}")
                    new = c2.text_input(f"New value {i+1}", key=f"new_{i}")
                    if old:
                        mapping[old] = new
                if st.button("Apply mapping", key="cat_apply2") and mapping:
                    df_new = df.copy()
                    df_new[col] = df_new[col].replace(mapping)
                    st.session_state.df_working = df_new
                    st.session_state.transform_log.append({"operation": "Value Mapping", "column": col, "mapping": str(mapping)})
                    st.success(f"Applied {len(mapping)} mapping(s)!")

            elif action == "Group rare categories into Other":
                threshold = st.slider("Frequency threshold (%)", 1, 20, 5, key="cat_thresh")
                freq = df[col].value_counts(normalize=True) * 100
                rare = freq[freq < threshold].index.tolist()
                st.caption(f"{len(rare)} rare categories will become 'Other': {rare[:5]}")
                if st.button("Apply", key="cat_apply3"):
                    df_new = df.copy()
                    df_new[col] = df_new[col].where(~df_new[col].isin(rare), other="Other")
                    st.session_state.df_working = df_new
                    st.session_state.transform_log.append({"operation": "Group Rare Categories", "column": col, "threshold": threshold})
                    st.success("Done!")

            elif action == "One-hot encode":
                if st.button("Apply one-hot encoding", key="cat_apply4"):
                    df_new = pd.get_dummies(df, columns=[col], prefix=col)
                    st.session_state.df_working = df_new
                    st.session_state.transform_log.append({"operation": "One-Hot Encoding", "column": col})
                    st.success(f"Column **{col}** one-hot encoded! New shape: {df_new.shape}")

    # ── 4.5
    elif section == "4.5 — Numeric Cleaning":
        st.markdown("### 4.5 — Numeric Cleaning & Outliers")
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not num_cols:
            st.info("No numeric columns found.")
        else:
            col = st.selectbox("Select column", num_cols, key="nc_col")
            method = st.radio("Detection method", ["IQR", "Z-score"], key="nc_method", horizontal=True)
            series = df[col].dropna()
            if method == "IQR":
                Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
                IQR = Q3 - Q1
                outliers = (df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)
            else:
                z = (df[col] - series.mean()) / series.std()
                outliers = z.abs() > 3
            st.metric("Outliers detected", int(outliers.sum()))
            action = st.radio("Action", [
                "Do nothing",
                "Remove outlier rows",
                "Cap at 5th and 95th percentile"
            ], key="nc_action")
            if action != "Do nothing" and st.button("Apply", key="nc_apply"):
                df_new = df.copy()
                if action == "Remove outlier rows":
                    before = len(df_new)
                    df_new = df_new[~outliers]
                    st.success(f"Removed {before - len(df_new)} outlier rows.")
                elif action == "Cap at 5th and 95th percentile":
                    lo, hi = df_new[col].quantile(0.05), df_new[col].quantile(0.95)
                    df_new[col] = df_new[col].clip(lo, hi)
                    st.success(f"Values capped to [{lo:.2f}, {hi:.2f}].")
                st.session_state.df_working = df_new
                st.session_state.transform_log.append({"operation": "Outlier Handling", "column": col, "action": action})

    # ── 4.6
    elif section == "4.6 — Normalization":
        st.markdown("### 4.6 — Normalization / Scaling")
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not num_cols:
            st.info("No numeric columns found.")
        else:
            selected = st.multiselect("Select columns to scale", num_cols, key="norm_cols")
            method = st.radio("Method", ["Min-Max (0–1)", "Z-score standardization"], key="norm_method", horizontal=True)
            if selected:
                st.caption("Before:")
                st.dataframe(df[selected].describe().loc[["mean", "std", "min", "max"]], width='stretch')
            if selected and st.button("Apply scaling", key="norm_apply"):
                df_new = df.copy()
                for c in selected:
                    if method == "Min-Max (0–1)":
                        mn, mx = df_new[c].min(), df_new[c].max()
                        df_new[c] = (df_new[c] - mn) / (mx - mn) if mx != mn else 0
                    else:
                        mu, sigma = df_new[c].mean(), df_new[c].std()
                        df_new[c] = (df_new[c] - mu) / sigma if sigma != 0 else 0
                st.caption("After:")
                st.dataframe(df_new[selected].describe().loc[["mean", "std", "min", "max"]], width='stretch')
                st.session_state.df_working = df_new
                st.session_state.transform_log.append({"operation": "Scaling", "method": method, "columns": selected})
                st.success("Scaling applied!")

    # ── 4.7
    elif section == "4.7 — Column Operations":
        st.markdown("### 4.7 — Column Operations")
        op = st.selectbox("Operation", [
            "Rename column",
            "Drop columns",
            "Create new column (formula)",
            "Bin numeric column"
        ], key="colop")

        if op == "Rename column":
            col = st.selectbox("Column to rename", df.columns.tolist(), key="ren_col")
            new_name = st.text_input("New name", key="ren_name")
            if st.button("Rename", key="ren_apply") and new_name:
                df_new = df.rename(columns={col: new_name})
                st.session_state.df_working = df_new
                st.session_state.transform_log.append({"operation": "Rename", "from": col, "to": new_name})
                st.success(f"Renamed **{col}** → **{new_name}**")

        elif op == "Drop columns":
            to_drop = st.multiselect("Select columns to drop", df.columns.tolist(), key="drop_cols")
            if st.button("Drop", key="drop_apply") and to_drop:
                df_new = df.drop(columns=to_drop)
                st.session_state.df_working = df_new
                st.session_state.transform_log.append({"operation": "Drop Columns", "dropped": to_drop})
                st.success(f"Dropped: {to_drop}")

        elif op == "Create new column (formula)":
            new_col = st.text_input("New column name", key="formula_name")
            st.caption("Examples: `salary * 0.1`, `experience_years + 5`, `skills_count / 2`")
            formula = st.text_input("Formula", key="formula_expr")
            if st.button("Create", key="formula_apply") and new_col and formula:
                try:
                    df_new = df.copy()
                    local_vars = {c: df_new[c] for c in df_new.columns}
                    local_vars.update({"log": np.log, "sqrt": np.sqrt, "abs": np.abs})
                    df_new[new_col] = eval(formula, {"__builtins__": {}}, local_vars)
                    st.session_state.df_working = df_new
                    st.session_state.transform_log.append({"operation": "Create Column", "name": new_col, "formula": formula})
                    st.success(f"Column **{new_col}** created!")
                except Exception as e:
                    st.error(f"Formula error: {e}")

        elif op == "Bin numeric column":
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            col = st.selectbox("Column to bin", num_cols, key="bin_col")
            n_bins = st.slider("Number of bins", 2, 20, 5, key="bin_n")
            bin_method = st.radio("Method", ["Equal-width", "Quantile"], key="bin_method", horizontal=True)
            new_col = st.text_input("New column name", value=f"{col}_bin", key="bin_name")
            if st.button("Bin", key="bin_apply"):
                df_new = df.copy()
                if bin_method == "Equal-width":
                    df_new[new_col] = pd.cut(df_new[col], bins=n_bins, labels=False)
                else:
                    df_new[new_col] = pd.qcut(df_new[col], q=n_bins, labels=False, duplicates="drop")
                st.session_state.df_working = df_new
                st.session_state.transform_log.append({"operation": "Bin Column", "column": col, "bins": n_bins})
                st.success(f"Binned **{col}** into **{new_col}**!")

    # ── 4.8
    elif section == "4.8 — Data Validation":
        st.markdown("### 4.8 — Data Validation Rules")
        rule = st.selectbox("Rule type", [
            "Numeric range check",
            "Allowed categories list",
            "Non-null constraint"
        ], key="val_rule")

        violations = pd.DataFrame()

        if rule == "Numeric range check":
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            col = st.selectbox("Column", num_cols, key="val_num_col")
            lo = st.number_input("Min allowed", value=float(df[col].min()), key="val_lo")
            hi = st.number_input("Max allowed", value=float(df[col].max()), key="val_hi")
            if st.button("Check", key="val_num_check"):
                violations = df[(df[col] < lo) | (df[col] > hi)]
                st.warning(f"{len(violations)} violations found.")

        elif rule == "Allowed categories list":
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
            col = st.selectbox("Column", cat_cols, key="val_cat_col")
            allowed_raw = st.text_input("Allowed values (comma-separated)", key="val_allowed")
            if st.button("Check", key="val_cat_check") and allowed_raw:
                allowed = [v.strip() for v in allowed_raw.split(",")]
                violations = df[~df[col].isin(allowed)]
                st.warning(f"{len(violations)} violations found.")

        elif rule == "Non-null constraint":
            col = st.selectbox("Column", df.columns.tolist(), key="val_null_col")
            if st.button("Check", key="val_null_check"):
                violations = df[df[col].isnull()]
                st.warning(f"{len(violations)} null violations found.")

        if not violations.empty:
            st.dataframe(violations.head(100), width='stretch')
            st.download_button("⬇️ Export violations CSV",
                violations.to_csv(index=False).encode(),
                "violations.csv", "text/csv")

    # ── Transformation log
    st.markdown("---")
    st.markdown("### 📝 Transformation Log")
    if st.session_state.transform_log:
        log_df = pd.DataFrame(st.session_state.transform_log)
        st.dataframe(log_df, width='stretch')
        if st.button("↩️ Undo last step"):
            st.session_state.transform_log.pop()
            st.rerun()
    else:
        st.caption("No transformations applied yet.")