import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Analisis Sentimen & Aspek",
    page_icon="📊",
    layout="wide",
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}

/* Background */
.stApp {
    background: #f0f4ff;
    color: #1e2240;
}

/* Header banner */
.dashboard-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    border-radius: 20px;
    padding: 36px 44px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(102,126,234,0.35);
}
.dashboard-header::before {
    content: '';
    position: absolute;
    top: -50px; right: -50px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(255,255,255,0.18) 0%, transparent 70%);
    border-radius: 50%;
}
.dashboard-header::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 25%;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(255,255,255,0.10) 0%, transparent 70%);
    border-radius: 50%;
}
.header-title {
    font-size: 30px;
    font-weight: 900;
    color: #ffffff;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.header-sub {
    font-size: 14px;
    color: rgba(255,255,255,0.80);
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
}

/* Metric cards */
.metric-card {
    background: #ffffff;
    border: 1.5px solid #e8eeff;
    border-radius: 16px;
    padding: 22px 26px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 2px 12px rgba(102,126,234,0.08);
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 28px rgba(102,126,234,0.18);
}
.metric-label {
    font-size: 11px;
    color: #9198c0;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 34px;
    font-weight: 900;
    color: #1e2240;
    line-height: 1;
    margin-bottom: 4px;
}
.metric-pct {
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    color: #9198c0;
}
.metric-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
}

/* Section headers */
.section-title {
    font-size: 16px;
    font-weight: 800;
    color: #1e2240;
    margin: 0 0 16px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title span.accent {
    color: #667eea;
}

/* Chart containers */
.chart-container {
    background: #ffffff;
    border: 1.5px solid #e8eeff;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(102,126,234,0.07);
}

/* Table styling */
.dataframe {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}

/* Streamlit overrides */
section[data-testid="stFileUploader"] {
    background: #ffffff;
    border: 2px dashed #c5d0f5;
    border-radius: 14px;
    padding: 20px;
}
div[data-testid="stSelectbox"] > div,
div[data-testid="stMultiSelect"] > div {
    background: #ffffff;
    border-color: #e8eeff;
    border-radius: 10px;
}
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 5px;
    gap: 4px;
    box-shadow: 0 2px 10px rgba(102,126,234,0.10);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #9198c0;
    border-radius: 9px;
    font-weight: 700;
    font-size: 13px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
}
hr {
    border-color: #e8eeff !important;
}
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1.5px solid #e8eeff;
}
</style>
""", unsafe_allow_html=True)

# ─── COLOR PALETTE ──────────────────────────────────────────────────────────────
COLOR_SENTIMEN = {
    "positif": "#10b981",
    "negatif": "#f43f5e",
    "netral":  "#f59e0b",
}
COLOR_ASPEK = {
    "fungsionalitas":           "#667eea",
    "transaksi & pembayaran":   "#f093fb",
    "customer service":         "#06b6d4",
}
PLOTLY_TEMPLATE = "plotly_white"
CHART_BG = "#ffffff"
PAPER_BG = "#ffffff"

def fig_style(fig):
    fig.update_layout(
        plot_bgcolor=CHART_BG,
        paper_bgcolor=PAPER_BG,
        font_family="Nunito",
        font_color="#1e2240",
        margin=dict(l=16, r=16, t=40, b=16),
        legend=dict(
            bgcolor="#f8f9ff",
            bordercolor="#e8eeff",
            borderwidth=1,
            font=dict(size=12),
        ),
        xaxis=dict(gridcolor="#eef0fa", zerolinecolor="#eef0fa"),
        yaxis=dict(gridcolor="#eef0fa", zerolinecolor="#eef0fa"),
    )
    return fig

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <div class="header-title">📊 Dashboard Analisis Sentimen & Aspek</div>
    <div class="header-sub">Analisis ulasan pengguna · Aspect-Based Sentiment Analysis (ABSA)</div>
</div>
""", unsafe_allow_html=True)

