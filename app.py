import pandas as pd
import streamlit as st

st.set_page_config(page_title="S04 Transfer-App", layout="centered")
st.title("⚽ S04 Transfers")

# HIER DEN NEUEN CSV-LINK EINTRAGEN (den du gerade kopiert hast)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSkS8BNWhblJuNDjHFrNLr6kD4I4ctFZcd_z11qnTiUfmymwb83fip4_iVRFzH5w7HCQNxVfcnnu2d7/pub?output=csv"


@st.cache_data(ttl=600)
def load_data(url):
  return pd.read_csv(url)


try:
  df = load_data(CSV_URL)

  with st.expander("🔍 Filter & Suche"):
    if "Position" in df.columns:
      pos = ["Alle"] + list(df["Position"].dropna().unique())
      s = st.selectbox("Position filtern:", pos)
      if s != "Alle":
        df = df[df["Position"] == s]

  st.dataframe(df, use_container_width=True)

except Exception as e:
  st.error("Fehler beim Laden der CSV-Daten.")
  st.info(f"Technischer Fehler: {e}")
