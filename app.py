import pandas as pd
import streamlit as st

st.set_page_config(page_title="S04 Transfer-App", layout="centered")
st.title("⚽ S04 Transfers (Mobile)")

CSV_URL = "https://docs.google.com/spreadsheets/d/1IYO8gTk5TYeqykFRGuBFX3l5-JledI0-CP_KLvotOYQ/edit?gid=0#gid=0"


@st.cache_data(ttl=600)
def load_data(url):
  # skiprows=6 überspringt die ersten 6 Zeilen, falls dort das Logo/Überschriften stehen
  # header=0 macht die neue erste Zeile (Zeile 7) zur echten Spaltenüberschrift
  df = pd.read_csv(url, skiprows=6)
  # Spaltennamen bereinigen (Leerzeichen entfernen)
  df.columns = df.columns.str.strip()
  return df


try:
  df = load_data(CSV_URL)

  # Kleine Statistik-Box oben (wie in deiner alten Version)
  col1, col2 = st.columns(2)
  with col1:
    st.metric("Gesamt Transfers", len(df))
  with col2:
    if "Ablöse" in df.columns:
      st.metric("Tabelle", "Aktiv")

  # Dynamische Filter (sucht automatisch nach passenden Spalten)
  with st.expander("🔍 Filter & Optionen", expanded=True):
    # Finde Spalten, die nach Position oder Saison aussehen könnten
    mögliche_spalten = [
        c
        for c in df.columns
        if "position" in c.lower() or "saison" in c.lower()
    ]

    for col in mögliche_spalten:
      werte = ["Alle"] + list(df[col].dropna().unique().astype(str))
      auswahl = st.selectbox(f"Filter nach {col}:", werte)
      if auswahl != "Alle":
        df = df[df[col].astype(str) == auswahl]

  # Tabelle anzeigen
  st.dataframe(df, use_container_width=True)

except Exception as e:
  st.error("Fehler beim Verarbeiten der Daten.")
  st.info(f"Details: {e}")
