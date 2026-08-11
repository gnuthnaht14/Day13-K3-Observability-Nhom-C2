"""
Day 13 — AI Observability Dashboard
Nguồn dữ liệu: data/logs.jsonl
Chạy: python -m streamlit run dashboard.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ─── Config ────────────────────────────────────────────────────────────────────
LOG_PATH = Path("data/logs.jsonl")
TIME_RANGE_MINUTES = 60
REFRESH_SECONDS = 30

SLO = {
    "latency_p95_ms": 3000,
    "traffic_rate_per_min": 1,
    "error_rate_pct": 2.0,
    "cost_total_usd": 2.5,
    "tokens_total": 50_000,
    "quality_mean": 0.75,
}

COLORS = {
    "ok":      "#22c55e",
    "warn":    "#f59e0b",
    "bad":     "#ef4444",
    "primary": "#2563eb",
    "surface": "#f8fafc",
    "border":  "#e2e8f0",
    "text":    "#1e293b",
    "subtext": "#64748b",
    "bg":      "#ffffff",
}

# ─── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Day 13 AI Observability",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(f"""
<style>
  html, body, [class*="css"] {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: {COLORS['bg']};
      color: {COLORS['text']};
  }}
  .block-container {{ padding: 1.5rem 2.5rem 2rem; max-width: 1400px; }}

  .dash-header {{
      display: flex; align-items: center; gap: 12px;
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid {COLORS['border']};
  }}
  .dash-title {{
      font-size: 1.35rem; font-weight: 700;
      color: {COLORS['text']}; margin: 0; line-height: 1;
  }}
  .dash-sub {{
      font-size: 0.8rem; color: {COLORS['subtext']}; margin: 0;
  }}

  .card {{
      background: {COLORS['surface']};
      border: 1px solid {COLORS['border']};
      border-radius: 12px;
      padding: 1.1rem 1.2rem 0.9rem;
      margin-bottom: 1rem;
  }}
  .card-title {{
      font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em;
      text-transform: uppercase; color: {COLORS['subtext']};
      margin-bottom: 0.5rem;
  }}

  .badge-ok   {{ background:#dcfce7; color:#166534; padding:2px 9px;
                 border-radius:99px; font-size:0.72rem; font-weight:600; }}
  .badge-bad  {{ background:#fee2e2; color:#991b1b; padding:2px 9px;
                 border-radius:99px; font-size:0.72rem; font-weight:600; }}
  .badge-warn {{ background:#fef9c3; color:#854d0e; padding:2px 9px;
                 border-radius:99px; font-size:0.72rem; font-weight:600; }}

  .kpi-val {{ font-size:2rem; font-weight:700; line-height:1; }}
  .kpi-sub {{ font-size:0.78rem; color:{COLORS['subtext']}; margin-top:2px; }}

  hr {{ border:none; border-top:1px solid {COLORS['border']}; margin:0.8rem 0; }}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ───────────────────────────────────────────────────────────────────
def _badge(val, slo_val, op="lte"):
    ok = (val <= slo_val) if op == "lte" else (val >= slo_val)
    cls = "badge-ok" if ok else "badge-bad"
    label = "OK" if ok else "BREACH"
    return f'<span class="{cls}">{label}</span>'


def _slo_color(val, slo_val, op="lte"):
    ok = (val <= slo_val) if op == "lte" else (val >= slo_val)
    return COLORS["ok"] if ok else COLORS["bad"]


def _chart_layout(height=200, showlegend=False):
    return dict(
        height=height,
        margin=dict(l=0, r=0, t=6, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color=COLORS["subtext"]),
        xaxis=dict(showgrid=False, zeroline=False, showline=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor=COLORS["border"],
                   zeroline=False, showline=False, tickfont=dict(size=10)),
        showlegend=showlegend,
    )


def _chart(fig):
    """Render plotly chart with correct Streamlit API (no deprecated params)."""
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


@st.cache_data(ttl=REFRESH_SECONDS)
def load_logs() -> pd.DataFrame:
    if not LOG_PATH.exists():
        return pd.DataFrame()
    rows = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"], utc=True, errors="coerce")
    return df


# ─── Load & filter ─────────────────────────────────────────────────────────────
df_all = load_logs()

