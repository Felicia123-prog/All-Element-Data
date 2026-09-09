import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import io

# -----------------------------
# DATA LADEN
# -----------------------------
DATA_PATH = "data/Merged_ZorgEnHoop.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(DATA_PATH)
    df["DAG"] = pd.to_datetime(df["DAG"], dayfirst=True, errors="coerce")
    df["Year"] = df["DAG"].dt.year
    df["Month"] = df["DAG"].dt.month
    df["Day"] = df["DAG"].dt.day
    return df

df = load_data()

# -----------------------------
# VECTOR GEMIDDELDE WINDRICHTING
# -----------------------------
def vector_mean(series):
    series = pd.to_numeric(series, errors="coerce").dropna()
    if len(series) == 0:
        return np.nan
    rad = np.deg2rad(series)
    u = -np.sin(rad)
    v = -np.cos(rad)
    angle = (np.rad2deg(np.arctan2(u.mean(), v.mean())) + 360) % 360
    return angle

# -----------------------------
# EXPORT FUNCTIES
# -----------------------------
def export_png(fig):
    buf = io.BytesIO()
    fig.write_image(buf, format="png")
    return buf.getvalue()

def export_svg(fig):
    buf = io.BytesIO()
    fig.write_image(buf, format="svg")
    return buf.getvalue()

def export_pdf(fig):
    buf = io.BytesIO()
    fig.write_image(buf, format="pdf")
    return buf.getvalue()

def export_csv(df):
    return df.to_csv(index=False).encode("utf-8")

def export_excel(df):
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    return buf.getvalue()

def export_panel(fig, df_export, filename_prefix="export"):
    st.subheader("📥 Export panel")
    col1, col2, col3 = st.columns(3)
    col4, col5 = st.columns(2)

    col1.download_button(
        "📸 PNG",
        data=export_png(fig),
        file_name=f"{filename_prefix}.png",
        mime="image/png"
    )
    col2.download_button(
        "🖼️ SVG",
        data=export_svg(fig),
        file_name=f"{filename_prefix}.svg",
        mime="image/svg+xml"
    )
    col3.download_button(
        "📄 PDF",
        data=export_pdf(fig),
        file_name=f"{filename_prefix}.pdf",
        mime="application/pdf"
    )
    col4.download_button(
        "📊 CSV (data)",
        data=export_csv(df_export),
        file_name=f"{filename_prefix}.csv",
        mime="text/csv"
    )
    col5.download_button(
        "📈 Excel (data)",
        data=export_excel(df_export),
        file_name=f"{filename_prefix}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -----------------------------
# PASTEL GLOW KLEUREN
# -----------------------------
PASTEL_COLORS = {
    "Temperatuur": "#ff9aa2",            # pastel roze
    "Relatieve vochtigheid": "#a2d5f2",  # pastel blauw
    "Visibilty": "#b5ead7",              # pastel groen
    "Windrichting": "#c7ceea",           # pastel paars
    "Windsnelheid": "#fff3b0",           # pastel geel
    "Druk": "#9bf6ff"                    # pastel mint
}

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="All Element Data – Zorg & Hoop", layout="wide")

