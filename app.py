import streamlit as st
import pandas as pd

# 1. Configurazione della pagina
st.set_page_config(page_title="Anime Live Explorer", page_icon="⛩️", layout="wide")

# 2. Stile estetico (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_code=True)

# 3. Funzione per caricare i dati dal GitHub di LeoRigasaki
@st.cache_data(ttl=3600) # Aggiorna i dati ogni ora
def load_data():
    # URL del file CSV (formato RAW per poterlo leggere)
    url = "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/anime_data.csv"
    try:
        data = pd.read_csv(url)
        # Pulizia base dei dati
        if 'score' in data.columns:
            data['score'] = pd.to_numeric(data['score'], errors='coerce').fillna(0)
        return data
    except Exception as e:
        return None

# Carichiamo i dati
df = load_data()

# 4. Interfaccia del Sito
st.title("⛩️ Anime Database Explorer")
st.write("Questo sito si collega direttamente al dataset di **LeoRigasaki** e si aggiorna automaticamente.")

if df is not None:
    # --- BARRA LATERALE PER FILTRARE ---
    st.sidebar.header("Filtra i Risultati")
    
    # Cerca per nome
    search_query = st.sidebar.text_input("Cerca titolo:", "")

    # Filtro per Stato (Concluso, In corso, ecc.)
    if 'status' in df.columns:
        stati = df['status'].unique().tolist()
        stati_scelti = st.sidebar.multiselect("Stato dell'anime:", stati, default=stati)
    else:
        stati_scelti = []

    # Filtro per Punteggio
    voto_min = st.sidebar.slider("Punteggio minimo:", 0.0, 10.0, 7.0)

    # --- APPLICAZIONE FILTRI ---
    mask = (df['title'].str.contains(search_query, case=False, na=False)) & \
           (df['status'].isin(stati_scelti)) & \
           (df['score'] >= voto_min)
    
    df_filtrato = df[mask]

    # --- VISUALIZZAZIONE DATI ---
    # Metriche veloci
    c1, c2, c3 = st.columns(3)
    c1.metric("Titoli nel database", len(df))
    c2.metric("Risultati trovati", len(df_filtrato))
    c3.metric("Punteggio Medio", round(df_filtrato['score'].mean(), 2) if not df_filtrato.empty else 0)

    st.divider()

    # Tabella principale
    st.subheader("Lista Anime")
    # Mostriamo solo le colonne più importanti per non creare confusione
    colonne_da_mostrare = ['title', 'status', 'score', 'episodes', 'genres']
    colonne_effettive = [c for c in colonne_da_mostrare if c in df_filtrato.columns]
    
    st.dataframe(df_filtrato[colonne_effettive], use_container_width=True)

    # Grafico a barre degli stati
    st.subheader("Statistiche stato anime filtrati")
    st.bar_chart(df_filtrato['status'].value_counts())

else:
    st.error("Errore: Non è stato possibile recuperare il file CSV dal repository. Controlla il link o riprova più tardi.")

st.info("💡 Consiglio: Clicca sulle intestazioni della tabella per ordinare gli anime per voto o per nome!")
