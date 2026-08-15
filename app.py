import pandas as pd
import streamlit as st

st.set_page_config(page_title="S04 Transfer-App", layout="centered")
st.title("⚽ S04 Transfers (Mobile)")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSkS8BNWhblJuNDjHFrNLr6kD4I4ctFZcd_z11qnTiUfmymwb83fip4_iVRFzH5w7HCQNxVfcnnu2d7/pub?output=csv"


@st.cache_data(ttl=600)
def load_data(url):
  # Wir laden die CSV ganz normal ab Zeile 1 ohne Zeilen zu überspringen
  df = pd.read_csv(url, engine="python", on_bad_lines="skip")
  df = df.dropna(how="all")

  # Falls deine Tabelle oben noch Leerzeilen hat, schneiden wir sie ab,
  # sobald die Spalte mit der Saison (erste Spalte) Daten enthält
  return df


try:
  df = load_data(CSV_URL)

  # Falls die erste Zeile die echten Spaltennamen enthält aber als Daten gelistet ist:
  # Wir geben den Spalten feste Namen, falls sie durcheinander sind.
  # (Passe die Namen hier an, falls deine Spalten im Google Sheet anders heißen)
  erwartete_spalten = [
      "Saison",
      "Manager/Trainer",
      "Spieler",
      "Position",
      "Alter",
      "Ablöse",
      "Land",
      "Art",
  ]

  # Wenn die Spaltenanzahl ungefähr passt, benennen wir sie sauber um
  if len(df.columns) >= len(erwartete_spalten):
    df.columns = erwartete_spalten + list(df.columns[len(erwartete_spalten) :])

  # Statistik oben
  st.metric("Gesamt Transfers", len(df))

  # Funktionierende Filter
  with st.expander("🔍 Filter & Optionen", expanded=True):
    # Nach Position filtern
    if "Position" in df.columns:
      pos_liste = ["Alle"] + list(df["Position"].dropna().unique().astype(str))
      w_pos = st.selectbox("Position:", pos_liste)
      if w_pos != "Alle":
        df = df[df["Position"].astype(str) == w_pos]

    # Nach Saison filtern
    if "Saison" in df.columns:
      saison_liste = ["Alle"] + list(
          df["Saison"].dropna().unique().astype(str)
      )
      w_saison = st.selectbox("Saison:", saison_liste)
      if w_saison != "Alle":
        df = df[df["Saison"].astype(str) == w_saison]

  # Tabelle sauber anzeigen
  st.dataframe(df, use_container_width=True)

except Exception as e:
  st.error("Fehler beim Verarbeiten der Daten.")
  st.info(f"Details: {e}")
