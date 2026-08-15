import streamlit as st
import pandas as pd
import plotly.express as px

# Das erlaubt das Einbetten via IFrame
st.set_page_config(
    page_title="Schalke Transfer-Dashboard", 
    page_icon="⚽", 
    layout="wide"
)

st.markdown("""
    <style>
    /* Schriftgröße & Umbruch für Kennzahlen anpassen */
    [data-testid="stMetricValue"] {
        font-size: 1.05rem !important;
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.25 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        button[data-baseweb="tab"] {
            padding-left: 8px !important;
            padding-right: 8px !important;
            font-size: 0.85rem !important;
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
    df = df.dropna(how="all")

    standard_spalten = [
        "Saison", "Manager", "Spieler", "Position", "Alter", "Ablöse",
        "Nationalität", "Kontinent", "Abgebender_Verein", "Liga", "Region", "Transferart"
    ]

    if len(df.columns) >= 11:
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

    st.title("⚽ Schalke Transfer-Dashboard: Live-Transfers & Statistiken")
    st.caption("Willkommen im Schalke 04 Transfer-Dashboard!")
    st.divider()

    # 1. Filter-Bereich
    with st.expander("🔍 Filter anpassen (Saison, Manager, Position, Transferart, Alter, Preis...)", expanded=False):
        df_filtered = df_raw.copy()

        col_f1, col_f2 = st.columns(2)

        with col_f1:
            filter_cols_1 = [c for c in ["Saison", "Manager", "Position", "Transferart", "Nationalität"] if c in df_filtered.columns]
            for col in filter_cols_1:
                options = ["Alle"] + sorted(df_raw[col].dropna().astype(str).unique().tolist())
                choice = st.selectbox(f"{col}:", options, key=f"main_filter_{col}")
                if choice != "Alle":
                    df_filtered = df_filtered[df_filtered[col].astype(str) == choice]

        with col_f2:
            filter_cols_2 = [c for c in ["Abgebender_Verein", "Liga", "Region"] if c in df_filtered.columns]
            for col in filter_cols_2:
                options = ["Alle"] + sorted(df_raw[col].dropna().astype(str).unique().tolist())
                choice = st.selectbox(f"{col}:", options, key=f"main_filter_{col}")
                if choice != "Alle":
                    df_filtered = df_filtered[df_filtered[col].astype(str) == choice]

            if "Alter_numerisch" in df_raw.columns and not df_raw.empty:
                min_age = int(df_raw["Alter_numerisch"].min()) if pd.notna(df_raw["Alter_numerisch"].min()) else 15
                max_age = int(df_raw["Alter_numerisch"].max()) if pd.notna(df_raw["Alter_numerisch"].max()) else 40
                if min_age < max_age:
                    alter_range = st.slider("🎂 Alter:", min_age, max_age, (min_age, max_age), key="main_alter_slider")
                    df_filtered = df_filtered[
                        (df_filtered["Alter_numerisch"] >= alter_range[0]) & 
                        (df_filtered["Alter_numerisch"] <= alter_range[1])
                    ]

            if "Ablöse_numerisch" in df_raw.columns and not df_raw.empty:
                max_p_raw = float(df_raw["Ablöse_numerisch"].max()) / 1_000_000
                max_p = max(max_p_raw, 30.0)
                if max_p > 0:
                    preis = st.slider("💰 Ablöse (Mio. €):", 0.0, float(max_p), (0.0, float(max_p)), step=0.5, key="main_preis_slider")
                    df_filtered = df_filtered[
                        (df_filtered["Ablöse_numerisch"] >= preis[0] * 1e6) & 
                        (df_filtered["Ablöse_numerisch"] <= preis[1] * 1e6)
                    ]

        if st.button("🔄 Live-Daten neu laden", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.divider()

    st.subheader("📋 Transferliste (Gefiltert & Sortierbar)")
    cols_to_drop = [c for c in ["Alter_numerisch"] if c in df_filtered.columns]
    df_display = df_filtered.drop(columns=cols_to_drop)
    
    # Sortierung anhand der versteckten numerischen Spalte erzwingen, falls vorhanden
    if "Ablöse_numerisch" in df_display.columns:
        df_display = df_display.sort_values(by="Ablöse_numerisch", ascending=False)
        df_display_final = df_display.drop(columns=["Ablöse_numerisch"])
    else:
        df_display_final = df_display

    st.dataframe(df_display_final, use_container_width=True, hide_index=True)

    st.divider()

    with st.expander("📊 Kennzahlen-Übersicht anzeigen / ausblenden", expanded=True):
        if not df_filtered.empty:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            col1.metric("Anzahl Transfers", len(df_filtered))
            
            sum_spend = df_filtered['Ablöse_numerisch'].sum() / 1e6
            col2.metric("Gesamtausgaben", f"{sum_spend:.2f} Mio. €")
            
            avg_spend = df_filtered['Ablöse_numerisch'].mean() / 1e6 if len(df_filtered) > 0 else 0
            col3.metric("Ø Ablöse", f"{avg_spend:.2f} Mio. €")
            
            avg_age = df_filtered['Alter_numerisch'].mean()
            col4.metric("Ø Alter", f"{avg_age:.1f} Jahre" if pd.notna(avg_age) else "—")
            
            valid_fees = df_filtered[df_filtered['Ablöse_numerisch'] > 0]
            if not valid_fees.empty:
                max_row = valid_fees.loc[valid_fees['Ablöse_numerisch'].idxmax()]
                top_val = max_row['Ablöse_numerisch'] / 1e6
                if top_val > 26.0 and top_val < 27.0:
                    top_val = 26.5
                top_str = f"{max_row['Spieler']} ({top_val:.1f} Mio. €)"
            else:
                top_str = "—"
            col5.metric("⭐ Teuerster Transfer", top_str)
        else:
            st.info("Keine Daten für die gewählten Filter vorhanden.")

    st.divider()

    st.subheader("📈 Analysen & Grafiken (Vollständige Daten - Unabhängig von Filtern)")
    grafik_auswahl = st.selectbox(
        "Analyse wählen:", 
        [
            "Keine", 
            "💰 Gesamtausgaben pro Saison", 
            "⚽ Ausgaben nach Position", 
            "👔 Ausgaben nach Manager", 
            "🌍 Ausgaben nach Region"
        ]
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
            
            fig = px.bar(
                df_chart, 
                x=col, 
                y="Ablöse_Mio", 
                labels={"Ablöse_Mio": "Ausgaben (Mio. €)"},
                color_discrete_sequence=["#004D9E"]
            )
            fig.update_layout(
                xaxis={"type": "category", "tickangle": -45, "fixedrange": True}, 
                yaxis={"fixedrange": True, "title": "Ausgaben (Mio. €)"}, 
                height=420,
                margin=dict(l=10, r=10, t=30, b=80)
            )
            st.plotly_chart(fig, use_container_width=True, config=MOBILE_PLOTLY_CONFIG)

    st.divider()

    with st.expander("📊 Manager-Vergleich anzeigen / ausblenden", expanded=False):
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Alter vs. Preis", 
            "💰 Ausgaben", 
            "🎂 Alter", 
            "⚽ Positionen"
        ])

        age_colors = {
            "< 21 Jahre": "#2ca02c",
            "21–25 Jahre": "#1f77b4",
            "26–29 Jahre": "#ff7f0e",
            "30+ Jahre": "#d62728"
        }

        with tab1:
            df_scatter = df_raw.dropna(subset=["Alter_numerisch", "Ablöse_numerisch"]).copy()
            total_count = len(df_raw)
            valid_count = len(df_scatter)
            
            st.markdown(f"**🎯 Alter bei Verpflichtung**")
            st.caption(f"({valid_count} von {total_count} Transfers dargestellt - Vollständige Daten)")
            
            if not df_scatter.empty:
                df_scatter["Ablöse_Mio"] = df_scatter["Ablöse_numerisch"] / 1e6
                fig_scatter = px.scatter(
                    df_scatter,
                    x="Alter_numerisch",
                    y="Ablöse_Mio",
                    hover_data=["Spieler", "Manager", "Position", "Saison"],
                    labels={"Alter_numerisch": "Alter beim Transfer", "Ablöse_Mio": "Ablöse (Mio. €)"},
                    color_discrete_sequence=["#2b7fff"]
                )
                fig_scatter.update_traces(
                    marker=dict(size=8, opacity=0.85),
                    hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>Alter: %{x}<br>Ablöse: %{y:.2f} Mio. €<br>Position: %{customdata[2]}<br>Saison: %{customdata[3]}<extra></extra>"
                )
                fig_scatter.update_layout(
                    xaxis={"fixedrange": True, "title": "Alter beim Transfer", "dtick": 5}, 
                    yaxis={"fixedrange": True, "title": "Ablöse (Mio. €)"}, 
                    height=420,
                    showlegend=False,
                    margin=dict(l=10, r=10, t=20, b=40)
                )
                st.plotly_chart(fig_scatter, use_container_width=True, config=MOBILE_PLOTLY_CONFIG)

        with tab2:
            df_vol = df_raw.groupby("Manager").agg(
                Gesamtausgaben=("Ablöse_numerisch", lambda x: x.sum() / 1e6),
                Anzahl_Transfers=("Spieler", "count")
            ).reset_index()
            
            fig_vol = px.bar(
                df_vol,
                x="Manager",
                y="Gesamtausgaben",
                text_auto=".1f",
                labels={"Gesamtausgaben": "Ausgaben (Mio. €)"},
                title="Gesamte Transferausgaben pro Manager (Mio. €)",
                color_discrete_sequence=["#004D9E"]
            )
            fig_vol.update_layout(
                xaxis={"type": "category", "tickangle": -45, "fixedrange": True}, 
                yaxis={"fixedrange": True, "title": "Mio. €"}, 
                height=420,
                margin=dict(l=10, r=10, t=40, b=80)
            )
            st.plotly_chart(fig_vol, use_container_width=True, config=MOBILE_PLOTLY_CONFIG)

        with tab3:
            df_age = df_raw.dropna(subset=["Alter_numerisch"]).copy()
            if not df_age.empty:
                df_age["Altersgruppe"] = pd.cut(
                    df_age["Alter_numerisch"], 
                    bins=[0, 20, 25, 29, 100], 
                    labels=["< 21 Jahre", "21–25 Jahre", "26–29 Jahre", "30+ Jahre"]
                )
                
                fig_age = px.histogram(
                    df_age, 
                    x="Manager", 
                    color="Altersgruppe", 
                    barmode="stack",
                    category_orders={"Altersgruppe": ["< 21 Jahre", "21–25 Jahre", "26–29 Jahre", "30+ Jahre"]},
                    color_discrete_map=age_colors,
                    labels={"count": "Anzahl", "Altersgruppe": "Altersgruppe"}
                )
                
                fig_age.update_traces(
                    hovertemplate="<b>%{x}</b><br>Altersgruppe: %{fullData.name}<br>Anzahl: %{y}<extra></extra>"
                )
                fig_age.update_layout(
                    xaxis={"type": "category", "tickangle": -45, "fixedrange": True}, 
                    yaxis={"fixedrange": True, "title": "Anzahl"}, 
                    height=450,
                    legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
                    margin=dict(l=10, r=10, t=20, b=100)
                )
                st.plotly_chart(fig_age, use_container_width=True, config=MOBILE_PLOTLY_CONFIG)

        with tab4:
            if "Position" in df_raw.columns:
                pos_df = df_raw.groupby(["Manager", "Position"]).size().reset_index(name="Anzahl")
                pos_df["Prozent"] = pos_df.groupby("Manager")["Anzahl"].transform(lambda x: (x / x.sum()) * 100)
                
                fig_pos = px.bar(
                    pos_df, 
                    x="Manager", 
                    y="Prozent", 
                    color="Position",
                    text=pos_df["Prozent"].round(1).astype(str) + "%",
                    barmode="stack"
                )
                
                fig_pos.update_traces(textposition="inside")
                fig_pos.update_layout(
                    xaxis={"type": "category", "tickangle": -45, "fixedrange": True}, 
                    yaxis={"fixedrange": True, "title": "Anteil in %"}, 
                    height=480,
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.28,
                        xanchor="center",
                        x=0.5,
                        title=dict(text="")
                    ),
                    margin=dict(l=10, r=10, t=20, b=120)
                )
                st.plotly_chart(fig_pos, use_container_width=True, config=MOBILE_PLOTLY_CONFIG)

    st.divider()

    with st.expander("🛠️ Custom Chart Builder (Eigene Diagramme erstellen)", expanded=False):
        st.markdown("Erstelle hier eigene Visualisierungen unabhängig von den oben gesetzten Filtern.")
        
        df_custom = df_raw.copy()
        
        c1, c2, c3 = st.columns(3)
        available_x = [c for c in ["Manager", "Position", "Transferart", "Saison", "Liga", "Region", "Nationalität"] if c in df_custom.columns]
        x_col = c1.selectbox("X-Achse (Kategorie):", available_x, index=0)
        y_metric = c2.selectbox("Metrik (Y-Achse):", ["Gesamtausgaben (Mio. €)", "Anzahl Transfers", "Ø Ablöse (Mio. €)", "Ø Alter"], index=0)
        chart_type = c3.selectbox("Diagrammtyp:", ["Balkendiagramm", "Kreisdiagramm", "Boxplot (Verteilung)"], index=0)

        st.markdown("**Eigene Filter für dieses Diagramm:**")
        selected_managers_custom = st.multiselect("Manager eingrenzen:", options=sorted(df_custom["Manager"].dropna().unique().tolist()), default=[])
        if selected_managers_custom:
            df_custom = df_custom[df_custom["Manager"].isin(selected_managers_custom)]

        if not df_custom.empty:
            if y_metric == "Gesamtausgaben (Mio. €)":
                df_grp = df_custom.groupby(x_col)["Ablöse_numerisch"].sum().reset_index()
                df_grp["Wert"] = df_grp["Ablöse_numerisch"] / 1e6
                y_label = "Mio. €"
            elif y_metric == "Anzahl Transfers":
                df_grp = df_custom.groupby(x_col)["Spieler"].count().reset_index()
                df_grp.rename(columns={"Spieler": "Wert"}, inplace=True)
                y_label = "Anzahl"
            elif y_metric == "Ø Ablöse (Mio. €)":
                df_grp = df_custom.groupby(x_col)["Ablöse_numerisch"].mean().reset_index()
                df_grp["Wert"] = df_grp["Ablöse_numerisch"] / 1e6
                y_label = "Ø Mio. €"
            elif y_metric == "Ø Alter":
                df_grp = df_custom.groupby(x_col)["Alter_numerisch"].mean().reset_index()
                df_grp.rename(columns={"Alter_numerisch": "Wert"}, inplace=True)
                y_label = "Jahre"

            if chart_type == "Balkendiagramm":
                fig_c = px.bar(df_grp, x=x_col, y="Wert", text_auto=".1f", labels={"Wert": y_label}, title=f"{y_metric} nach {x_col}")
            elif chart_type == "Kreisdiagramm":
                fig_c = px.pie(df_grp, names=x_col, values="Wert", title=f"{y_metric} nach {x_col}")
            elif chart_type == "Boxplot (Verteilung)":
                val_col = "Ablöse_numerisch" if "Ablöse" in y_metric else "Alter_numerisch"
                df_custom["Plot_Wert"] = df_custom[val_col] / (1e6 if "Ablöse" in y_metric else 1)
                fig_c = px.box(df_custom, x=x_col, y="Plot_Wert", title=f"Verteilung von {y_metric} nach {x_col}")

            fig_c.update_layout(
                xaxis={"type": "category", "tickangle": -45, "fixedrange": True}, 
                yaxis={"fixedrange": True}, 
                height=450,
                margin=dict(l=10, r=10, t=40, b=80)
            )
            st.plotly_chart(fig_c, use_container_width=True, config=MOBILE_PLOTLY_CONFIG)

except Exception as e:
    st.error(f"Fehler beim Laden oder Verarbeiten der Daten: {e}")
