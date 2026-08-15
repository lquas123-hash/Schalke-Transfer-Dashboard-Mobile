import streamlit as st
import pandas as pd

# Konfiguration
st.set_page_config(page_title="S04 Transfer-Dashboard", layout="wide")
st.title("⚽ S04 Transfers")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSkS8BNWhblJuNDjHFrNLr6kD4I4ctFZcd_z11qnTiUfmymwb83fip4_iVRFzH5w7HCQNxVfcnnu2d7/pub?output=csv"

@st.cache_data(ttl=600)
def load_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    
    # Hilfsspalte für die Berechnung (Ablöse als Zahl)
    if "Ablöse" in df.columns:
        # Entfernt '€' und '.' für die Berechnung
        df["Ablöse_Num"] = df["Ablöse"].astype(str).replace({'€': '', '\.': ''}, regex=True)
        # Handle "0€" oder leere Werte zu 0
        df["Ablöse_Num"] = pd.to_numeric(df["Ablöse_Num"], errors='coerce').fillna(0)
    return df

try:
    df = load_data(CSV_URL)
    df_filtered = df.copy()

    st.sidebar.header("🔍 Filter")

    # 1. Slider für Alter
    if "Alter" in df.columns:
        min_a, max_a = int(df["Alter"].min()), int(df["Alter"].max())
        alter_range = st.sidebar.slider("Alter", min_a, max_a, (min_a, max_a))
        df_filtered = df_filtered[(df_filtered["Alter"] >= alter_range[0]) & (df_filtered["Alter"] <= alter_range[1])]

    # 2. Slider für Ablöse
    if "Ablöse_Num" in df.columns:
        min_abl, max_abl = int(df["Ablöse_Num"].min()), int(df["Ablöse_Num"].max())
        # Wir lassen den Slider in 100k-Schritten laufen
        abl_range = st.sidebar.slider("Ablöse Bereich (€)", min_abl, max_abl, (min_abl, max_abl), step=100000)
        df_filtered = df_filtered[(df_filtered["Ablöse_Num"] >= abl_range[0]) & (df_filtered["Ablöse_Num"] <= abl_range[1])]

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
    
    # WICHTIG: Hier verstecken wir nur die technische Spalte 'Ablöse_Num', 
    # aber die originale 'Ablöse' Spalte bleibt sichtbar!
    if "Ablöse_Num" in df_filtered.columns:
        df_show = df_filtered.drop(columns=["Ablöse_Num"])
    else:
        df_show = df_filtered
        
    st.dataframe(df_show, use_container_width=True)

except Exception as e:
    st.error("Fehler beim Laden der Daten.")
    st.write(e)
