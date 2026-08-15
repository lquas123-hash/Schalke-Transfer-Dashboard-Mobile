import pandas as pd
import streamlit as st

st.set_page_config(page_title="S04 Transfer-App", layout="centered")
st.title("⚽ S04 Transfers")

# Dein Google Sheet Link
SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/1IY08gTk5TEqykFRGuBFX3l5-JledI0-CP_KLvotOYQ/edit?gid=0#gid=0"
)


@st.cache_data(ttl=600)
def load_data(url):
  # Hier wandeln wir den normalen Link sicher in den direkten Export-Link um
  if "/edit" in url:
    base_url = url.split("/edit")[0]
    csv_url = f"{base_url}/export?format=csv"
  else:
    csv_url = url
  return pd.read_csv(csv_url)


# Daten laden mit Fehlerbehandlung
try:
  df = load_data(SHEET_URL)

  # Mobile-freundliche Filter
  with st.expander("🔍 Filter & Suche"):
    if "Position" in df.columns:
      pos = ["Alle"] + list(df["Position"].dropna().unique())
      s = st.selectbox("Position filtern:", pos)
      if s != "Alle":
        df = df[df["Position"] == s]

  # Kompakte Tabelle anzeigen
  st.dataframe(df, use_container_width=True)

except Exception as e:
  st.error(
      "Fehler beim Laden der Daten. Bitte stelle sicher, dass das Google Sheet"
      ' auf "Jeder mit dem Link kann es als Betrachter öffnen" gestellt ist!'
  )
  st.info(f"Technischer Fehler: {e}")
