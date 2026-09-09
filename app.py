import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

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
# MAPPING NAAR JOUW KOLOMNAMEN
# -----------------------------
element_map = {
    "Temperatuur": "T",
    "Relatieve vochtigheid": "RH",
    "Visibility": "VV",
    "Windrichting": "DD",
    "Windsnelheid": "FF",
    "Druk": "PPP"
}

# -----------------------------
# KLEUREN (HIGH CONTRAST)
# -----------------------------
COLOR_MAP = {
    "Temperatuur": "#FF5733",            # fel oranje-rood
    "Relatieve vochtigheid": "#33C1FF",  # fel blauw
    "Visibility": "#9DFF33",             # fel groen
    "Windrichting": "#c7ceea",           # windroos pastel
    "Windsnelheid": "#FF33F6",           # fel roze
    "Druk": "#F3FF33"                    # fel geel
}

# -----------------------------
# WINDROOS
# -----------------------------
def make_wind_rose(df):
    directions = df["DD"]
    speeds = df["FF"]

    bins = np.arange(0, 361, 30)
    df["sector"] = pd.cut(directions, bins=bins, include_lowest=True)

    rose = df.groupby("sector")["FF"].mean().reset_index()
    labels = [f"{bins[i]}–{bins[i+1]}" for i in range(len(bins)-1)]

    fig = go.Figure()

    fig.add_trace(go.Barpolar(
        r=rose["FF"],
        theta=labels,
        marker_color="#c7ceea",
        marker_line_color="#c7ceea",
        marker_line_width=2,
        opacity=0.85
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(showticklabels=True, ticks="outside", color="white"),
            angularaxis=dict(direction="clockwise", color="white")
        ),
        showlegend=False,
        height=600,
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(color="white"),
        title="Windroos"
    )

    return fig

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="All Element Data – Zorg & Hoop", layout="wide")

st.title("🌑 All Element Data – Zorg & Hoop (Dark Mode)")
st.write("Analyse van uurdata per dag en per maand, inclusief windroos voor windrichting.")

# ELEMENT KIEZEN
elements = [
    "Temperatuur",
    "Relatieve vochtigheid",
    "Visibility",
    "Windrichting",
    "Windsnelheid",
    "Druk"
]
element_name = st.selectbox("Kies een element:", elements)
colname = element_map[element_name]
color = COLOR_MAP[element_name]

# TIJDSRESOLUTIE
resolution = st.selectbox("Kies tijdsresolutie:", ["Dagbasis (uren)", "Maandbasis (dagen)"])

# JAARSELECTIE
years = sorted(df["Year"].dropna().unique())
year = st.selectbox("Kies een jaar:", years)

df_year = df[df["Year"] == year]

# -----------------------------
# DAGBASIS
# -----------------------------
if resolution == "Dagbasis (uren)":
    months = sorted(df_year["Month"].dropna().unique())
    month = st.selectbox("Kies een maand:", months)

    df_month = df_year[df_year["Month"] == month]

    days = sorted(df_month["Day"].dropna().unique())
    day = st.selectbox("Kies een dag:", days)

    df_day = df_month[df_month["Day"] == day].copy()
    df_day = df_day.sort_values("TIJD")

    # WINDROOS
    if element_name == "Windrichting":
        st.subheader(f"Windroos – {year}-{month}-{day}")
        fig = make_wind_rose(df_day)
        st.plotly_chart(fig, use_container_width=True)

    else:
        # LIJNDIAGRAM (DAGBASIS)
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_day["TIJD"],
            y=df_day[colname],
            mode="lines+markers",
            line=dict(color=color, width=3),
            marker=dict(size=6, color=color)
        ))

        fig.update_layout(
            height=500,
            plot_bgcolor="#000000",
            paper_bgcolor="#000000",
            font=dict(color="white"),
            xaxis=dict(title="Uur (0–23)", color="white"),
            yaxis=dict(title=element_name, color="white")
        )

        st.subheader(f"{element_name} – Dagbasis (uren)")
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# MAANDBASIS
# -----------------------------
elif resolution == "Maandbasis (dagen)":
    months = sorted(df_year["Month"].dropna().unique())
    month = st.selectbox("Kies een maand:", months)

    df_month = df_year[df_year["Month"] == month].copy()

    # WINDROOS
    if element_name == "Windrichting":
        st.subheader(f"Windroos – {year}-{month}")
        fig = make_wind_rose(df_month)
        st.plotly_chart(fig, use_container_width=True)

    else:
        stat_choice = st.radio(
            "Kies statistiek:",
            ["Gemiddelde", "Maximum", "Minimum"],
            horizontal=True
        )

        if stat_choice == "Gemiddelde":
            daily = df_month.groupby("Day")[colname].mean().reset_index()
        elif stat_choice == "Maximum":
            daily = df_month.groupby("Day")[colname].max().reset_index()
        elif stat_choice == "Minimum":
            daily = df_month.groupby("Day")[colname].min().reset_index()

        daily = daily.sort_values("Day")

        # STAADIAGRAM (MAANDBASIS)
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=daily["Day"],
            y=daily[colname],
            marker=dict(color=color)
        ))

        fig.update_layout(
            height=500,
            plot_bgcolor="#000000",
            paper_bgcolor="#000000",
            font=dict(color="white"),
            xaxis=dict(title="Dag van de maand", color="white"),
            yaxis=dict(title=f"{stat_choice} {element_name}", color="white")
        )

        st.subheader(f"{element_name} – Maandbasis ({stat_choice})")
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.write("Gemaakt voor Zorg & Hoop – All Element Data Dashboard (Dark Mode)")
