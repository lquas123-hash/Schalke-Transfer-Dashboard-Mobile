import streamlit as st
import pandas as pd
import plotly.express as px

# Minimalistisches Setup im Mobile-Layout
st.set_page_config(page_title="S04 App", layout="centered")

# App-CSS angepasst für den Dark Mode
st.markdown("""
    <style>
    .block-container { padding: 1rem !important; }
    h1 { font-size: 1.5rem !important; margin-bottom: 0.5rem !important; }
    .stMetric { background: #1e2530; padding: 10px; border-radius: 10px; border: 1px solid #2d3748; }
    </style>
""", unsafe_allow_html=True)

MOBILE_PLOTLY_CONFIG = {
    'displayModeBar': False,
    'scrollZoom': False,
    'doubleClick': False
}

SHEET_ID = "1IYO8gTk5TYeqykFRGuBFX3l5-JledI0-CP_KLvotOYQ"

# Daten laden
@st.cache_data(ttl=60)
def load_data(sheet_id):
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(csv_url, header=2)
    df = df.fillna("") 

    cols = ["Saison", "Manager", "Spieler", "Position", "Alter", "Ablöse", "Nationalität", "Kontinent", "Abgebender_Verein", "Liga", "Region", "Transferart"]
    if len(df.columns) >= len(cols):
        df.columns = cols + list(df.columns[len(cols):])
    else:
        df.columns = cols[:len(df.columns)]

    df["Ablöse_num"] = (
        df["Ablöse"].astype(str)
        .str.replace("€", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.extract(r"(\d+\.?\d*)")[0]
    )
    df["Ablöse_num"] = pd.to_numeric(df["Ablöse_num"], errors="coerce").fillna(0)
    
    return df

try:
    df = load_data(SHEET_ID)

    # 1. APP-HEADER
    st.title("⚽ S04 Transfers")

    # 2. SCHNELLE FILTER-LEISTE
    col1, col2 = st.columns(2)
    manager = col1.selectbox("Manager", ["Alle"] + sorted([str(x) for x in df["Manager"].unique() if x != ""]))
    saison = col2.selectbox("Saison", ["Alle"] + sorted([str(x) for x in df["Saison"].unique() if x != ""], reverse=True))

    if manager != "Alle": 
        df = df[df["Manager"] == manager]
    if saison != "Alle": 
        df = df[df["Saison"] == saison]

    st.divider()

    # 3. STATS-DASHBOARD
    c1, c2 = st.columns(2)
    c1.metric("Transfers", len(df))
    c2.metric("Budget", f"{int(df['Ablöse_num'].sum()/1000000)} Mio €")

    st.divider()

    # 4. TABELLE (Gewünschte Spaltenreihenfolge: Saison, Manager, Spieler, Ablöse)
    st.subheader("Aktuelle Auswahl")
    if "Ablöse_num" in df.columns:
        df_display = df.sort_values(by="Ablöse_num", ascending=False)
    else:
        df_display = df

    desired_cols = ["Saison", "Manager", "Spieler", "Ablöse"]
    cols_to_show = [c for c in desired_cols if c in df_display.columns]
    st.dataframe(df_display[cols_to_show], use_container_width=True, hide_index=True)

    st.divider()

    # 5. FOKUS-GRAFIK (Mit abgekürzten, waagerechten Saisons)
    st.subheader("Ausgaben-Verlauf")
    if not df.empty:
        df_chart = df.groupby("Saison")["Ablöse_num"].sum().reset_index()
        
        # Saison abkürzen (z. B. "2001/2002" -> "2001")
        df_chart["Saison_kurz"] = df_chart["Saison"].astype(str).str.split('/').str[0]
        df_chart["Mio"] = df_chart["Ablöse_num"] / 1e6
        
        fig = px.bar(df_chart, x="Saison_kurz", y="Mio", labels={"Mio": "Mio. €", "Saison_kurz": "Saison"})
        
        # tickangle: 0 stellt den Text waagerecht direkt unter die Balken
        fig.update_layout(
            xaxis={"type": "category", "fixedrange": True, "tickangle": 0}, 
            yaxis={"fixedrange": True}, 
            height=300, 
            margin=dict(l=20, r=20, t=10, b=40)
        )
        st.plotly_chart(fig, use_container_width=True, config=MOBILE_PLOTLY_CONFIG)

except Exception as e:
    st.error(f"Fehler beim Laden: {e}")
