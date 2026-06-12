
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Retail Forecast AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# CUSTOM CSS - PREMIUM CLEAN UI
# ==========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(99, 102, 241, 0.16), transparent 32%),
            radial-gradient(circle at top right, rgba(14, 165, 233, 0.14), transparent 30%),
            linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
        color: #0f172a;
    }

    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.78);
        backdrop-filter: blur(18px);
        border-right: 1px solid rgba(226, 232, 240, 0.9);
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #0f172a;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    .hero-card {
        padding: 28px 30px;
        border-radius: 28px;
        background:
            linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.94)),
            radial-gradient(circle at 85% 20%, rgba(59, 130, 246, 0.35), transparent 35%);
        color: white;
        box-shadow: 0 26px 70px rgba(15, 23, 42, 0.25);
        border: 1px solid rgba(255,255,255,0.12);
        margin-bottom: 22px;
    }

    .hero-title {
        font-size: 38px;
        line-height: 1.12;
        font-weight: 800;
        margin-bottom: 8px;
        letter-spacing: -0.045em;
    }

    .hero-subtitle {
        font-size: 15.5px;
        color: rgba(226, 232, 240, 0.92);
        max-width: 980px;
        line-height: 1.7;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.16);
        color: rgba(255,255,255,0.95);
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 14px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.035em;
        color: #0f172a;
        margin-top: 8px;
        margin-bottom: 4px;
    }

    .section-desc {
        color: #64748b;
        font-size: 14.5px;
        margin-bottom: 16px;
        line-height: 1.6;
    }

    .metric-card {
        padding: 20px 20px;
        border-radius: 24px;
        background: rgba(255, 255, 255, 0.86);
        border: 1px solid rgba(226, 232, 240, 0.95);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
        min-height: 116px;
    }

    .metric-label {
        color: #64748b;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.015em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .metric-value {
        color: #0f172a;
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -0.05em;
        line-height: 1.05;
    }

    .metric-note {
        margin-top: 8px;
        color: #94a3b8;
        font-size: 12.5px;
    }

    .insight-card {
        padding: 18px 20px;
        border-radius: 22px;
        background: rgba(255,255,255,0.82);
        border: 1px solid rgba(226, 232, 240, 0.9);
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.07);
        margin: 10px 0 16px 0;
    }

    .insight-title {
        font-weight: 800;
        font-size: 16px;
        color: #0f172a;
        margin-bottom: 6px;
    }

    .insight-text {
        font-size: 14px;
        color: #475569;
        line-height: 1.65;
    }

    .pill {
        display: inline-flex;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        border: 1px solid transparent;
        margin-right: 6px;
    }

    .pill-high {
        background: #ecfdf5;
        color: #047857;
        border-color: #bbf7d0;
    }

    .pill-mid {
        background: #eff6ff;
        color: #1d4ed8;
        border-color: #bfdbfe;
    }

    .pill-low {
        background: #fff7ed;
        color: #c2410c;
        border-color: #fed7aa;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.84);
        border: 1px solid rgba(226, 232, 240, 0.9);
        padding: 18px;
        border-radius: 22px;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.06);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b;
        font-weight: 700;
    }

    div[data-testid="stMetricValue"] {
        color: #0f172a;
        font-weight: 800;
        letter-spacing: -0.05em;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255,255,255,0.64);
        padding: 10px;
        border-radius: 22px;
        border: 1px solid rgba(226, 232, 240, 0.88);
        box-shadow: 0 14px 36px rgba(15, 23, 42, 0.06);
    }

    .stTabs [data-baseweb="tab"] {
        height: 46px;
        border-radius: 16px;
        padding-left: 18px;
        padding-right: 18px;
        color: #64748b;
        font-weight: 700;
    }

    .stTabs [aria-selected="true"] {
        background: #0f172a !important;
        color: white !important;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 22px;
        overflow: hidden;
        border: 1px solid rgba(226, 232, 240, 0.9);
        box-shadow: 0 16px 42px rgba(15, 23, 42, 0.06);
    }

    div[data-testid="stExpander"] {
        border-radius: 20px;
        border: 1px solid rgba(226, 232, 240, 0.9);
        background: rgba(255,255,255,0.72);
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 16px;
        border: 1px solid rgba(15, 23, 42, 0.10);
        background: #0f172a;
        color: white;
        font-weight: 750;
        padding: 0.68rem 1rem;
        box-shadow: 0 14px 30px rgba(15, 23, 42, 0.16);
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #1e293b;
        color: white;
        border: 1px solid rgba(15, 23, 42, 0.18);
    }

    .small-caption {
        font-size: 12.5px;
        color: #94a3b8;
        margin-top: -4px;
    }

    .footer-card {
        padding: 16px 18px;
        border-radius: 22px;
        background: rgba(15, 23, 42, 0.96);
        color: rgba(255,255,255,0.86);
        font-size: 13px;
        margin-top: 26px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# PLOTLY TEMPLATE
# ==========================================================

px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = ["#2563eb", "#14b8a6", "#f97316", "#8b5cf6", "#ef4444", "#22c55e"]


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def load_csv(output_dir, filename, required=True):
    path = Path(output_dir) / filename
    if not path.exists():
        if required:
            st.error(f"File belum ditemukan: {path}")
            st.info("Jalankan dulu kode tambahan multi-product forecasting di Colab sampai selesai.")
            st.stop()
        return None
    return pd.read_csv(path)


def fmt(x):
    try:
        return f"{float(x):,.0f}"
    except Exception:
        return x


def styled_plot(fig, height=430):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Inter, Arial", color="#0f172a"),
        title=dict(font=dict(size=18, color="#0f172a"), x=0.02),
        margin=dict(l=20, r=20, t=58, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Inter"
        )
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(226,232,240,0.75)",
        zeroline=False
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(226,232,240,0.75)",
        zeroline=False
    )
    return fig


