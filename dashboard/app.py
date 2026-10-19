"""
Student Success & Value Benchmark — interactive demo dashboard.

Run:  streamlit run dashboard/app.py   (from the repo root)

Reads the synthetic CSVs in ../data and recreates a Power BI-style
student-success benchmark layout: KPI cards, trend line, bar comparison,
peer scatter, and a working filter panel.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------- palette
NAVY = "#0A2A4A"
TEAL = "#0E7C7B"
GOLD = "#D9A441"
TEAL_DARK = "#0B5F5E"
GREY_TXT = "#5A6B7B"
PEER_DOT = "#C9BFA8"

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

st.set_page_config(
    page_title="Student Success & Value Benchmark",
    page_icon="🎓",
    layout="wide",
)

# ------------------------------------------------------------------ CSS
st.markdown(
    f"""
    <style>
    .stApp {{ background: #FFFFFF; }}
    .banner {{
        background: linear-gradient(120deg, {NAVY} 0%, {NAVY} 55%, {TEAL} 100%);
        border-radius: 10px;
        padding: 26px 34px;
        margin-bottom: 18px;
    }}
    .banner h1 {{ color: white; margin: 0; font-size: 34px; font-weight: 700; }}
    .banner p {{ color: {GOLD}; margin: 4px 0 0 0; font-size: 17px;
                 font-style: italic; }}
    .kpi {{
        background: #FFFFFF;
        border: 1px solid #E3E8ED;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 1px 4px rgba(10,42,74,0.08);
        height: 148px;
    }}
    .kpi .icon {{
        width: 44px; height: 44px; border-radius: 50%;
        background: {TEAL}; color: white;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 22px; float: left; margin-right: 12px;
    }}
    .kpi .label {{ color: {NAVY}; font-weight: 600; font-size: 14px;
                   padding-top: 2px; }}
    .kpi .value {{ color: {TEAL_DARK}; font-size: 34px; font-weight: 700;
                   clear: both; padding-top: 6px; }}
    .kpi .delta {{ font-size: 14px; font-weight: 600; }}
    .up {{ color: #1E7E34; }} .down {{ color: #C0392B; }}
    .filter-box {{
        background: #F7F9FA;
        border: 1px solid #E3E8ED;
        border-radius: 12px;
        overflow: hidden;
    }}
    .filter-head {{
        background: {NAVY}; color: white; font-weight: 700;
        font-size: 16px; letter-spacing: 1px; padding: 12px 18px;
    }}
    .filter-body {{ padding: 8px 14px 16px 14px; }}
    .chart-card {{
        background: #FFFFFF;
        border: 1px solid #E3E8ED;
        border-radius: 12px;
        padding: 14px 16px 6px 16px;
        box-shadow: 0 1px 4px rgba(10,42,74,0.08);
        margin-bottom: 16px;
    }}
    .chart-title {{ color: {NAVY}; font-weight: 700; font-size: 16px; }}
    .chart-sub {{ color: {GREY_TXT}; font-size: 12px; margin-bottom: 4px; }}
    .footer {{ color: {GREY_TXT}; font-size: 12px; padding: 10px 4px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ data
@st.cache_data
def load():
    fact = pd.read_csv(DATA_DIR / "fact_student_outcomes.csv")
    bench = pd.read_csv(DATA_DIR / "peer_benchmark.csv")
    peers = pd.read_csv(DATA_DIR / "peer_institutions.csv")
    dims = {
        "residency": pd.read_csv(DATA_DIR / "dim_residency.csv"),
        "student_type": pd.read_csv(DATA_DIR / "dim_student_type.csv"),
        "pell": pd.read_csv(DATA_DIR / "dim_pell_status.csv"),
        "race": pd.read_csv(DATA_DIR / "dim_race_ethnicity.csv"),
    }
    return fact, bench, peers, dims

fact, bench, peers, dims = load()

# ---------------------------------------------------------------- header
st.markdown(
    """
    <div class="banner">
      <h1>Student Success &amp; Value Benchmark</h1>
      <p>Measuring outcomes. Driving impact.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("All figures on this page are **synthetic demo data** — "
           "no real institution's numbers are used.")

# ---------------------------------------------------------------- layout
main, side = st.columns([3.6, 1])

with side:
    st.markdown(
        '<div class="filter-box"><div class="filter-head">FILTERS</div>'
        '<div class="filter-body">',
        unsafe_allow_html=True,
    )
    f_cohort = st.selectbox("Cohort",
                            ["All Cohorts"] + sorted(fact["cohort_year"].unique().tolist()))
    f_res = st.selectbox("Residency",
                         ["All"] + dims["residency"]["residency"].tolist())
    f_type = st.selectbox("Student Type",
                          ["All"] + dims["student_type"]["student_type"].tolist())
    f_race = st.selectbox("Race/Ethnicity",
                          ["All"] + dims["race"]["race_ethnicity"].tolist())
    f_pell = st.selectbox("Pell Status",
                          ["All"] + dims["pell"]["pell_status"].tolist())
    st.info("Filters apply to the KPI cards and cohort charts. The peer scatter below compares institutions, so it stays put.")
    st.markdown("</div></div>", unsafe_allow_html=True)

# ------------------------------------------------------------ filtering
f = fact.copy()
if f_cohort != "All Cohorts":
    f = f[f["cohort_year"] == f_cohort]
if f_res != "All":
    key = dims["residency"].query("residency == @f_res")["residency_key"].iloc[0]
    f = f[f["residency_key"] == key]
if f_type != "All":
    key = dims["student_type"].query("student_type == @f_type")["student_type_key"].iloc[0]
    f = f[f["student_type_key"] == key]
if f_race != "All":
    key = dims["race"].query("race_ethnicity == @f_race")["race_key"].iloc[0]
    f = f[f["race_key"] == key]
if f_pell != "All":
    key = dims["pell"].query("pell_status == @f_pell")["pell_key"].iloc[0]
    f = f[f["pell_key"] == key]

years = sorted(f["cohort_year"].unique().tolist())
b = bench[bench["cohort_year"].isin(years)].copy()
# year weights from the (filtered) demo headcount, for fair benchmark averages
w = f.groupby("cohort_year")["cohort_n"].sum()
b["w"] = b["cohort_year"].map(w)

def wavg(col):
    sub = b.dropna(subset=[col])
    return float((sub[col] * sub["w"]).sum() / sub["w"].sum()) if len(sub) else None

# ----------------------------------------------------------------- KPIs
ret = f["retained_1yr_n"].sum() / f["cohort_n"].sum() * 100
b_ret = wavg("benchmark_retention")

g4 = f.dropna(subset=["grad_4yr_n"])
g4_rate = g4["grad_4yr_n"].sum() / g4["cohort_n"].sum() * 100 if len(g4) else None
b_g4 = wavg("benchmark_grad_4yr")

g6 = f.dropna(subset=["grad_6yr_n"])
g6_rate = g6["grad_6yr_n"].sum() / g6["cohort_n"].sum() * 100 if len(g6) else None
b_g6 = wavg("benchmark_grad_6yr")

debt = (f["cohort_n"] * f["avg_debt_usd"]).sum() / f["cohort_n"].sum()
b_debt = wavg("benchmark_debt")

def kpi_card(icon, label, value, delta_html):
    st.markdown(
        f'<div class="kpi"><span class="icon">{icon}</span>'
        f'<div class="label">{label}</div>'
        f'<div class="value">{value}</div>'
        f'<div class="delta">{delta_html}</div></div>',
        unsafe_allow_html=True,
    )

def pp_delta(demo, bench_v, suffix="vs Benchmark"):
    if demo is None or bench_v is None:
        return '<span style="color:#999">n/a</span>'
    d = demo - bench_v
    arrow = "▲" if d >= 0 else "▼"
    cls = "up" if d >= 0 else "down"
    return f'<span class="{cls}">{arrow} {abs(d):.1f} pp</span> {suffix}'

with main:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("👥", "First-Year Retention", f"{ret:.1f}%",
                 pp_delta(ret, b_ret))
    with c2:
        val = f"{g4_rate:.1f}%" if g4_rate else "n/a"
        kpi_card("🎓", "Four-Year Graduation", val, pp_delta(g4_rate, b_g4))
    with c3:
        val = f"{g6_rate:.1f}%" if g6_rate else "n/a"
        kpi_card("📜", "Six-Year Graduation", val, pp_delta(g6_rate, b_g6))
    with c4:
        diff = b_debt - debt
        arrow, cls = ("▼", "up") if diff >= 0 else ("▲", "down")
        kpi_card("💲", "Average Debt", f"${debt:,.0f}",
                 f'<span class="{cls}">{arrow} ${abs(diff):,.0f}</span> vs Benchmark')

    # -------------------------------------------------- charts, row 1
    ch1, ch2 = st.columns(2)

    trend = f.groupby("cohort_year").agg(
        n=("cohort_n", "sum"), r=("retained_1yr_n", "sum")).reset_index()
    trend["demo"] = trend["r"] / trend["n"] * 100
    trend = trend.merge(b[["cohort_year", "benchmark_retention"]], on="cohort_year")
    # alternate label positions so neighboring years don't collide
    demo_pos = ["top center" if i % 2 == 0 else "bottom center"
                for i in range(len(trend))]

    with ch1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend["cohort_year"], y=trend["demo"],
                                 mode="lines+markers+text", name="Demo",
                                 line=dict(color=TEAL, width=3),
                                 marker=dict(size=9, color=TEAL),
                                 text=[f"{v:.1f}%" for v in trend["demo"]],
                                 textposition=demo_pos,
                                 textfont=dict(size=11, color=TEAL)))
        fig.add_trace(go.Scatter(x=trend["cohort_year"],
                                 y=trend["benchmark_retention"],
                                 mode="lines+markers+text", name="Benchmark",
                                 line=dict(color=NAVY, width=2.5, dash="dash"),
                                 marker=dict(size=8, color=NAVY),
                                 text=[f"{v:.1f}%" for v in trend["benchmark_retention"]],
                                 textposition="bottom center",
                                 textfont=dict(size=11, color=NAVY)))
        fig.update_layout(
            title=dict(text="First-Year Retention Rate Comparison (Fall Cohorts)",
                       font=dict(color=NAVY, size=16)),
            yaxis=dict(ticksuffix="%", range=[75, 92]),
            xaxis=dict(dtick=1, tickmode="linear"),
            margin=dict(l=10, r=10, t=50, b=10), height=380,
            legend=dict(orientation="h", y=1.08),
            plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    g4y = g4.groupby("cohort_year").agg(
        n=("cohort_n", "sum"), gg=("grad_4yr_n", "sum")).reset_index()
    g4y["demo"] = g4y["gg"] / g4y["n"] * 100
    g4y = g4y.merge(b[["cohort_year", "benchmark_grad_4yr"]], on="cohort_year")

    with ch2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=g4y["cohort_year"], y=g4y["demo"], name="Demo",
                             marker_color=TEAL,
                             text=[f"{v:.1f}%" for v in g4y["demo"]],
                             textposition="outside",
                             textfont=dict(size=11, color=TEAL)))
        fig.add_trace(go.Bar(x=g4y["cohort_year"], y=g4y["benchmark_grad_4yr"],
                             name="Benchmark", marker_color=NAVY,
                             text=[f"{v:.1f}%" for v in g4y["benchmark_grad_4yr"]],
                             textposition="outside",
                             textfont=dict(size=11, color=NAVY)))
        fig.update_layout(
            title=dict(text="Four-Year Graduation Rate Comparison (Cohorts)",
                       font=dict(color=NAVY, size=16)),
            barmode="group", bargap=0.25,
            yaxis=dict(ticksuffix="%", range=[0, 78]),
            xaxis=dict(dtick=1, tickmode="linear", type="category"),
            margin=dict(l=10, r=10, t=50, b=10), height=380,
            legend=dict(orientation="h", y=1.08),
            plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------- scatter
    demo_pt = peers[peers["is_demo"]]
    other = peers[~peers["is_demo"]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=other["avg_net_price"], y=other["completion_rate"],
                             mode="markers", name="Peer institutions",
                             marker=dict(size=10, color=PEER_DOT,
                                         line=dict(width=1, color="#8A7F63")),
                             text=other["institution"],
                             hovertemplate="%{text}<br>Completion: %{y:.1f}%"
                                           "<br>Net price: $%{x:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=demo_pt["avg_net_price"], y=demo_pt["completion_rate"],
                             mode="markers+text", name="Demo University",
                             marker=dict(size=18, color=TEAL,
                                         line=dict(width=2, color=NAVY)),
                             text=["Demo University"], textposition="middle right",
                             textfont=dict(size=13, color=TEAL_DARK),
                             hovertemplate="Demo University<br>Completion: %{y:.1f}%"
                                           "<br>Net price: $%{x:,.0f}<extra></extra>"))
    fig.update_layout(
        title=dict(text="Peer Benchmark: Completion Rate vs. Net Price",
                   font=dict(color=NAVY, size=16)),
        xaxis=dict(title="Average Net Price (USD)",
                   tickprefix="$", range=[4000, 42000]),
        yaxis=dict(title="Completion Rate (150% of Normal Time)",
                   ticksuffix="%", range=[30, 95]),
        margin=dict(l=10, r=10, t=60, b=10), height=420,
        legend=dict(orientation="h", y=1.08),
        plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

st.markdown(
    '<div class="footer">Source: synthetic demo data generated for this portfolio '
    'project · Peer figures styled after College Scorecard public benchmarks · '
    'Data as of Fall 2025 (fictional)</div>',
    unsafe_allow_html=True,
)
