import pandas as pd
import streamlit as st

st.set_page_config(page_title="S04 Transfer-App", layout="centered")
st.title("⚽ S04 Transfers (Mobile)")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSkS8BNWhblJuNDjHFrNLr6kD4I4ctFZcd_z11qnTiUfmymwb83fip4_iVRFzH5w7HCQNxVfcnnu2d7/pub?output=csv"


@st.cache_data(ttl=600)
def load_data(url):
  # Wir lesen die CSV ein (header=None, weil wir die Spaltennamen selbst bestimmen)
  df = pd.read_csv(url, header=None, engine="python", on_bad_lines="skip")
  df = df.dropna(how="all")

  # Hier vergeben wir die exakten Kategorien der Reihe nach:
  # (Falls du mehr oder weniger Spalten hast, passen wir das an)
  kategorien = [
      "Saison",
      "Manager",
      "Spieler",
      "Position",
      "Nationalität",
      "Kontinent",
      "Verein",
      "Liga",
      "Markt",
      "Transferart",
  ]

  # Falls das Sheet mehr Spalten hat, füllen wir den Rest automatisch auf
  if len(df.columns) > len(kategorien):
    for i in range(len(kategorien), len(df.columns)):
      kategorien.append(f"Spalte {i+1}")

  df.columns = kategorien[: len(df.columns)]
  return df


try:
  df = load_data(CSV_URL)

  st.metric("Gesamt Transfers", len(df))

  # Saubere Filter nach den echten Kategorien
  with st.expander("🔍 Nach Kategorien filtern", expanded=True):
    # Die wichtigsten Kategorien als gezielte Filter anbieten
    ziel_spalten = [
        "Saison",
        "Position",
        "Manager",
        "Nationalität",
        "Kontinent",
        "Transferart",
    ]

    for spalte in ziel_spalten:
      if spalte in df.columns:
        optionen = ["Alle"] + list(df[spalte].dropna().unique().astype(str))
        wahl = st.selectbox(f"Filter nach {spalte}:", optionen)
        if wahl != "Alle":
          df = df[df[spalte].astype(str) == wahl]

  st.dataframe(df, use_container_width=True)

except Exception as e:
  st.error("Fehler beim Laden der Daten.")
  st.info(f"Details: {e}")
