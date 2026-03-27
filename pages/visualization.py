import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def show():
    st.title("📊 Visualization Builder")

    if st.session_state.get("df_working") is None:
        st.warning("⚠️ No dataset loaded. Go to Page A first.")
        return

    df = st.session_state.df_working
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    all_cols = df.columns.tolist()

    st.markdown("### Choose your chart")
    chart_type = st.selectbox("Chart type", [
        "Histogram",
        "Box Plot",
        "Scatter Plot",
        "Line Chart",
        "Bar Chart",
        "Heatmap / Correlation Matrix"
    ])

    st.markdown("---")

    fig, ax = plt.subplots(figsize=(10, 5))

    try:
        if chart_type == "Histogram":
            col = st.selectbox("Column (numeric)", num_cols)
            bins = st.slider("Bins", 5, 100, 20)
            ax.hist(df[col].dropna(), bins=bins, color="#4e9af1", edgecolor="white")
            ax.set_xlabel(col)
            ax.set_ylabel("Frequency")
            ax.set_title(f"Histogram of {col}")

        elif chart_type == "Box Plot":
            cols = st.multiselect("Columns (numeric)", num_cols, default=num_cols[:3])
            if cols:
                ax.boxplot([df[c].dropna() for c in cols], labels=cols)
                ax.set_title("Box Plot")
                plt.xticks(rotation=15)

        elif chart_type == "Scatter Plot":
            x_col = st.selectbox("X axis", num_cols, key="sc_x")
            y_col = st.selectbox("Y axis", num_cols, index=min(1, len(num_cols)-1), key="sc_y")
            color_col = st.selectbox("Color by (optional)", ["None"] + cat_cols, key="sc_color")
            if color_col == "None":
                ax.scatter(df[x_col], df[y_col], alpha=0.5, s=10, color="#4e9af1")
            else:
                groups = df[color_col].unique()
                colors = plt.cm.tab10(np.linspace(0, 1, len(groups)))
                for g, c in zip(groups, colors):
                    subset = df[df[color_col] == g]
                    ax.scatter(subset[x_col], subset[y_col], label=str(g), alpha=0.5, s=10, color=c)
                ax.legend(fontsize=8)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f"Scatter: {x_col} vs {y_col}")

        elif chart_type == "Line Chart":
            x_col = st.selectbox("X axis", all_cols, key="line_x")
            y_col = st.selectbox("Y axis", num_cols, key="line_y")
            agg = st.selectbox("Aggregation", ["None", "mean", "sum", "count"], key="line_agg")
            plot_df = df[[x_col, y_col]].dropna().sort_values(x_col)
            if agg != "None":
                plot_df = plot_df.groupby(x_col)[y_col].agg(agg).reset_index()
            ax.plot(plot_df[x_col], plot_df[y_col], color="#4e9af1", linewidth=1.5)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f"Line Chart: {y_col} over {x_col}")
            plt.xticks(rotation=30, ha="right")

        elif chart_type == "Bar Chart":
            x_col = st.selectbox("Category (X axis)", cat_cols, key="bar_x")
            y_col = st.selectbox("Value (Y axis)", num_cols, key="bar_y")
            agg = st.selectbox("Aggregation", ["mean", "sum", "count"], key="bar_agg")
            top_n = st.slider("Show top N", 3, 20, 10, key="bar_n")
            plot_df = df.groupby(x_col)[y_col].agg(agg).nlargest(top_n).reset_index()
            ax.bar(plot_df[x_col].astype(str), plot_df[y_col], color="#4e9af1")
            ax.set_xlabel(x_col)
            ax.set_ylabel(f"{agg}({y_col})")
            ax.set_title(f"Top {top_n} {x_col} by {agg} of {y_col}")
            plt.xticks(rotation=30, ha="right")

        elif chart_type == "Heatmap / Correlation Matrix":
            selected = st.multiselect("Select numeric columns", num_cols, default=num_cols[:6])
            if len(selected) >= 2:
                corr = df[selected].corr()
                im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
                ax.set_xticks(range(len(selected)))
                ax.set_yticks(range(len(selected)))
                ax.set_xticklabels(selected, rotation=45, ha="right", fontsize=8)
                ax.set_yticklabels(selected, fontsize=8)
                for i in range(len(selected)):
                    for j in range(len(selected)):
                        ax.text(j, i, f"{corr.iloc[i,j]:.2f}",
                                ha="center", va="center", fontsize=7)
                plt.colorbar(im, ax=ax)
                ax.set_title("Correlation Matrix")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    except Exception as e:
        st.error(f"Chart error: {e}")
        plt.close(fig)