import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="S04 Transfers", layout="wide", initial_sidebar_state="collapsed")

# Aggressives mobiles CSS
st.markdown("""
    <style>
    .stApp { padding-top: 10px; }
    [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    div[data-testid="stExpander"] { border: none !important; }
    /* Filter-Boxen kompakter */
    .stSelectbox { margin-bottom: -10px; }
    </style>
""", unsafe_allow_html=True)

SHEET_ID = "1IYO8gTk5TYeqykFRGuBFX3l5-JledI0-CP_KLvotOYQ"

@st.cache_data(ttl=60)
def load_data(sheet_id):
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    # Header=2 lassen wir, aber dropna=False damit keine Zeilen verschwinden
    df = pd.read_csv(csv_url, header=2)
    # KEIN dropna() mehr, wir füllen Lücken manuell
    df = df.fillna("") 
    
    # Sicherstellen, dass die Spalten korrekt benannt sind
    cols = ["Saison", "Manager", "Spieler", "Position", "Alter", "Ablöse", "Nationalität", "Kontinent", "Abgebender_Verein", "Liga", "Region", "Transferart"]
    df.columns = cols + list(df.columns[len(cols):])
    
    # Ablöse-Fix
    df["Ablöse_num"] = df["Ablöse"].astype(str).str.replace(r'[^\d]', '', regex=True)
    df["Ablöse_num"] = pd.to_numeric(df["Ablöse_num"], errors="coerce").fillna(0)
    df["Alter_num"] = pd.to_numeric(df["Alter"], errors="coerce").fillna(0)
    return df

df = load_data(SHEET_ID)

# --- MOBILES LAYOUT ---
st.title("⚽ S04 Trans-Dashboard")

# 1. KPIs ganz oben (Das sieht sofort nach App aus)
col1, col2 = st.columns(2)
col1.metric("Transfers", len(df))
col2.metric("Gesamt", f"{int(df['Ablöse_num'].sum()/1000000)} Mio €")

# 2. Filter in einem "Mobile-Toggle"
with st.expander("⚙️ Filter & Suche"):
    manager = st.selectbox("Manager", ["Alle"] + sorted(df["Manager"].unique().tolist()))
    pos = st.selectbox("Position", ["Alle"] + sorted(df["Position"].unique().tolist()))
    if manager != "Alle": df = df[df["Manager"] == manager]
    if pos != "Alle": df = df[df["Position"] == pos]

# 3. Liste als einfache, saubere Tabelle
st.subheader("Transfer-Historie")
st.dataframe(df[["Saison", "Spieler", "Ablöse"]], use_container_width=True, hide_index=True)

# 4. Nur eine Grafik, die wirklich Sinn macht
st.subheader("Ausgaben pro Saison")
fig = px.bar(df.groupby("Saison")["Ablöse_num"].sum().reset_index(), x="Saison", y="Ablöse_num")
fig.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=300)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
