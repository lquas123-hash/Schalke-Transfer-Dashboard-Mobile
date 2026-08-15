import pandas as pd
import streamlit as st

st.set_page_config(page_title="S04 Transfer-App", layout="centered")
st.title("⚽ S04 Transfers (Mobile)")

# Dein CSV-Link
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSkS8BNWhblJuNDjHFrNLr6kD4I4ctFZcd_z11qnTiUfmymwb83fip4_iVRFzH5w7HCQNxVfcnnu2d7/pub?output=csv"

@st.cache_data(ttl=600)
def load_data(url):
    df = pd.read_csv(url, engine="python", on_bad_lines="skip")
    df.columns = df.columns.str.strip()
    df = df.dropna(how="all")
    
    # Entfernt die doppelte Kopfzeile, falls sie existiert
    if len(df) > 0 and str(df.iloc[0, 0]).lower() in ["saison", "jahr", "spielzeit"]:
        df = df.iloc[1:].reset_index(drop=True)
    return df

try:
    df = load_data(CSV_URL)
    
    # Statistik oben
    st.metric("Gesamt Transfers", len(df))

    # Filter-Bereich
    with st.expander("🔍 Alle Kategorien filtern", expanded=True):
        # Wir gehen durch JEDE Spalte im Sheet und erstellen einen Filter dafür
        for spalte in df.columns:
            # Dropdown für jede Spalte erstellen
            optionen = ["Alle"] + list(df[spalte].dropna().unique().astype(str))
            wahl = st.selectbox(f"Filter nach {spalte}:", optionen)
            
            # Daten sofort filtern, wenn etwas anderes als "Alle" gewählt wurde
            if wahl != "Alle":
                df = df[df[spalte].astype(str) == wahl]

    # Tabelle anzeigen
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("Fehler beim Laden der Daten.")
    st.info(f"Details: {e}")
