import streamlit as st
import pandas as pd

st.set_page_config(page_title="S04 Transfer-Dashboard", layout="wide")
st.title("⚽ S04 Transfers")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSkS8BNWhblJuNDjHFrNLr6kD4I4ctFZcd_z11qnTiUfmymwb83fip4_iVRFzH5w7HCQNxVfcnnu2d7/pub?output=csv"

@st.cache_data(ttl=600)
def load_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data(CSV_URL)
    df_filtered = df.copy()

    # Finde die echte Ablöse-Spalte automatisch (egal ob mit Umlaut oder Sonderzeichen)
    ablöse_col = next((c for c in df.columns if "ablöse" in c.lower() or "abloese" in c.lower()), None)

    st.sidebar.header("🔍 Filter")

    # 1. Slider für Alter
    if "Alter" in df.columns:
        min_a, max_a = int(df["Alter"].min()), int(df["Alter"].max())
        alter_range = st.sidebar.slider("Alter", min_a, max_a, (min_a, max_a))
        df_filtered = df_filtered[(df_filtered["Alter"] >= alter_range[0]) & (df_filtered["Alter"] <= alter_range[1])]

    # 2. Slider für Ablöse (falls gefunden)
    if ablöse_col:
        # Bereinige die Werte für den Slider im Hintergrund
        temp_ablöse = df[ablöse_col].astype(str).str.replace('€', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        temp_ablöse_num = pd.to_numeric(temp_ablöse, errors='coerce').fillna(0)
        
        min_abl, max_abl = int(temp_ablöse_num.min()), int(temp_ablöse_num.max())
        if min_abl < max_abl:
            abl_range = st.sidebar.slider("Ablöse Bereich (€)", min_abl, max_abl, (min_abl, max_abl), step=100000)
            mask = (temp_ablöse_num >= abl_range[0]) & (temp_ablöse_num <= abl_range[1])
            df_filtered = df_filtered[mask]

    # 3. Dropdowns für Kategorien
    kategorien = ["Saison", "Position", "Nationalität", "Kontinent", "Transferart"]
    for kat in kategorien:
        if kat in df.columns:
            vals = ["Alle"] + sorted(df[kat].dropna().unique().astype(str).tolist())
            wahl = st.sidebar.selectbox(f"{kat}", vals)
            if wahl != "Alle":
                df_filtered = df_filtered[df_filtered[kat].astype(str) == wahl]

    # Anzeige
    st.metric("Gefundene Transfers", len(df_filtered))
    
    # Tabelle anzeigen (die originale Ablöse-Spalte bleibt unberührt und voll sichtbar)
    st.dataframe(df_filtered, use_container_width=True)

except Exception as e:
    st.error("Fehler beim Laden der Daten.")
    st.write(e)