# ─── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data(path):
    if path.endswith(".xlsx") or path.endswith(".xls"):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    if "at" in df.columns:
        df["at"] = pd.to_datetime(df["at"], errors="coerce")
        df["tahun_bulan"] = df["at"].dt.to_period("M").astype(str)
    if "jumlah_kata" not in df.columns and "final_text" in df.columns:
        df["jumlah_kata"] = df["final_text"].astype(str).apply(lambda x: len(x.split()))
    return df

# Coba load dari file repo dulu, kalau tidak ada baru minta upload
DATASET_PATH = "dataset-modelling.xlsx"
import os
if os.path.exists(DATASET_PATH):
    df = load_data(DATASET_PATH)
else:
    uploaded = st.file_uploader(
        "Upload dataset (CSV/XLSX)",
        type=["csv", "xlsx"],
        help="Pastikan kolom: sentimen_final, aspek_final, at, score, final_text"
    )
    if uploaded is None:
        st.info("⬆️ Upload file dataset dulu ya untuk memulai dashboard.")
        st.stop()
    # simpan sementara
    import tempfile, shutil
    suffix = ".xlsx" if uploaded.name.endswith(".xlsx") else ".csv"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(uploaded, tmp)
        tmp_path = tmp.name
    df = load_data(tmp_path)

# ─── VALIDATE ──────────────────────────────────────────────────────────────────
required = ["sentimen_final", "aspek_final"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"Kolom berikut tidak ditemukan: {missing}. Cek nama kolom CSV kamu ya.")
    st.stop()

# ─── SIDEBAR FILTER ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔧 Filter Data")
    all_sentimen = df["sentimen_final"].dropna().unique().tolist()
    all_aspek    = df["aspek_final"].dropna().unique().tolist()

    sel_sentimen = st.multiselect("Sentimen", all_sentimen, default=all_sentimen)
    sel_aspek    = st.multiselect("Aspek",    all_aspek,    default=all_aspek)

    st.markdown("---")
    st.markdown(f"<div style='color:#9198c0;font-size:12px'>Total data awal: <b style='color:#1e2240'>{len(df):,}</b></div>", unsafe_allow_html=True)

dff = df[df["sentimen_final"].isin(sel_sentimen) & df["aspek_final"].isin(sel_aspek)]

# ─── METRIC CARDS ──────────────────────────────────────────────────────────────
total = len(dff)
cnt_positif = (dff["sentimen_final"] == "positif").sum()
cnt_negatif = (dff["sentimen_final"] == "negatif").sum()
cnt_netral  = (dff["sentimen_final"] == "netral").sum()

