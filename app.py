import pandas as pd
import streamlit as st

st.set_page_config(page_title="S04 Transfer-App", layout="centered")
st.title("⚽ S04 Transfers (Mobile)")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSkS8BNWhblJuNDjHFrNLr6kD4I4ctFZcd_z11qnTiUfmymwb83fip4_iVRFzH5w7HCQNxVfcnnu2d7/pub?output=csv"


@st.cache_data(ttl=600)
def load_data(url):
  # engine='python' und on_bad_lines='skip' verhindern Abstürze bei unsauberen Zeilen
  df = pd.read_csv(url, skiprows=6, engine="python", on_bad_lines="skip")
  df.columns = df.columns.str.strip()
  # Entferne komplett leere Zeilen
  df = df.dropna(how="all")
  return df


try:
  df = load_data(CSV_URL)

  # Statistik oben
  st.metric("Gesamt Transfers", len(df))

  # Filter
  with st.expander("🔍 Filter & Optionen", expanded=True):
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
