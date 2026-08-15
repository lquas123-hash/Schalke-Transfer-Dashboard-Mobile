import streamlit as st
import pandas as pd

# 1. Layout-Einstellungen
st.set_page_config(page_title="S04 Transfer-App", layout="centered")
st.title("⚽ S04 Transfers")

# 2. HIER DEINEN LINK EINFÜGEN!
# Kopiere den Link aus deinem Browser-Fenster hier rein:
SHEET_URL = https://docs.google.com/spreadsheets/d/1IYO8gTk5TYeqykFRGuBFX3l5-JledI0-CP_KLvotOYQ/edit?gid=0#gid=0

# 3. Daten direkt laden
@st.cache_data(ttl=600) 
def load_data(url):
    # Der Trick, um das Sheet als CSV zu lesen
    csv_url = url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

# Daten laden
df = load_data(SHEET_URL)

# 4. Mobile-freundliche Filter
with st.expander("🔍 Filter & Suche"):
    # Beispiel: Wenn du eine Spalte 'Position' hast
    if "Position" in df.columns:
        pos = ["Alle"] + list(df["Position"].unique())
        s = st.selectbox("Position filtern:", pos)
        if s != "Alle":
            df = df[df["Position"] == s]

# 5. Kompakte Tabelle
st.dataframe(df, use_container_width=True)
