import streamlit as st
import pandas as pd
import numpy as np

# Konfiguration
st.set_page_config(page_title="S04 Transfer-Dashboard", layout="wide")
st.title("⚽ S04 Transfers")

# HIER DEINEN CSV-LINK VON "IM WEB VERÖFFENTLICHEN" EINFÜGEN
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSkS8BNWhblJuNDjHFrNLr6kD4I4ctFZcd_z11qnTiUfmymwb83fip4_iVRFzH5w7HCQNxVfcnnu2d7/pub?output=csv"

@st.cache_data(ttl=600)
def load_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    # Versuch, Ablöse in eine reine Zahl umzuwandeln (entfernt € und Punkte)
    if "Ablöse" in df.columns:
        df["Ablöse_Num"] = df["Ablöse"].replace({'€': '', '\.': ''}, regex=True)
        df["Ablöse_Num"] = pd.to_numeric(df["Ablöse_Num"], errors='coerce').fillna(0)
    return df

try:
    df = load_data(CSV_URL)
    df_filtered = df.copy()

    st.sidebar.header("🔍 Filter")

    # 1. Slider für Alter (falls vorhanden)
    if "Alter" in df.columns:
        min_alter, max_alter = int(df["Alter"].min()), int(df["Alter"].max())
        alter_range = st.sidebar.slider("Alter", min_alter, max_alter, (min_alter, max_alter))
        df_filtered = df_filtered[(df_filtered["Alter"] >= alter_range[0]) & (df_filtered["Alter"] <= alter_range[1])]

    # 2. Slider für Ablöse (falls Spalte umgewandelt wurde)
    if "Ablöse_Num" in df.columns:
        min_abl, max_abl = int(df["Ablöse_Num"].min()), int(df["Ablöse_Num"].max())
        abl_range = st.sidebar.slider("Ablöse (€)", min_abl, max_abl, (min_abl, max_abl), step=100000)
        df_filtered = df_filtered[(df_filtered["Ablöse_Num"] >= abl_range[0]) & (df_filtered["Ablöse_Num"] <= abl_range[1])]

    # 3. Dropdowns für den Rest (Kategorien)
    kategorien = ["Saison", "Position", "Nationalität", "Kontinent", "Transferart"]
    for kat in kategorien:
        if kat in df.columns:
            unique_vals = ["Alle"] + sorted(df[kat].dropna().unique().astype(str).tolist())
            wahl = st.sidebar.selectbox(f"{kat}", unique_vals)
            if wahl != "Alle":
                df_filtered = df_filtered[df_filtered[kat].astype(str) == wahl]

    # Anzeige
    st.metric("Gefundene Transfers", len(df_filtered))
    
    # Tabelle ohne die technische Ablöse-Spalte anzeigen
    cols_to_show = [c for c in df_filtered.columns if c != "Ablöse_Num"]
    st.dataframe(df_filtered[cols_to_show], use_container_width=True)

except Exception as e:
    st.error("Fehler beim Laden. Bitte prüfe den CSV-Link.")
    st.write(e)
