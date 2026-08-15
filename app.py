import streamlit as st
import pandas as pd

# Konfiguration
st.set_page_config(page_title="S04 Transfer-Dashboard", layout="wide")
st.title("⚽ S04 Transfers")

# HIER DEINEN CSV-LINK VON "IM WEB VERÖFFENTLICHEN" EINFÜGEN
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSkS8BNWhblJuNDjHFrNLr6kD4I4ctFZcd_z11qnTiUfmymwb83fip4_iVRFzH5w7HCQNxVfcnnu2d7/pub?output=csv"

@st.cache_data(ttl=600)
def load_data(url):
    # Liest die Datei direkt und nutzt die erste Zeile als Header
    df = pd.read_csv(url)
    # Entfernt Leerzeichen aus den Spaltennamen
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data(CSV_URL)

    # Filter-Bereich in der Sidebar für echtes Mobile-Feeling
    st.sidebar.header("🔍 Filter")
    
    # Dynamische Filter für jede Spalte
    filters = {}
    for column in df.columns:
        # Nur Spalten mit vernünftigen Werten anbieten
        unique_vals = ["Alle"] + sorted(df[column].dropna().unique().astype(str).tolist())
        filters[column] = st.sidebar.selectbox(f"{column}", unique_vals)

    # Daten filtern
    df_filtered = df.copy()
    for column, selection in filters.items():
        if selection != "Alle":
            df_filtered = df_filtered[df_filtered[column].astype(str) == selection]

    # Anzeige
    st.metric("Anzahl Transfers", len(df_filtered))
    st.dataframe(df_filtered, use_container_width=True)

except Exception as e:
    st.error("Fehler beim Laden. Bitte prüfe, ob die CSV-Veröffentlichung aktuell ist.")
    st.write(e)
