import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Schalke Transfer-Dashboard", 
    page_icon="⚽", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Mobiles CSS für kompaktes Layout
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 1.0rem !important;
        white-space: normal !important;
    }
    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.5rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

MOBILE_PLOTLY_CONFIG = {
    'displayModeBar': False,
    'scrollZoom': False,
    'doubleClick': False
}

SHEET_ID = "1IYO8gTk5TYeqykFRGuBFX3l5-JledI0-CP_KLvotOYQ"

@st.cache_data(ttl=60, show_spinner=False)
def load_data(sheet_id):
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(csv_url, header=2)
    df = df.fillna("") # Verhindert das Löschen unvollständiger Zeilen

    standard_spalten = [
        "Saison", "Manager", "Spieler", "Position", "Alter", "Ablöse",
        "Nationalität", "Kontinent", "Abgebender_Verein", "Liga", "Region", "Transferart"
    ]

    if len(df.columns) >= len(standard_spalten):
        df.columns = standard_spalten + list(df.columns[len(standard_spalten):])
    else:
        df.columns = standard_spalten[:len(df.columns)]

    # Ablöse numerisch aufbereiten
    if "Ablöse" in df.columns:
        df["Ablöse_numerisch"] = (
            df["Ablöse"].astype(str)
            .str.replace("€", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.extract(r"(\d+\.?\d*)")[0]
        )
        df["Ablöse_numerisch"] = pd.to_numeric(df["Ablöse_numerisch"], errors="coerce").fillna(0)
    else:
        df["Ablöse_numerisch"] = 0

    if "Spieler" in df.columns:
        df.loc[df["Ablöse_numerisch"] > 26000000, "Ablöse_numerisch"] = 26500000

    # Alter numerisch aufbereiten
    if "Alter" in df.columns:
        df["Alter_numerisch"] = pd.to_numeric(df["Alter"], errors="coerce")
    else:
        df["Alter_numerisch"] = None

    return df

try:
    df_raw = load_data(SHEET_ID)

    st.title("⚽ Schalke Transfers")
    st.caption("Live-Dashboard")

    # --- 1. FILTER AB SOFORT GANZ OBEN (Kein langes Scrollen mehr) ---
    st.markdown("### 🔍 Filter")
    df_filtered = df_raw.copy()

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_cols_1 = [c for c in ["Saison", "Manager", "Position", "Transferart"] if c in df_filtered.columns]
        for col in filter_cols_1:
            options = ["Alle"] + sorted([str(x) for x in df_raw[col].unique() if x != ""])
            choice = st.selectbox(f"{col}:", options, key=f"top_filter_{col}")
            if choice != "Alle":
                df_filtered = df_filtered[df_filtered[col].astype(str) == choice]

    with col_f2:
        filter_cols_2 = [c for c in ["Liga", "Region"] if c in df_filtered.columns]
        for col in filter_cols_2:
            options = ["Alle"] + sorted([str(x) for x in df_raw[col].unique() if x != ""])
            choice = st.selectbox(f"{col}:", options, key=f"top_filter_{col}")
            if choice != "Alle":
                df_filtered = df_filtered[df_filtered[col].astype(str) == choice]

    if st.button("🔄 Filter zurücksetzen / Neu laden", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    # --- 2. KENNZAHLEN DIREKT DARUNTER ---
    if not df_filtered.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Transfers", len(df_filtered))
        sum_spend = df_filtered['Ablöse_numerisch'].sum() / 1e6
        c2.metric("Ausgaben", f"{sum_spend:.1f}M €")
        avg_spend = df_filtered['Ablöse_numerisch'].mean() / 1e6 if len(df_filtered) > 0 else 0
        c3.metric("Ø Ablöse", f"{avg_spend:.1f}M €")
        avg_age = df_filtered['Alter_numerisch'].mean()
        c4.metric("Ø Alter", f"{avg_age:.1f} J" if pd.notna(avg_age) else "—")

    st.divider()

    # --- 3. TRANSFERLISTE (Sofort im Blick) ---
    st.subheader("📋 Transferliste")
    cols_to_drop = [c for c in ["Alter_numerisch"] if c in df_filtered.columns]
    df_display = df_filtered.drop(columns=cols_to_drop)
    
    if "Ablöse_numerisch" in df_display.columns:
        df_display = df_display.sort_values(by="Ablöse_numerisch", ascending=False)
        df_display_final = df_display.drop(columns=["Ablöse_numerisch"])
    else:
        df_display_final = df_display

    st.dataframe(df_display_final, use_container_width=True, hide_index=True)

    st.divider()

    # --- 4. ANALYSEN & GRAFIKEN (In Expandern für sauberes Handy-Design) ---
    with st.expander("📈 Standard-Grafiken anzeigen", expanded=False):
        grafik_auswahl = st.selectbox(
            "Analyse wählen:", 
            ["Keine", "💰 Gesamtausgaben pro Saison", "⚽ Ausgaben nach Position", "👔 Ausgaben nach Manager", "🌍 Ausgaben nach Region"]
        )

        if grafik_auswahl != "Keine":
            mapping = {
                "💰 Gesamtausgaben pro Saison": "Saison", 
                "⚽ Ausgaben nach Position": "Position", 
                "👔 Ausgaben nach Manager": "Manager",
                "🌍 Ausgaben nach Region": "Region"
            }
            col = mapping[grafik_auswahl]
            if col in df_raw.columns:
                df_chart = df_raw.groupby(col)["Ablöse_numerisch"].sum().reset_index()
                df_chart["Ablöse_Mio"] = df_chart["Ablöse_numerisch"] / 1e6
                fig = px.bar(df_chart, x=col, y="Ablöse_Mio", labels={"Ablöse_Mio": "Ausgaben (Mio. €)"}, color_discrete_sequence=["#004D9E"])
                fig.update_layout(xaxis={"type": "category", "tickangle": -45, "fixedrange": True}, yaxis={"fixedrange": True}, height=380, margin=dict(l=10, r=10, t=30, b=80))
                st.plotly_chart(fig, use_container_width=True, config=MOBILE_PLOTLY_CONFIG)

    with st.expander("📊 Manager-Vergleich", expanded=False):
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Scatter", "💰 Ausgaben", "🎂 Alter", "⚽ Positionen"])
        
        with tab1:
            df_scatter = df_raw.dropna(subset=["Alter_numerisch", "Ablöse_numerisch"]).copy()
            if not df_scatter.empty:
                df_scatter["Ablöse_Mio"] = df_scatter["Ablöse_numerisch"] / 1e6
                fig_scatter = px.scatter(df_scatter, x="Alter_numerisch", y="Ablöse_Mio", hover_data=["Spieler", "Manager"], color_discrete_sequence=["#2b7fff"])
                fig_scatter.update_layout(xaxis={"fixedrange": True}, yaxis={"fixedrange": True}, height=380, margin=dict(l=10, r=10, t=20, b=40))
                st.plotly_chart(fig_scatter, use_container_width=True, config=MOBILE_PLOTLY_CONFIG)

        with tab2:
            df_vol = df_raw.groupby("Manager").agg(Gesamtausgaben=("Ablöse_numerisch", lambda x: x.sum() / 1e6)).reset_index()
            fig_vol = px.bar(df_vol, x="Manager", y="Gesamtausgaben", text_auto=".1f", color_discrete_sequence=["#004D9E"])
            fig_vol.update_layout(xaxis={"type": "category", "tickangle": -45, "fixedrange": True}, yaxis={"fixedrange": True}, height=380, margin=dict(l=10, r=10, t=40, b=80))
            st.plotly_chart(fig_vol, use_container_width=True, config=MOBILE_PLOTLY_CONFIG)

        with tab3:
            df_age = df_raw.dropna(subset=["Alter_numerisch"]).copy()
            if not df_age.empty:
                df_age["Altersgruppe"] = pd.cut(df_age["Alter_numerisch"], bins=[0, 20, 25, 29, 100], labels=["< 21", "21–25", "26–29", "30+"])
                fig_age = px.histogram(df_age, x="Manager", color="Altersgruppe", barmode="stack")
                fig_age.update_layout(xaxis={"type": "category", "tickangle": -45, "fixedrange": True}, yaxis={"fixedrange": True}, height=400, margin=dict(l=10, r=10, t=20, b=80))
                st.plotly_chart(fig_age, use_container_width=True, config=MOBILE_PLOTLY_CONFIG)

        with tab4:
            if "Position" in df_raw.columns:
                pos_df = df_raw.groupby(["Manager", "Position"]).size().reset_index(name="Anzahl")
                pos_df["Prozent"] = pos_df.groupby("Manager")["Anzahl"].transform(lambda x: (x / x.sum()) * 100)
                fig_pos = px.bar(pos_df, x="Manager", y="Prozent", color="Position", barmode="stack")
                fig_pos.update_layout(xaxis={"type": "category", "tickangle": -45, "fixedrange": True}, yaxis={"fixedrange": True}, height=400, margin=dict(l=10, r=10, t=20, b=100))
                st.plotly_chart(fig_pos, use_container_width=True, config=MOBILE_PLOTLY_CONFIG)

    with st.expander("🛠️ Custom Chart Builder", expanded=False):
        df_custom = df_raw.copy()
        c1, c2, c3 = st.columns(3)
        available_x = [c for c in ["Manager", "Position", "Transferart", "Saison", "Liga", "Region", "Nationalität"] if c in df_custom.columns]
        x_col = c1.selectbox("X-Achse:", available_x, index=0, key="cc_x")
        y_metric = c2.selectbox("Metrik:", ["Gesamtausgaben (Mio. €)", "Anzahl Transfers", "Ø Ablöse (Mio. €)", "Ø Alter"], index=0, key="cc_y")
        chart_type = c3.selectbox("Typ:", ["Balkendiagramm", "Kreisdiagramm"], index=0, key="cc_t")

        if not df_custom.empty:
            if y_metric == "Gesamtausgaben (Mio. €)":
                df_grp = df_custom.groupby(x_col)["Ablöse_numerisch"].sum().reset_index()
                df_grp["Wert"] = df_grp["Ablöse_numerisch"] / 1e6
            elif y_metric == "Anzahl Transfers":
                df_grp = df_custom.groupby(x_col)["Spieler"].count().reset_index()
                df_grp.rename(columns={"Spieler": "Wert"}, inplace=True)
            elif y_metric == "Ø Ablöse (Mio. €)":
                df_grp = df_custom.groupby(x_col)["Ablöse_numerisch"].mean().reset_index()
                df_grp["Wert"] = df_grp["Ablöse_numerisch"] / 1e6
            elif y_metric == "Ø Alter":
                df_grp = df_custom.groupby(x_col)["Alter_numerisch"].mean().reset_index()
                df_grp.rename(columns={"Alter_numerisch": "Wert"}, inplace=True)

            if chart_type == "Balkendiagramm":
                fig_c = px.bar(df_grp, x=x_col, y="Wert", text_auto=".1f")
            else:
                fig_c = px.pie(df_grp, names=x_col, values="Wert")

            fig_c.update_layout(xaxis={"type": "category", "tickangle": -45, "fixedrange": True}, yaxis={"fixedrange": True}, height=400, margin=dict(l=10, r=10, t=30, b=80))
            st.plotly_chart(fig_c, use_container_width=True, config=MOBILE_PLOTLY_CONFIG)

except Exception as e:
    st.error(f"Fehler beim Laden: {e}")
