import pandas as pd
import streamlit as st

st.set_page_config(page_title="S04 Transfer-App", layout="centered")
st.title("⚽ S04 Transfers (Mobile)")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSkS8BNWhblJuNDjHFrNLr6kD4I4ctFZcd_z11qnTiUfmymwb83fip4_iVRFzH5w7HCQNxVfcnnu2d7/pub?output=csv"

@st.cache_data(ttl=600)
def load_data(url):
    # header=6 sagt: Nutze Zeile 7 als echten Tabellenkopf (weil die echten Spalten bei dir weiter unten im Sheet stehen).
    # Falls deine Spalten in Zeile 5 oder 8 stehen, müssen wir die Zahl (6) gleich anpassen!
    df = pd.read_csv(url, header=6, engine="python", on_bad_lines="skip")
    df.columns = df.columns.str.strip()
    df = df.dropna(how="all")
    return df

try:
    df = load_data(CSV_URL)
    
    st.metric("Gesamt Transfers", len(df))

    # Alle Kategorien als Filter untereinander
    with st.expander("🔍 Nach Kategorien filtern", expanded=True):
        for spalte in df.columns:
            # Nur filtern, wenn die Spalte auch einen echten Namen hat (kein "Unnamed")
            if "unnamed" not in spalte.lower():
                optionen = ["Alle"] + list(df[spalte].dropna().unique().astype(str))
                wahl = st.selectbox(f"Filter nach {spalte}:", optionen)
                
                if wahl != "Alle":
                    df = df[df[spalte].astype(str) == wahl]

    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("Fehler beim Laden der Daten.")
    st.info(f"Details: {e}")
