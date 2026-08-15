import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="S04 Transfers", layout="wide")

# CSS für kompakte Darstellung
st.markdown("""
    <style>
    /* Filter-Bereich immer kompakt */
    .stSelectbox { margin-top: -10px; }
    /* Kennzahlen-Box kleiner machen, wenn gefiltert wird */
    [data-testid="stMetricValue"] { font-size: 1.0rem !important; }
    </style>
""", unsafe_allow_html=True)

# ... (Hier bleibt dein load_data Code identisch wie vorher) ...
# (Wichtig: Stelle sicher, dass fillna("") drin bleibt!)

df_raw = load_data(SHEET_ID)

st.title("⚽ Schalke Transfers")

# 1. FILTER KOMMEN HIER HIN (Ganz oben, ohne erst zu scrollen)
with st.container():
    col_f1, col_f2 = st.columns(2)
    # Filter-Logik hier rein... 
    # (Damit die Filter immer sichtbar sind, wenn man die App öffnet)

# 2. ERGEBNIS-BEREICH
st.divider()

# Statt eines Expanders für Kennzahlen nehmen wir columns, die bei Mobile automatisch untereinander rutschen
col1, col2, col3 = st.columns(3)
col1.metric("Anzahl", len(df_filtered))
col2.metric("Ausgaben", f"{int(df_filtered['Ablöse_numerisch'].sum()/1e6)} Mio €")
col3.metric("Ø Alter", f"{df_filtered['Alter_numerisch'].mean():.1f}")

st.divider()

# 3. TABELLE (Direkt danach, ohne Zwischen-Expander)
st.dataframe(df_filtered, use_container_width=True)
