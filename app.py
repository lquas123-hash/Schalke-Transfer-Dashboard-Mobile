import streamlit as st
import pandas as pd
import plotly.express as px

# Minimalistisches Setup
st.set_page_config(page_title="S04 App", layout="centered")

# App-CSS: Entfernt Desktop-Überbleibsel
st.markdown("""
    <style>
    .block-container { padding: 1rem !important; }
    h1 { font-size: 1.5rem !important; margin-bottom: 0.5rem !important; }
    .stMetric { background: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# Daten laden (dein stabiler Loader)
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/1IYO8gTk5TYeqykFRGuBFX3l5-JledI0-CP_KLvotOYQ/export?format=csv", header=2).fillna("")
    # Spalten umbenennen (dein Standard)
    cols = ["Saison", "Manager", "Spieler", "Position", "Alter", "Ablöse", "Nationalität", "Kontinent", "Abgebender_Verein", "Liga", "Region", "Transferart"]
    df.columns = cols + list(df.columns[len(cols):])
    # Numerische Werte
    df["Ablöse_num"] = pd.to_numeric(df["Ablöse"].astype(str).str.replace(r'[^\d]', '', regex=True), errors="coerce").fillna(0)
    return df

df = load_data()

# 1. APP-HEADER
st.title("⚽ S04 Transfers")

# 2. SCHNELLE FILTER-LEISTE (Wie in einer App)
col1, col2 = st.columns(2)
manager = col1.selectbox("Manager", ["Alle"] + sorted(df["Manager"].unique().tolist()))
saison = col2.selectbox("Saison", ["Alle"] + sorted(df["Saison"].unique().tolist(), reverse=True))

if manager != "Alle": df = df[df["Manager"] == manager]
if saison != "Alle": df = df[df["Saison"] == saison]

# 3. STATS-DASHBOARD (Kompakt als "Cards")
c1, c2 = st.columns(2)
c1.metric("Transfers", len(df))
c2.metric("Budget", f"{int(df['Ablöse_num'].sum()/1000000)} Mio")

# 4. TABELLE (Nur das Nötigste für den schnellen Überblick)
st.subheader("Aktuelle Auswahl")
st.dataframe(df[["Spieler", "Ablöse"]], use_container_width=True, hide_index=True)

# 5. EINE EINZIGE FOKUS-GRAFIK (Kein Custom-Chart-Gedöns, das auf Mobile nervt)
st.subheader("Ausgaben-Verlauf")
fig = px.bar(df.groupby("Saison")["Ablöse_num"].sum().reset_index(), x="Saison", y="Ablöse_num")
fig.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig, use_container_width=True)
