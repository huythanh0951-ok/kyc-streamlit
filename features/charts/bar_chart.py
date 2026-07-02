import plotly.express as px
import pandas as pd


def create_horizontal_bar(df, y_col, value_col, color, height=250, top_n=None):
    counts = df.groupby(y_col)[value_col].nunique().sort_values(ascending=True).reset_index()
    counts.columns = [y_col, "Học viên"]
    if top_n:
        counts = counts.tail(top_n)
    fig = px.bar(counts, x="Học viên", y=y_col, orientation="h",
                 text_auto=True, color_discrete_sequence=[color])
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=height,
                      xaxis_title="", yaxis_title="", showlegend=False,
                      paper_bgcolor="white", plot_bgcolor="white",
                      dragmode=False)
    fig.update_xaxes(gridcolor="#f0f0f0")
    fig.update_yaxes(tickfont=dict(size=13 if not top_n else 12))
    return fig


def create_top_n_bar(df, col_name, color, top_n=15, height=250):
    counts = df[col_name].value_counts().head(top_n + 5).iloc[::-1].reset_index()
    counts.columns = [col_name, "Học viên"]
    # Bỏ noise: "tổng", "total", "không có thông tin"
    noise = {"tổng", "tong", "total", "không có thông tin", "-", "--", ""}
    counts = counts[~counts[col_name].astype(str).str.strip().str.lower().isin(noise)]
    counts = counts.head(top_n)
    fig = px.bar(counts, x="Học viên", y=col_name, orientation="h",
                 text_auto=True, color_discrete_sequence=[color])
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=height,
                      xaxis_title="", yaxis_title="", showlegend=False,
                      paper_bgcolor="white", plot_bgcolor="white",
                      dragmode=False)
    fig.update_yaxes(tickfont=dict(size=12))
    fig.update_xaxes(gridcolor="#f0f0f0")
    return fig


def create_parent_job_bar(df, color, top_n=15, height=300):
    """Gộp PH1 + PH2 → top nghề nghiệp PH"""
    ph1 = df[["Parent 1 Job"]].rename(columns={"Parent 1 Job": "Job"})
    ph2 = df[["Parent 2 Job"]].rename(columns={"Parent 2 Job": "Job"})
    # Chỉ giữ row có tên PH (nếu cột tồn tại)
    if "Parent 1 Name" in df.columns:
        ph1 = ph1[df["Parent 1 Name"].notna()]
    if "Parent 2 Name" in df.columns:
        ph2 = ph2[df["Parent 2 Name"].notna()]
    combined = pd.concat([ph1, ph2], ignore_index=True)
    # Lọc: bỏ NaN, "Không có thông tin", và các giá trị nhiễu như "tổng", "total"
    mask = combined["Job"].notna() & (combined["Job"] != "Không có thông tin")
    # Bỏ các giá trị không phải nghề nghiệp thật
    noise = {"tổng", "tong", "total", "khác", "khong", "-", "--", ""}
    mask = mask & ~combined["Job"].astype(str).str.strip().str.lower().isin(noise)
    cleaned = combined[mask]
    counts = cleaned["Job"].value_counts().head(top_n).iloc[::-1].reset_index()
    counts.columns = ["Nghề nghiệp", "Số PH"]
    fig = px.bar(counts, x="Số PH", y="Nghề nghiệp", orientation="h",
                 text_auto=True, color_discrete_sequence=[color])
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=height,
                      xaxis_title="", yaxis_title="", showlegend=False,
                      paper_bgcolor="white", plot_bgcolor="white",
                      dragmode=False)
    fig.update_yaxes(tickfont=dict(size=12))
    fig.update_xaxes(gridcolor="#f0f0f0")
    return fig