pct = lambda n: f"{n/total*100:.1f}%" if total else "0%"

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📋 Total Review</div>
        <div class="metric-value">{total:,}</div>
        <div class="metric-pct">seluruh data terfilter</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label"><span class="metric-dot" style="background:#22c55e"></span>Sentimen Positif</div>
        <div class="metric-value" style="color:#22c55e">{cnt_positif:,}</div>
        <div class="metric-pct">{pct(cnt_positif)} dari total</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label"><span class="metric-dot" style="background:#ef4444"></span>Sentimen Negatif</div>
        <div class="metric-value" style="color:#ef4444">{cnt_negatif:,}</div>
        <div class="metric-pct">{pct(cnt_negatif)} dari total</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label"><span class="metric-dot" style="background:#f59e0b"></span>Sentimen Netral</div>
        <div class="metric-value" style="color:#f59e0b">{cnt_netral:,}</div>
        <div class="metric-pct">{pct(cnt_netral)} dari total</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── TAB NAVIGATION ────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Distribusi & Aspek",
    "📈 Time Series",
    "⭐ Rating & Skor",
    "☁️ WordCloud & Top Words",
    "📋 Data Ulasan",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DISTRIBUSI & ASPEK
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_a, col_b = st.columns(2)

    # Bar Chart Sentimen per Aspek
    with col_a:
        st.markdown('<div class="section-title">📊 Bar Chart Analisis per Aspek</div>', unsafe_allow_html=True)
        sentimen_aspek = dff.groupby(["aspek_final", "sentimen_final"]).size().reset_index(name="jumlah")
        fig1 = px.bar(
            sentimen_aspek,
            x="aspek_final", y="jumlah", color="sentimen_final",
            barmode="group",
            color_discrete_map=COLOR_SENTIMEN,
            labels={"aspek_final": "Aspek", "jumlah": "Jumlah", "sentimen_final": "Sentimen"},
        )
        fig1 = fig_style(fig1)
        st.plotly_chart(fig1, use_container_width=True)

    # Pie Chart Distribusi Sentimen
    with col_b:
        st.markdown('<div class="section-title">🥧 Pie Chart Distribusi Sentimen</div>', unsafe_allow_html=True)
        sentimen_count = dff["sentimen_final"].value_counts().reset_index()
        sentimen_count.columns = ["sentimen", "jumlah"]
        fig2 = px.pie(
            sentimen_count, names="sentimen", values="jumlah",
            color="sentimen",
            color_discrete_map=COLOR_SENTIMEN,
            hole=0.42,
        )
        fig2 = fig_style(fig2)
        fig2.update_traces(textinfo="percent+label", textfont_size=13)
        st.plotly_chart(fig2, use_container_width=True)

    # Bar Chart Distribusi Aspek
    st.markdown('<div class="section-title">📦 Distribusi per Aspek</div>', unsafe_allow_html=True)
    aspek_count = dff["aspek_final"].value_counts().reset_index()
    aspek_count.columns = ["aspek", "jumlah"]
    fig3 = px.bar(
        aspek_count, x="aspek", y="jumlah",
        color="aspek", color_discrete_map=COLOR_ASPEK,
        labels={"aspek": "Aspek", "jumlah": "Jumlah"},
    )
    fig3 = fig_style(fig3)
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    # Heatmap Sentimen vs Aspek (persen)
    st.markdown('<div class="section-title">🔥 Heatmap Persentase Sentimen per Aspek</div>', unsafe_allow_html=True)
    crosstab = pd.crosstab(dff["aspek_final"], dff["sentimen_final"], normalize="index") * 100
    fig4 = px.imshow(
        crosstab.round(1),
        text_auto=True,
        color_continuous_scale="Viridis",
        labels=dict(x="Sentimen", y="Aspek", color="%"),
        aspect="auto",
    )
    fig4 = fig_style(fig4)
    st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TIME SERIES
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    if "tahun_bulan" not in dff.columns:
        st.warning("Kolom `at` (tanggal) tidak ditemukan. Tab ini memerlukan data waktu.")
    else:
        st.markdown('<div class="section-title">📈 Tren Sentimen per Bulan</div>', unsafe_allow_html=True)
        trend = dff.groupby(["tahun_bulan", "sentimen_final"]).size().reset_index(name="jumlah")
        fig5 = px.line(
            trend, x="tahun_bulan", y="jumlah",
            color="sentimen_final",
            color_discrete_map=COLOR_SENTIMEN,
            markers=True,
            labels={"tahun_bulan": "Bulan", "jumlah": "Jumlah Review", "sentimen_final": "Sentimen"},
        )
        fig5 = fig_style(fig5)
        fig5.update_xaxes(tickangle=45)
        st.plotly_chart(fig5, use_container_width=True)

        st.markdown('<div class="section-title">📉 Jumlah Total Review per Bulan</div>', unsafe_allow_html=True)
        total_per_bulan = dff["tahun_bulan"].value_counts().sort_index().reset_index()
        total_per_bulan.columns = ["tahun_bulan", "jumlah"]
        fig6 = px.area(
            total_per_bulan, x="tahun_bulan", y="jumlah",
            color_discrete_sequence=["#6366f1"],
            labels={"tahun_bulan": "Bulan", "jumlah": "Jumlah Review"},
        )
        fig6 = fig_style(fig6)
        fig6.update_xaxes(tickangle=45)
        st.plotly_chart(fig6, use_container_width=True)

        st.markdown('<div class="section-title">📊 Tren Aspek per Bulan</div>', unsafe_allow_html=True)
        trend_aspek = dff.groupby(["tahun_bulan", "aspek_final"]).size().reset_index(name="jumlah")
        fig7 = px.line(
            trend_aspek, x="tahun_bulan", y="jumlah",
            color="aspek_final",
            color_discrete_map=COLOR_ASPEK,
            markers=True,
            labels={"tahun_bulan": "Bulan", "jumlah": "Jumlah Review", "aspek_final": "Aspek"},
        )
        fig7 = fig_style(fig7)
        fig7.update_xaxes(tickangle=45)
        st.plotly_chart(fig7, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — RATING & SKOR
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    if "score" not in dff.columns:
        st.warning("Kolom `score` tidak ditemukan di dataset.")
    else:
        col_r1, col_r2 = st.columns(2)

        with col_r1:
            st.markdown('<div class="section-title">⭐ Distribusi Rating</div>', unsafe_allow_html=True)
            score_count = dff["score"].value_counts().sort_index().reset_index()
            score_count.columns = ["score", "jumlah"]
            fig8 = px.bar(
                score_count, x="score", y="jumlah",
                color="score",
                color_continuous_scale="RdYlGn",
                labels={"score": "Rating", "jumlah": "Jumlah"},
            )
            fig8 = fig_style(fig8)
            st.plotly_chart(fig8, use_container_width=True)

        with col_r2:
            st.markdown('<div class="section-title">💬 Sentimen per Rating</div>', unsafe_allow_html=True)
            score_sent = dff.groupby(["score", "sentimen_final"]).size().reset_index(name="jumlah")
            fig9 = px.bar(
                score_sent, x="score", y="jumlah",
                color="sentimen_final",
                barmode="stack",
                color_discrete_map=COLOR_SENTIMEN,
                labels={"score": "Rating", "jumlah": "Jumlah", "sentimen_final": "Sentimen"},
            )
            fig9 = fig_style(fig9)
            st.plotly_chart(fig9, use_container_width=True)

        st.markdown('<div class="section-title">📦 Aspek per Rating</div>', unsafe_allow_html=True)
        score_aspek = dff.groupby(["score", "aspek_final"]).size().reset_index(name="jumlah")
        fig10 = px.bar(
            score_aspek, x="score", y="jumlah",
            color="aspek_final",
            barmode="group",
            color_discrete_map=COLOR_ASPEK,
            labels={"score": "Rating", "jumlah": "Jumlah", "aspek_final": "Aspek"},
        )
        fig10 = fig_style(fig10)
        st.plotly_chart(fig10, use_container_width=True)

        if "jumlah_kata" in dff.columns:
            st.markdown('<div class="section-title">📝 Distribusi Panjang Review (Jumlah Kata)</div>', unsafe_allow_html=True)
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                fig11 = px.histogram(
                    dff, x="jumlah_kata", nbins=30,
                    color="sentimen_final",
                    color_discrete_map=COLOR_SENTIMEN,
                    labels={"jumlah_kata": "Jumlah Kata", "sentimen_final": "Sentimen"},
                    opacity=0.8,
                )
                fig11 = fig_style(fig11)
                st.plotly_chart(fig11, use_container_width=True)
            with col_h2:
                fig12 = px.box(
                    dff, x="sentimen_final", y="jumlah_kata",
                    color="sentimen_final",
                    color_discrete_map=COLOR_SENTIMEN,
                    labels={"sentimen_final": "Sentimen", "jumlah_kata": "Jumlah Kata"},
                )
                fig12 = fig_style(fig12)
                st.plotly_chart(fig12, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — WORDCLOUD & TOP WORDS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    if "final_text" not in dff.columns:
        st.warning("Kolom `final_text` tidak ditemukan. Tab ini perlu kolom teks.")
    else:
        def make_wordcloud(text, bg="#ffffff", colormap="viridis"):
            wc = WordCloud(
                width=800, height=400,
                background_color=bg,
                colormap=colormap,
                collocations=False,
                max_words=100,
            ).generate(text)
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor(bg)
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            return fig

        def top_words_chart(text, n=15, title=""):
            words = text.split()
            freq = Counter(words).most_common(n)
            temp = pd.DataFrame(freq, columns=["kata", "frekuensi"])
            fig = px.bar(
                temp, x="frekuensi", y="kata",
                orientation="h",
                color="frekuensi",
                color_continuous_scale="Viridis",
                title=title,
                labels={"kata": "Kata", "frekuensi": "Frekuensi"},
            )
            fig = fig_style(fig)
            fig.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
            return fig

        wc_scope = st.radio("Pilih scope WordCloud:", ["Keseluruhan", "per Sentimen", "per Aspek"], horizontal=True)
        st.markdown("---")

        if wc_scope == "Keseluruhan":
            all_text = " ".join(dff["final_text"].dropna().astype(str))
            if all_text.strip():
                col_w1, col_w2 = st.columns([1.5, 1])
                with col_w1:
                    st.markdown('<div class="section-title">☁️ WordCloud Keseluruhan</div>', unsafe_allow_html=True)
                    st.pyplot(make_wordcloud(all_text))
                with col_w2:
                    st.markdown('<div class="section-title">🏆 Top 15 Kata</div>', unsafe_allow_html=True)
                    st.plotly_chart(top_words_chart(all_text, title=""), use_container_width=True)

        elif wc_scope == "per Sentimen":
            for sent in dff["sentimen_final"].unique():
                text = " ".join(dff[dff["sentimen_final"] == sent]["final_text"].dropna().astype(str))
                if not text.strip():
                    continue
                st.markdown(f'<div class="section-title">☁️ Sentimen: <span class="accent">{sent}</span></div>', unsafe_allow_html=True)
                col_w1, col_w2 = st.columns([1.5, 1])
                cmap = {"positif": "Greens", "negatif": "Reds", "netral": "YlOrBr"}.get(sent, "plasma")
                with col_w1:
                    st.pyplot(make_wordcloud(text, colormap=cmap))
                with col_w2:
                    st.plotly_chart(top_words_chart(text, title=f"Top Words · {sent}"), use_container_width=True)
                st.markdown("---")

        else:
            for aspek in dff["aspek_final"].unique():
                text = " ".join(dff[dff["aspek_final"] == aspek]["final_text"].dropna().astype(str))
                if not text.strip():
                    continue
                st.markdown(f'<div class="section-title">☁️ Aspek: <span class="accent">{aspek}</span></div>', unsafe_allow_html=True)
                col_w1, col_w2 = st.columns([1.5, 1])
                with col_w1:
                    st.pyplot(make_wordcloud(text, colormap="cool"))
                with col_w2:
                    st.plotly_chart(top_words_chart(text, title=f"Top Words · {aspek}"), use_container_width=True)
                st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — DATA ULASAN
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">📋 List Ulasan Pengguna</div>', unsafe_allow_html=True)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_sent = st.selectbox("Filter Sentimen", ["Semua"] + dff["sentimen_final"].unique().tolist())
    with col_f2:
        filter_aspek = st.selectbox("Filter Aspek", ["Semua"] + dff["aspek_final"].unique().tolist())

    view = dff.copy()
    if filter_sent != "Semua":
        view = view[view["sentimen_final"] == filter_sent]
    if filter_aspek != "Semua":
        view = view[view["aspek_final"] == filter_aspek]

    # Kolom yang ditampilkan
    show_cols = [c for c in ["at", "score", "final_text", "sentimen_final", "aspek_final", "jumlah_kata"] if c in view.columns]
    rename_map = {
        "at": "Tanggal", "score": "Rating", "final_text": "Ulasan",
        "sentimen_final": "Sentimen", "aspek_final": "Aspek", "jumlah_kata": "Jml Kata"
    }

    st.markdown(f"<div style='color:#9198c0;font-size:13px;margin-bottom:12px'>Menampilkan <b style='color:#1e2240'>{len(view):,}</b> ulasan</div>", unsafe_allow_html=True)
    st.dataframe(
        view[show_cols].rename(columns=rename_map).reset_index(drop=True),
        use_container_width=True,
        height=500,
    )

    # Download
    csv_export = view[show_cols].rename(columns=rename_map).to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download data ini (CSV)", csv_export, "filtered_reviews.csv", "text/csv")
