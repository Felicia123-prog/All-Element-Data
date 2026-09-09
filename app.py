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
# KLEUREN (HIGH CONTRAST)
# -----------------------------
COLOR_MAP = {
    "Temperatuur": "#FF5733",
    "Relatieve Vochtigheid": "#33C1FF",
    "Visibility": "#9DFF33",
    "Windrichting": "#c7ceea",
    "Windsnelheid": "#FF33F6",
    "Druk": "#F3FF33"
}

# -----------------------------
# WINDROOS
# -----------------------------
def make_wind_rose(df):
    directions = df["Windrichting"]
    speeds = df["Windsnelheid"]

    bins = np.arange(0, 361, 30)
    df["sector"] = pd.cut(directions, bins=bins, include_lowest=True)

    rose = df.groupby("sector")["Windsnelheid"].mean().reset_index()
    labels = [f"{bins[i]}–{bins[i+1]}" for i in range(len(bins)-1)]

    fig = go.Figure()

    fig.add_trace(go.Barpolar(
        r=rose["Windsnelheid"],
        theta=labels,
        marker_color="#c7ceea",
        marker_line_color="#c7ceea",
        marker_line_width=2,
        opacity=0.85
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(showticklabels=True, ticks="outside", color="black"),
            angularaxis=dict(direction="clockwise", color="black")
        ),
        showlegend=False,
        height=600,
        paper_bgcolor="#e6e6e6",
        plot_bgcolor="#e6e6e6",
        font=dict(color="black", size=14),
        title="Windroos"
    )

    return fig

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="All Element Data – Zorg & Hoop", layout="wide")

st.title("All Element Data – Zorg & Hoop")
st.write("Analyse van uurdata per dag, per maand en per jaar, inclusief windroos voor windrichting.")

# ELEMENT KIEZEN
elements = [
    "Temperatuur",
    "Relatieve Vochtigheid",
    "Visibility",
    "Windrichting",
    "Windsnelheid",
    "Druk"
]
element_name = st.selectbox("Kies een element:", elements)
color = COLOR_MAP[element_name]

# TIJDSRESOLUTIE
resolution = st.selectbox(
    "Kies tijdsresolutie:",
    ["Dagbasis (uren)", "Maandbasis (dagen)", "Jaarbasis (maanden)"]
)

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
            y=df_day[element_name],
            mode="lines+markers",
            line=dict(color=color, width=3),
            marker=dict(size=6, color=color)
        ))

        fig.update_layout(
            height=500,
            plot_bgcolor="#e6e6e6",
            paper_bgcolor="#e6e6e6",
            font=dict(color="black", size=14),
            xaxis_title="Uur (0–23)",
            yaxis_title=element_name
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
            daily = df_month.groupby("Day")[element_name].mean().reset_index()
        elif stat_choice == "Maximum":
            daily = df_month.groupby("Day")[element_name].max().reset_index()
        elif stat_choice == "Minimum":
            daily = df_month.groupby("Day")[element_name].min().reset_index()

        daily = daily.sort_values("Day")

        # LIJNDIAGRAM (MAANDBASIS)
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=daily["Day"],
            y=daily[element_name],
            mode="lines+markers",
            line=dict(color=color, width=3),
            marker=dict(size=6, color=color)
        ))

        fig.update_layout(
            height=500,
            plot_bgcolor="#e6e6e6",
            paper_bgcolor="#e6e6e6",
            font=dict(color="black", size=14),
            xaxis_title="Dag van de maand",
            yaxis_title=f"{stat_choice} {element_name}"
        )

        st.subheader(f"{element_name} – Maandbasis ({stat_choice})")
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# JAARBASIS
# -----------------------------
elif resolution == "Jaarbasis (maanden)":

    stat_choice = st.radio(
        "Kies statistiek:",
        ["Gemiddelde", "Maximum", "Minimum"],
        horizontal=True
    )

    if stat_choice == "Gemiddelde":
        yearly = df_year.groupby("Month")[element_name].mean().reset_index()
    elif stat_choice == "Maximum":
        yearly = df_year.groupby("Month")[element_name].max().reset_index()
    elif stat_choice == "Minimum":
        yearly = df_year.groupby("Month")[element_name].min().reset_index()

    yearly = yearly.sort_values("Month")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=yearly["Month"],
        y=yearly[element_name],
        mode="lines+markers",
        line=dict(color=color, width=3),
        marker=dict(size=6, color=color)
    ))

    fig.update_layout(
        height=500,
        plot_bgcolor="#e6e6e6",
        paper_bgcolor="#e6e6e6",
        font=dict(color="black", size=14),
        xaxis_title="Maand (1–12)",
        yaxis_title=f"{stat_choice} {element_name}"
    )

    st.subheader(f"{element_name} – Jaarbasis ({stat_choice})")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.write("Gemaakt voor Zorg & Hoop – All Element Data Dashboard")