st.markdown(
    """
    <style>
    body {
        background-color: #fdfbff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌈 All Element Data – Zorg & Hoop (Pastel Glow Dashboard)")
st.write("Analyse van uurdata per dag en per maand, met exportopties en vector-gemiddelde voor windrichting.")

# ELEMENT KIEZEN
elements = [
    "Temperatuur",
    "Relatieve vochtigheid",
    "Visibilty",
    "Windrichting",
    "Windsnelheid",
    "Druk"
]
element_name = st.selectbox("Kies een element:", elements)

# TIJDSRESOLUTIE
resolution = st.selectbox("Kies tijdsresolutie:", ["Dagbasis (uren)", "Maandbasis (dagen)"])

# JAARSELECTIE
years = sorted(df["Year"].dropna().unique())
year = st.selectbox("Kies een jaar:", years)

df_year = df[df["Year"] == year]

# -----------------------------
# DAGBASIS (uren 0–23)
# -----------------------------
if resolution == "Dagbasis (uren)":
    st.subheader(f"{element_name} – Dagbasis (uren) – {year}")

    months = sorted(df_year["Month"].dropna().unique())
    month = st.selectbox("Kies een maand:", months)

    df_month = df_year[df_year["Month"] == month]

    days = sorted(df_month["Day"].dropna().unique())
    day = st.selectbox("Kies een dag:", days)

    df_day = df_month[df_month["Day"] == day].copy()
    df_day = df_day.sort_values("TIJD")

    color = PASTEL_COLORS.get(element_name, "#a2d5f2")

    fig = go.Figure()

    # Glow layer
    fig.add_trace(go.Scatter(
        x=df_day["TIJD"],
        y=df_day[element_name],
        mode="lines",
        line=dict(color=color, width=10),
        opacity=0.15,
        showlegend=False
    ))

    # Main pastel line
    fig.add_trace(go.Scatter(
        x=df_day["TIJD"],
        y=df_day[element_name],
        mode="lines+markers",
        line=dict(color=color, width=3),
        marker=dict(size=6, color=color),
        name=element_name
    ))

    fig.update_layout(
        xaxis_title="Uur (0–23)",
        yaxis_title=element_name,
        height=500,
        plot_bgcolor="#fdfbff",
        paper_bgcolor="#fdfbff"
    )

    st.plotly_chart(fig, use_container_width=True)

    export_panel(
        fig,
        df_day[["DAG", "TIJD", element_name]],
        filename_prefix=f"{element_name}_{year}_{month}_{day}_dagbasis"
    )

# -----------------------------
# MAANDBASIS (dagen 1–31)
# -----------------------------
elif resolution == "Maandbasis (dagen)":
    st.subheader(f"{element_name} – Maandbasis (dagen) – {year}")

    months = sorted(df_year["Month"].dropna().unique())
    month = st.selectbox("Kies een maand:", months)

    df_month = df_year[df_year["Month"] == month].copy()

    stat_choice = st.radio(
        "Kies statistiek:",
        ["Gemiddelde", "Maximum", "Minimum"],
        horizontal=True
    )

    if element_name == "Windrichting":
        daily = df_month.groupby("Day")[element_name].apply(vector_mean).reset_index()
    else:
        if stat_choice == "Gemiddelde":
            daily = df_month.groupby("Day")[element_name].mean().reset_index()
        elif stat_choice == "Maximum":
            daily = df_month.groupby("Day")[element_name].max().reset_index()
        elif stat_choice == "Minimum":
            daily = df_month.groupby("Day")[element_name].min().reset_index()

    daily = daily.sort_values("Day")

    color = PASTEL_COLORS.get(element_name, "#a2d5f2")

    fig = go.Figure()

    # Glow layer
    fig.add_trace(go.Scatter(
        x=daily["Day"],
        y=daily[element_name],
        mode="lines",
        line=dict(color=color, width=10),
        opacity=0.15,
        showlegend=False
    ))

    # Main pastel line
    fig.add_trace(go.Scatter(
        x=daily["Day"],
        y=daily[element_name],
        mode="lines+markers",
        line=dict(color=color, width=3),
        marker=dict(size=6, color=color),
        name=f"{stat_choice} {element_name}"
    ))

    fig.update_layout(
        xaxis_title="Dag van de maand",
        yaxis_title=f"{stat_choice} {element_name}",
        height=500,
        plot_bgcolor="#fdfbff",
        paper_bgcolor="#fdfbff"
    )

    st.plotly_chart(fig, use_container_width=True)

    export_panel(
        fig,
        daily[["Day", element_name]],
        filename_prefix=f"{element_name}_{year}_{month}_{stat_choice}_maandbasis"
    )