def render_metric_card(label, value, note="", icon=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{icon} {label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# HERO
# ==========================================================

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-badge">✨ Retail Forecast AI Dashboard</div>
        <div class="hero-title">Prediksi Produk Laris & Rekomendasi Stok</div>
        <div class="hero-subtitle">
            Dashboard interaktif untuk melihat produk yang diprediksi paling laris dalam beberapa minggu ke depan,
            menghitung estimasi permintaan, safety stock, dan rekomendasi stok berdasarkan hasil model dari Google Colab.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.markdown("## ⚙️ Kontrol Dashboard")
st.sidebar.caption("Atur sumber data, periode prediksi, dan tampilan produk.")

OUTPUT_DIR = st.sidebar.text_input(
    "Folder output hasil Colab",
    value="/content/drive/MyDrive/output_forecasting_retail_uk"
)

if not Path(OUTPUT_DIR).exists():
    st.error(f"Folder tidak ditemukan: {OUTPUT_DIR}")
    st.stop()


# ==========================================================
# LOAD DATA
# ==========================================================

multi_forecast = load_csv(OUTPUT_DIR, "multi_product_forecast.csv")
multi_metrics = load_csv(OUTPUT_DIR, "multi_product_model_metrics.csv", required=False)
multi_weekly = load_csv(OUTPUT_DIR, "multi_product_weekly_sales.csv", required=False)
monthly_sales = load_csv(OUTPUT_DIR, "dashboard_monthly_sales.csv", required=False)
top_quantity = load_csv(OUTPUT_DIR, "dashboard_top_products_quantity.csv", required=False)
top_revenue = load_csv(OUTPUT_DIR, "dashboard_top_products_revenue.csv", required=False)

multi_forecast["Forecast_Date"] = pd.to_datetime(multi_forecast["Forecast_Date"], errors="coerce")
if multi_weekly is not None and "WeekStart" in multi_weekly.columns:
    multi_weekly["WeekStart"] = pd.to_datetime(multi_weekly["WeekStart"], errors="coerce")


# ==========================================================
# FILTER CONTROL
# ==========================================================

st.sidebar.markdown("## 🔮 Prediksi")
horizon = st.sidebar.slider("Prediksi berapa minggu ke depan?", 1, 8, 2)
top_n = st.sidebar.slider("Tampilkan top produk", 5, 30, 10)

sort_by = st.sidebar.selectbox(
    "Urutkan berdasarkan",
    [
        "Prediksi quantity tertinggi",
        "Rekomendasi stok tertinggi",
        "Revenue historis tertinggi",
        "Produk paling sering transaksi"
    ]
)

keyword = st.sidebar.text_input("Cari nama/kode produk", "")

st.sidebar.markdown("---")
st.sidebar.markdown("### Status Data")
st.sidebar.success("Data Colab berhasil dibaca")


# ==========================================================
# SUMMARY CUSTOM
# ==========================================================

filtered = multi_forecast[multi_forecast["Forecast_Week_Number"] <= horizon].copy()

summary = filtered.groupby(["StockCode", "Description"]).agg(
    Predicted_Quantity=("Predicted_Quantity", "sum"),
    Safety_Stock=("Safety_Stock", "max"),
    Best_Model=("Best_Model", "first"),
    Model_MAE=("Model_MAE", "first"),
    Historical_Total_Quantity=("Historical_Total_Quantity", "first"),
    Historical_Total_Revenue=("Historical_Total_Revenue", "first"),
    Historical_Invoice_Count=("Historical_Invoice_Count", "first"),
    Historical_Active_Weeks=("Historical_Active_Weeks", "first")
).reset_index()

summary["Recommended_Stock"] = np.ceil(summary["Predicted_Quantity"] + summary["Safety_Stock"]).astype(int)

if len(summary) > 0:
    q75 = summary["Predicted_Quantity"].quantile(0.75)
    q40 = summary["Predicted_Quantity"].quantile(0.40)
    summary["Potensi_Laris"] = np.where(
        summary["Predicted_Quantity"] >= q75,
        "Sangat Laris",
        np.where(summary["Predicted_Quantity"] >= q40, "Cukup Laris", "Rendah")
    )

if keyword.strip():
    k = keyword.strip().upper()
    summary = summary[
        summary["Description"].str.upper().str.contains(k, na=False) |
        summary["StockCode"].str.upper().str.contains(k, na=False)
    ]

if sort_by == "Prediksi quantity tertinggi":
    summary = summary.sort_values("Predicted_Quantity", ascending=False)
elif sort_by == "Rekomendasi stok tertinggi":
    summary = summary.sort_values("Recommended_Stock", ascending=False)
elif sort_by == "Revenue historis tertinggi":
    summary = summary.sort_values("Historical_Total_Revenue", ascending=False)
else:
    summary = summary.sort_values("Historical_Invoice_Count", ascending=False)

summary = summary.reset_index(drop=True)
summary["Rank"] = np.arange(1, len(summary) + 1)
top_summary = summary.head(top_n)


# ==========================================================
# KPI CARDS
# ==========================================================

st.markdown(f'<div class="section-title">Prediksi Produk Laris {horizon} Minggu ke Depan</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-desc">Ringkasan produk yang diprediksi memiliki permintaan tertinggi berdasarkan hasil model forecasting dari Google Colab.</div>',
    unsafe_allow_html=True
)

k1, k2, k3, k4 = st.columns(4)
with k1:
    render_metric_card("Produk Dianalisis", f"{multi_forecast['StockCode'].nunique():,}", "Produk kandidat dari hasil Colab", "📦")
with k2:
    render_metric_card("Top Produk", f"{len(top_summary):,}", "Produk yang ditampilkan", "🏆")
with k3:
    render_metric_card("Prediksi Demand", fmt(top_summary["Predicted_Quantity"].sum()), f"Akumulasi {horizon} minggu", "📈")
with k4:
    render_metric_card("Rekomendasi Stok", fmt(top_summary["Recommended_Stock"].sum()), "Demand + safety stock", "🛒")


st.markdown(
    """
    <div class="insight-card">
        <div class="insight-title">Business Insight</div>
        <div class="insight-text">
        Dashboard ini membantu menentukan produk prioritas yang perlu disiapkan stoknya.
        Produk dengan status <span class="pill pill-high">Sangat Laris</span> memiliki prediksi permintaan paling tinggi
        dibandingkan produk lain pada periode yang dipilih.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# TABS
# ==========================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔥 Produk Akan Laris",
    "📦 Rekomendasi Stok",
    "📈 Detail Produk",
    "📊 Overview BI",
    "🗣️ Narasi"
])


with tab1:
    st.markdown('<div class="section-title">Produk yang Diprediksi Paling Laris</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">Urutan produk berdasarkan prediksi permintaan pada periode yang dipilih.</div>',
        unsafe_allow_html=True
    )

    show_cols = [
        "Rank", "StockCode", "Description", "Potensi_Laris",
        "Predicted_Quantity", "Safety_Stock", "Recommended_Stock",
        "Best_Model", "Model_MAE",
        "Historical_Total_Quantity", "Historical_Total_Revenue",
        "Historical_Invoice_Count", "Historical_Active_Weeks"
    ]

    st.dataframe(top_summary[show_cols], use_container_width=True, hide_index=True)

    fig = px.bar(
        top_summary.sort_values("Predicted_Quantity"),
        x="Predicted_Quantity",
        y="Description",
        orientation="h",
        color="Potensi_Laris",
        color_discrete_map={
            "Sangat Laris": "#10b981",
            "Cukup Laris": "#2563eb",
            "Rendah": "#f97316"
        },
        title=f"Top {len(top_summary)} Produk Diprediksi Laris {horizon} Minggu ke Depan"
    )
    fig.update_traces(marker_line_width=0, opacity=0.92)
    st.plotly_chart(styled_plot(fig, 520), use_container_width=True)

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">Cara membaca hasil</div>
            <div class="insight-text">
            Kolom <b>Predicted_Quantity</b> menunjukkan perkiraan jumlah produk yang akan terjual dalam {horizon} minggu.
            Semakin tinggi nilainya, semakin besar potensi produk tersebut untuk menjadi produk prioritas.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with tab2:
    st.markdown('<div class="section-title">Rekomendasi Stok per Produk</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">Rekomendasi stok dihitung dari prediksi permintaan ditambah safety stock.</div>',
        unsafe_allow_html=True
    )

    stock_cols = ["Rank", "StockCode", "Description", "Predicted_Quantity", "Safety_Stock", "Recommended_Stock", "Potensi_Laris"]
    st.dataframe(top_summary[stock_cols], use_container_width=True, hide_index=True)

    fig = px.bar(
        top_summary.sort_values("Recommended_Stock"),
        x="Recommended_Stock",
        y="Description",
        orientation="h",
        color="Potensi_Laris",
        color_discrete_map={
            "Sangat Laris": "#10b981",
            "Cukup Laris": "#2563eb",
            "Rendah": "#f97316"
        },
        title=f"Rekomendasi Stok untuk {horizon} Minggu ke Depan"
    )
    fig.update_traces(marker_line_width=0, opacity=0.92)
    st.plotly_chart(styled_plot(fig, 520), use_container_width=True)

    st.markdown(
        """
        <div class="insight-card">
            <div class="insight-title">Rumus rekomendasi</div>
            <div class="insight-text">
            <b>Recommended Stock = Predicted Quantity + Safety Stock</b>.
            Safety stock digunakan sebagai cadangan untuk mengurangi risiko kehabisan stok jika permintaan aktual lebih tinggi dari prediksi.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with tab3:
    st.markdown('<div class="section-title">Detail Forecast per Produk</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">Pilih satu produk untuk melihat detail prediksi mingguan, rekomendasi stok, dan riwayat penjualannya.</div>',
        unsafe_allow_html=True
    )

    if summary.empty:
        st.warning("Tidak ada produk sesuai filter.")
    else:
        product_options = (summary["StockCode"] + " - " + summary["Description"]).tolist()
        selected = st.selectbox("Pilih produk", product_options)
        selected_stock = selected.split(" - ")[0]

        detail = multi_forecast[multi_forecast["StockCode"] == selected_stock].copy()
        detail_summary = summary[summary["StockCode"] == selected_stock].copy()

        d1, d2, d3 = st.columns(3)
        with d1:
            render_metric_card("Prediksi Demand", fmt(detail_summary["Predicted_Quantity"].iloc[0]), f"{horizon} minggu ke depan", "📈")
        with d2:
            render_metric_card("Recommended Stock", fmt(detail_summary["Recommended_Stock"].iloc[0]), "Termasuk safety stock", "🛒")
        with d3:
            render_metric_card("Status", str(detail_summary["Potensi_Laris"].iloc[0]), "Kelas potensi permintaan", "🔥")

        st.dataframe(detail_summary, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)

        with col1:
            fig = px.line(
                detail,
                x="Forecast_Date",
                y="Predicted_Quantity",
                markers=True,
                title="Prediksi Quantity Mingguan"
            )
            fig.update_traces(line=dict(width=4), marker=dict(size=9))
            st.plotly_chart(styled_plot(fig, 420), use_container_width=True)

        with col2:
            fig = px.bar(
                detail,
                x="Forecast_Date",
                y="Recommended_Stock_Weekly",
                title="Rekomendasi Stok Mingguan"
            )
            fig.update_traces(marker_color="#0f172a", marker_line_width=0, opacity=0.88)
            st.plotly_chart(styled_plot(fig, 420), use_container_width=True)

        if multi_weekly is not None:
            hist = multi_weekly[multi_weekly["StockCode"] == selected_stock].copy()
            if not hist.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hist["WeekStart"],
                    y=hist["quantity_sold"],
                    mode="lines+markers",
                    name="Historical",
                    line=dict(color="#2563eb", width=3),
                    marker=dict(size=7)
                ))
                fig.add_trace(go.Scatter(
                    x=detail["Forecast_Date"],
                    y=detail["Predicted_Quantity"],
                    mode="lines+markers",
                    name="Forecast",
                    line=dict(color="#10b981", width=4, dash="dash"),
                    marker=dict(size=9)
                ))
                fig.update_layout(title="Historical Sales + Forecast", xaxis_title="Minggu", yaxis_title="Quantity")
                st.plotly_chart(styled_plot(fig, 500), use_container_width=True)

        with st.expander("Lihat tabel forecast mingguan"):
            st.dataframe(detail, use_container_width=True, hide_index=True)


with tab4:
    st.markdown('<div class="section-title">Overview Business Intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">Ringkasan performa penjualan historis dari hasil export Google Colab.</div>',
        unsafe_allow_html=True
    )

    if monthly_sales is not None:
        col1, col2 = st.columns(2)
        with col1:
            if {"YearMonth", "total_revenue"}.issubset(monthly_sales.columns):
                fig = px.line(monthly_sales, x="YearMonth", y="total_revenue", markers=True, title="Tren Revenue Bulanan")
                fig.update_traces(line=dict(width=4), marker=dict(size=8))
                st.plotly_chart(styled_plot(fig, 420), use_container_width=True)
        with col2:
            if {"YearMonth", "total_quantity"}.issubset(monthly_sales.columns):
                fig = px.line(monthly_sales, x="YearMonth", y="total_quantity", markers=True, title="Tren Quantity Bulanan")
                fig.update_traces(line=dict(width=4), marker=dict(size=8))
                st.plotly_chart(styled_plot(fig, 420), use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        if top_quantity is not None:
            st.markdown("#### Top Produk Historis Berdasarkan Quantity")
            st.dataframe(top_quantity, use_container_width=True, hide_index=True)

    with col4:
        if top_revenue is not None:
            st.markdown("#### Top Produk Historis Berdasarkan Revenue")
            st.dataframe(top_revenue, use_container_width=True, hide_index=True)


with tab5:
    st.markdown('<div class="section-title">Narasi Penjelasan untuk Record</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">Script penjelasan singkat</div>
            <div class="insight-text">
            Pada dashboard ini, pengguna dapat menentukan periode prediksi secara custom, misalnya <b>{horizon} minggu ke depan</b>.
            Sistem kemudian menampilkan produk yang diprediksi memiliki permintaan tertinggi pada periode tersebut.
            <br><br>
            Kolom <b>Predicted_Quantity</b> menunjukkan perkiraan jumlah produk yang akan terjual.
            Kolom <b>Safety_Stock</b> adalah cadangan stok berdasarkan error model.
            Kolom <b>Recommended_Stock</b> adalah jumlah stok yang disarankan.
            <br><br>
            Jadi dashboard ini tidak hanya menampilkan grafik, tetapi membantu pengambilan keputusan bisnis:
            produk apa yang diprioritaskan dan berapa stok yang perlu disiapkan.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="insight-card">
            <div class="insight-title">Kesimpulan</div>
            <div class="insight-text">
            Streamlit digunakan sebagai dashboard visualisasi hasil model dari Google Colab.
            Proses preprocessing dan training model tetap dilakukan di Colab, sedangkan dashboard ini menampilkan hasilnya secara interaktif.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# DOWNLOAD
# ==========================================================

st.sidebar.markdown("---")
st.sidebar.header("⬇️ Download")

st.sidebar.download_button(
    "Download Summary Custom CSV",
    data=summary.to_csv(index=False).encode("utf-8"),
    file_name=f"custom_prediksi_produk_laris_{horizon}_minggu.csv",
    mime="text/csv"
)

st.sidebar.download_button(
    "Download Multi Forecast CSV",
    data=multi_forecast.to_csv(index=False).encode("utf-8"),
    file_name="multi_product_forecast.csv",
    mime="text/csv"
)

st.markdown(
    """
    <div class="footer-card">
        Retail Forecast AI • Dashboard prediksi produk laris dan rekomendasi stok berbasis hasil model Google Colab.
    </div>
    """,
    unsafe_allow_html=True
)