st.markdown(f"""
<div class="dash-header">
  <span style="font-size:1.6rem">📊</span>
  <div>
    <p class="dash-title">Day 13 — AI Observability Dashboard</p>
    <p class="dash-sub">
      Nguồn: {LOG_PATH} &nbsp;·&nbsp;
      Window: {TIME_RANGE_MINUTES} phút &nbsp;·&nbsp;
      Refresh: {REFRESH_SECONDS}s &nbsp;·&nbsp;
      Cập nhật: {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

if df_all.empty:
    st.error("⚠️ Không tìm thấy `data/logs.jsonl`. Hãy chạy API và load test trước.")
    st.code("python scripts/load_test.py")
    st.stop()

# Filter time window
if "ts" in df_all.columns:
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(minutes=TIME_RANGE_MINUTES)
    df = df_all[df_all["ts"] >= cutoff].copy()
else:
    df = df_all.copy()

# ─── Summary bar ───────────────────────────────────────────────────────────────
n_req = len(df[df["event"] == "request_received"])
n_err = len(df[df["event"] == "request_failed"])
rate  = round(n_err / n_req * 100, 2) if n_req > 0 else 0.0

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.metric("📋 Log records", f"{len(df):,}")
with s2:
    st.metric("📥 Requests", f"{n_req:,}")
with s3:
    st.metric("❌ Errors", f"{n_err:,}")
with s4:
    st.metric("⚡ Error rate", f"{rate:.2f}%")

st.divider()

# ─── Row 1: Latency · Traffic · Errors ─────────────────────────────────────────
col1, col2, col3 = st.columns(3)

# ── Panel 1: Latency ────────────────────────────────────────────────────────────
with col1:
    resp = df[df["event"] == "response_sent"].copy()
    if "latency_ms" in resp.columns and not resp.empty:
        lat = resp["latency_ms"].dropna().astype(float)
        p50, p95, p99 = lat.quantile(0.50), lat.quantile(0.95), lat.quantile(0.99)
        badge = _badge(p95, SLO["latency_p95_ms"], "lte")
        color_p95 = _slo_color(p95, SLO["latency_p95_ms"], "lte")

        st.markdown(f"""
        <div class="card">
          <p class="card-title">📈 Latency percentiles &nbsp; {badge}</p>
          <div style="display:flex;gap:24px;margin-bottom:0.7rem">
            <div><div class="kpi-val">{p50:.0f}</div><div class="kpi-sub">P50 ms</div></div>
            <div><div class="kpi-val" style="color:{color_p95}">{p95:.0f}</div>
                 <div class="kpi-sub">P95 ms · SLO ≤ {SLO['latency_p95_ms']}</div></div>
            <div><div class="kpi-val">{p99:.0f}</div><div class="kpi-sub">P99 ms</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if "ts" in resp.columns:
            spark = resp.set_index("ts")[["latency_ms"]].resample("1min").quantile(0.95).reset_index()
            fig = go.Figure(go.Scatter(
                x=spark["ts"], y=spark["latency_ms"],
                mode="lines", fill="tozeroy",
                line=dict(color=COLORS["primary"], width=2),
                fillcolor="rgba(37,99,235,0.08)",
            ))
            fig.add_hline(y=SLO["latency_p95_ms"], line_dash="dot",
                          line_color=COLORS["warn"], line_width=1.5,
                          annotation_text=f"SLO {SLO['latency_p95_ms']}ms",
                          annotation_font_size=10)
            fig.update_layout(**_chart_layout(160), yaxis_title="ms")
            _chart(fig)
    else:
        st.markdown('<div class="card"><p class="card-title">📈 Latency</p>'
                    '<p style="color:#94a3b8">Chưa có dữ liệu response_sent</p></div>',
                    unsafe_allow_html=True)


# ── Panel 2: Traffic ────────────────────────────────────────────────────────────
with col2:
    req_df = df[df["event"] == "request_received"].copy()
    if not req_df.empty and "ts" in req_df.columns:
        by_min = req_df.set_index("ts").resample("1min").size().reset_index(name="count")
        avg_rpm = round(by_min["count"].mean(), 1)
        badge = _badge(avg_rpm, SLO["traffic_rate_per_min"], "gte")

        st.markdown(f"""
        <div class="card">
          <p class="card-title">📊 Request traffic &nbsp; {badge}</p>
          <div style="display:flex;gap:24px;margin-bottom:0.7rem">
            <div><div class="kpi-val">{n_req:,}</div><div class="kpi-sub">Total requests</div></div>
            <div><div class="kpi-val">{avg_rpm}</div>
                 <div class="kpi-sub">avg req/min · SLO ≥ {SLO['traffic_rate_per_min']}</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure(go.Bar(
            x=by_min["ts"], y=by_min["count"],
            marker_color=COLORS["primary"], marker_line_width=0,
        ))
        fig.add_hline(y=SLO["traffic_rate_per_min"], line_dash="dot",
                      line_color=COLORS["warn"], line_width=1.5,
                      annotation_text=f"SLO ≥{SLO['traffic_rate_per_min']}",
                      annotation_font_size=10)
        fig.update_layout(**_chart_layout(160), yaxis_title="requests/min")
        _chart(fig)
    else:
        st.markdown('<div class="card"><p class="card-title">📊 Traffic</p>'
                    '<p style="color:#94a3b8">Chưa có dữ liệu</p></div>',
                    unsafe_allow_html=True)


# ── Panel 3: Errors ─────────────────────────────────────────────────────────────
with col3:
    badge = _badge(rate, SLO["error_rate_pct"], "lte")
    color_rate = _slo_color(rate, SLO["error_rate_pct"], "lte")

    st.markdown(f"""
    <div class="card">
      <p class="card-title">🚨 Error rate &amp; breakdown &nbsp; {badge}</p>
      <div style="display:flex;gap:24px;margin-bottom:0.7rem">
        <div><div class="kpi-val" style="color:{color_rate}">{rate:.2f}%</div>
             <div class="kpi-sub">error rate · SLO ≤ {SLO['error_rate_pct']}%</div></div>
        <div><div class="kpi-val">{n_err}</div>
             <div class="kpi-sub">errors / {n_req} requests</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    err_df = df[df["event"] == "request_failed"]
    if not err_df.empty and "error_type" in err_df.columns:
        breakdown = err_df["error_type"].value_counts().reset_index()
        breakdown.columns = ["Error Type", "Count"]
        fig = go.Figure(go.Bar(
            x=breakdown["Error Type"], y=breakdown["Count"],
            marker_color=COLORS["bad"], marker_line_width=0,
        ))
        fig.update_layout(**_chart_layout(160), yaxis_title="count")
        _chart(fig)
    else:
        fig = go.Figure()
        fig.add_annotation(text="✅ Không có lỗi", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=13, color=COLORS["ok"]))
        fig.update_layout(**_chart_layout(160))
        _chart(fig)


st.divider()

# ─── Row 2: Cost · Tokens · Quality ────────────────────────────────────────────
col4, col5, col6 = st.columns(3)

# ── Panel 4: Cost ───────────────────────────────────────────────────────────────
with col4:
    resp = df[df["event"] == "response_sent"].copy()
    if "cost_usd" in resp.columns and not resp.empty:
        total_cost = resp["cost_usd"].sum()
        badge = _badge(total_cost, SLO["cost_total_usd"], "lte")
        color_cost = _slo_color(total_cost, SLO["cost_total_usd"], "lte")

        st.markdown(f"""
        <div class="card">
          <p class="card-title">💰 Cost over time &nbsp; {badge}</p>
          <div style="display:flex;gap:24px;margin-bottom:0.7rem">
            <div><div class="kpi-val" style="color:{color_cost}">${total_cost:.4f}</div>
                 <div class="kpi-sub">Total USD · SLO ≤ ${SLO['cost_total_usd']}</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if "ts" in resp.columns:
            by_min = resp.set_index("ts")[["cost_usd"]].resample("1min").sum().reset_index()
            fig = go.Figure(go.Scatter(
                x=by_min["ts"], y=by_min["cost_usd"],
                mode="lines+markers", fill="tozeroy",
                line=dict(color="#7c3aed", width=2),
                fillcolor="rgba(124,58,237,0.07)",
                marker=dict(size=4),
            ))
            fig.add_hline(y=SLO["cost_total_usd"], line_dash="dot",
                          line_color=COLORS["warn"], line_width=1.5,
                          annotation_text=f"SLO ${SLO['cost_total_usd']}",
                          annotation_font_size=10)
            fig.update_layout(**_chart_layout(160), yaxis_title="USD/min")
            _chart(fig)
    else:
        st.markdown('<div class="card"><p class="card-title">💰 Cost</p>'
                    '<p style="color:#94a3b8">Chưa có dữ liệu</p></div>',
                    unsafe_allow_html=True)


# ── Panel 5: Tokens ─────────────────────────────────────────────────────────────
with col5:
    resp = df[df["event"] == "response_sent"].copy()
    if "tokens_in" in resp.columns and not resp.empty:
        total_in  = int(resp["tokens_in"].sum())
        total_out = int(resp["tokens_out"].sum()) if "tokens_out" in resp.columns else 0
        total_tok = total_in + total_out
        badge = _badge(total_tok, SLO["tokens_total"], "lte")
        color_tok = _slo_color(total_tok, SLO["tokens_total"], "lte")

        st.markdown(f"""
        <div class="card">
          <p class="card-title">🔢 Input &amp; Output tokens &nbsp; {badge}</p>
          <div style="display:flex;gap:24px;margin-bottom:0.7rem">
            <div><div class="kpi-val">{total_in:,}</div><div class="kpi-sub">tokens_in</div></div>
            <div><div class="kpi-val">{total_out:,}</div><div class="kpi-sub">tokens_out</div></div>
            <div><div class="kpi-val" style="color:{color_tok}">{total_tok:,}</div>
                 <div class="kpi-sub">Total · SLO ≤ {SLO['tokens_total']:,}</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(name="tokens_in",  x=["tokens_in"],  y=[total_in],
                             marker_color=COLORS["primary"], marker_line_width=0))
        fig.add_trace(go.Bar(name="tokens_out", x=["tokens_out"], y=[total_out],
                             marker_color="#0ea5e9", marker_line_width=0))
        fig.add_hline(y=SLO["tokens_total"] / 2, line_dash="dot",
                      line_color=COLORS["warn"], line_width=1.5,
                      annotation_text=f"½ SLO ({SLO['tokens_total']//2:,})",
                      annotation_font_size=10)
        fig.update_layout(**_chart_layout(160, showlegend=True), yaxis_title="tokens",
                          legend=dict(orientation="h", y=1.1, x=0))
        _chart(fig)
    else:
        st.markdown('<div class="card"><p class="card-title">🔢 Tokens</p>'
                    '<p style="color:#94a3b8">Chưa có dữ liệu</p></div>',
                    unsafe_allow_html=True)


# ── Panel 6: Quality ────────────────────────────────────────────────────────────
with col6:
    resp = df[df["event"] == "response_sent"].copy()
    if "quality_score" in resp.columns and not resp.empty:
        mean_q = resp["quality_score"].mean()
        badge = _badge(mean_q, SLO["quality_mean"], "gte")
        color_q = _slo_color(mean_q, SLO["quality_mean"], "gte")

        st.markdown(f"""
        <div class="card">
          <p class="card-title">⭐ Quality proxy &nbsp; {badge}</p>
          <div style="display:flex;gap:24px;margin-bottom:0.7rem">
            <div><div class="kpi-val" style="color:{color_q}">{mean_q:.3f}</div>
                 <div class="kpi-sub">mean score · SLO ≥ {SLO['quality_mean']}</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if "ts" in resp.columns:
            by_min = resp.set_index("ts")[["quality_score"]].resample("1min").mean().reset_index()
            fig = go.Figure(go.Scatter(
                x=by_min["ts"], y=by_min["quality_score"],
                mode="lines+markers", fill="tozeroy",
                line=dict(color=COLORS["ok"], width=2),
                fillcolor="rgba(34,197,94,0.08)",
                marker=dict(size=4),
            ))
            fig.add_hline(y=SLO["quality_mean"], line_dash="dot",
                          line_color=COLORS["warn"], line_width=1.5,
                          annotation_text=f"SLO ≥{SLO['quality_mean']}",
                          annotation_font_size=10)
            layout = _chart_layout(160)
            layout["yaxis"] = dict(range=[0, 1], title="score",
                                   showgrid=True, gridcolor=COLORS["border"],
                                   zeroline=False, tickfont=dict(size=10))
            fig.update_layout(**layout)
            _chart(fig)
    else:
        st.markdown('<div class="card"><p class="card-title">⭐ Quality</p>'
                    '<p style="color:#94a3b8">Chưa có dữ liệu</p></div>',
                    unsafe_allow_html=True)


# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<hr style="margin-top:1.5rem"/>
<div style="display:flex;justify-content:space-between;align-items:center;
            font-size:0.75rem;color:{COLORS['subtext']};padding:0.2rem 0 0.5rem">
  <span>📄 {len(df):,} log records · ⏱ {TIME_RANGE_MINUTES}-min window</span>
  <span>🔄 Auto-refresh every {REFRESH_SECONDS}s · Day 13 K3 Observability</span>
</div>
""", unsafe_allow_html=True)
