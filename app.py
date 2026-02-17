import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. Configurazione Pagina
st.set_page_config(page_title="AnimeAtlas", page_icon="⛩️", layout="wide")

# Inizializzazione navigazione
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# 2. Motore di Caricamento Dati
@st.cache_data(ttl=3600)
def load_all_data():
    oggi = datetime.now().strftime("%Y%m%d")
    ieri = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    date_da_provare = [oggi, ieri]
    urls_fisso = ["https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/airing_anime.csv"]
    templates_data = [
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/anilist_seasonal_{}.csv",
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/anime_seasonal_{}.csv",
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/jikan_seasonal_{}.csv"
    ]
    lista_df = []
    for url in urls_fisso:
        try: lista_df.append(pd.read_csv(url))
        except: continue
    for temp in templates_data:
        for d in date_da_provare:
            try:
                lista_df.append(pd.read_csv(temp.format(d)))
                break
            except: continue
    if not lista_df: return None
    full_df = pd.concat(lista_df, ignore_index=True)
    full_df.columns = [str(c).strip().lower() for c in full_df.columns]
    
    colonne_utili = ['title', 'type', 'episodes', 'status']
    presenti = [c for c in colonne_utili if c in full_df.columns]
    return full_df[presenti].drop_duplicates(subset=['title'])

df = load_all_data()

# --- INTERFACCIA ---

# SCHERMATA INIZIALE (HOME)
if st.session_state.page == 'home':
    # Usiamo st.title e st.subheader invece di HTML per evitare crash
    st.write("") # Spazio vuoto
    st.write("")
    st.title("⛩️ AnimeAtlas")
    st.subheader("Il tuo archivio anime definitivo")
    st.divider() # Una linea elegante per separare
    
    # Pulsanti Centrali
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        if st.button("🏁 CONCLUSI", use_container_width=True, help="Visualizza anime terminati"):
            st.session_state.filter = "Finished Airing"
            st.session_state.page = 'lista'
            st.rerun()
            
    with col_c2:
        if st.button("📡 IN CORSO", use_container_width=True, help="Visualizza anime attualmente in onda"):
            st.session_state.filter = "Currently Airing"
            st.session_state.page = 'lista'
            st.rerun()

# SCHERMATA ELENCO (LISTA)
elif st.session_state.page == 'lista':
    if st.button("⬅️ Torna alla Home"):
        st.session_state.page = 'home'
        st.rerun()
    
    tipo_testo = "IN CORSO" if "Currently" in st.session_state.filter else "CONCLUSI"
    st.title(f"Database: {tipo_testo}")

    # Barra di ricerca e Filtri
    c1, c2, c3 = st.columns([3, 1, 1])
    search = c1.text_input("🔍 Cerca per titolo...")
    f_tipo = c2.selectbox("Tipo:", ["Tutti", "TV", "Movie", "OVA"])
    f_ordine = c3.selectbox("Ordine:", ["A-Z", "Z-A"])

    # Logica Filtro Dati
    mask = df['status'].str.contains(st.session_state.filter, case=False, na=False)
    filtered_df = df[mask]
    
    if search:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search, case=False, na=False)]
    if f_tipo != "Tutti":
        filtered_df = filtered_df[filtered_df['type'].str.contains(f_tipo, case=False, na=False)]
    
    # Ordinamento
    filtered_df = filtered_df.sort_values(by='title', ascending=(f_ordine == "A-Z"))

    # Tabella
    st.divider()
    display_df = filtered_df[['title', 'type', 'episodes']].copy()
    display_df.columns = ['Titolo Anime', 'Tipologia', 'Episodi']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.caption(f"Trovati {len(filtered_df)} titoli")
