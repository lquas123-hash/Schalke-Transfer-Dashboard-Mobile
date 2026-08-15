import pandas as pd
import streamlit as st

st.set_page_config(page_title="S04 Transfer-App", layout="centered")
st.title("⚽ S04 Transfers (Mobile)")

# ---------------------------------------------------------
# HIER DEINEN LINK EINTRAGEN
# ---------------------------------------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSkS8BNWhblJuNDjHFrNLr6kD4I4ctFZcd_z11qnTiUfmymwb83fip4_iVRFzH5w7HCQNxVfcnnu2d7/pub?output=csv"


@st.cache_data(ttl=600)
def load_data(url):
  # Wandelt jeden normalen Google-Sheet-Link in den direkten CSV-Export um
  if "/edit" in url:
    csv_url = url.split("/edit")[0] + "/export?format=csv"
  else:
    csv_url = url

  # Wir lesen das Sheet ein und nutzen Zeile 1 als echte Überschrift
  df = pd.read_csv(csv_url, engine="python")
  df.columns = df.columns.str.strip()  # Leerzeichen entfernen
  df = df.dropna(how="all")  # Leere Zeilen löschen
  return df


try:
  df = load_data(SHEET_URL)

  # Anzeige der Gesamtzahl
  st.metric("Gesamt Transfers", len(df))

  # Saubere Dropdown-Filter für alle vorhandenen Spalten
  with st.expander("🔍 Nach Kategorien filtern", expanded=True):
    for spalte in df.columns:
      if "unnamed" not in spalte.lower():
        optionen = ["Alle"] + list(df[spalte].dropna().unique().astype(str))
        wahl = st.selectbox(f"Filter nach {spalte}:", optionen)
        if wahl != "Alle":
          df = df[df[spalte].astype(str) == wahl]

  # Tabelle anzeigen
  st.dataframe(df, use_container_width=True)

except Exception as e:
  st.error(
      "Fehler beim Laden. Bitte prüfe, ob das Google Sheet öffentlich"
      ' ("Jeder mit dem Link kann als Betrachter öffnen") eingestellt ist!'
  )
  st.info(f"Details: {e}")
