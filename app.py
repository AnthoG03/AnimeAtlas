import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. Configurazione Pagina
st.set_page_config(page_title="AnimeAtlas", page_icon="⛩️", layout="wide")

# --- TRUCCO HTML/CSS SICURO ---
# Questo blocco fuori dagli "if" non farà mai crashare il sito
st.markdown("""
    <style>
    /* Sfondo scuro e font pulito */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    /* Titolo AnimeAtlas */
    .main-title {
        font-family: 'Arial Black', sans-serif;
        font-size: 100px !important;
        color: #FF4B4B;
        text-align: center;
        text-shadow: 3px 3px 10px rgba(255, 75, 75, 0.5);
        margin-bottom: 0px;
    }
    /* Sottotitolo */
    .sub-title {
        text-align: center;
        font-size: 20px;
        color: #808495;
        margin-bottom: 50px;
    }
    /* Pulsanti personalizzati */
    div.stButton > button {
        background-color: #1f2937;
        color: white;
        border: 2px solid #FF4B4B;
        border-radius: 10px;
        height: 80px;
        font-size: 20px !important;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #FF4B4B;
        color: white;
        box-shadow: 0px 0px 15px #FF4B4B;
    }
    </style>
    """, unsafe_allow_code=True)

# 2. Il resto del codice (Logica Navigazione)
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# (Qui carichiamo i dati - stessa funzione di prima)
@st.cache_data(ttl=3600)
def load_all_data():
    # ... logicamente identico a quello che funziona ...
    urls = ["https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/airing_anime.csv",
            "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/anilist_anime_data.csv",
            "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/jikan_anime_data.csv"]
    templates = ["https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/anilist_seasonal_{}.csv",
                 "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/anime_seasonal_{}.csv"]
    oggi, ieri = datetime.now().strftime("%Y%m%d"), (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    lista_df = []
    for u in urls:
        try: lista_df.append(pd.read_csv(u, on_bad_lines='skip'))
        except: continue
    for t in templates:
        for d in [oggi, ieri]:
            try:
                lista_df.append(pd.read_csv(t.format(d), on_bad_lines='skip'))
                break
            except: continue
    full_df = pd.concat(lista_df, ignore_index=True)
    full_df.columns = [str(c).strip().lower() for c in full_df.columns]
    return full_df.drop_duplicates(subset=['title']) if 'title' in full_df.columns else full_df

df = load_all_data()

# --- RENDERING PAGINE ---

if st.session_state.page == 'home':
    # Usiamo le classi CSS che abbiamo creato sopra
    st.markdown('<p class="main-title">AnimeAtlas</p>', unsafe_allow_code=True)
    st.markdown('<p class="sub-title">IL TUO ARCHIVIO ANIME DEFINITIVO</p>', unsafe_allow_code=True)
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if st.button("🏁 ARCHIVIO COMPLETO", use_container_width=True):
            st.session_state.filter, st.session_state.page = "all", 'lista'
            st.rerun()
    with col_c2:
        if st.button("📡 IN CORSO", use_container_width=True):
            st.session_state.filter, st.session_state.page = "airing", 'lista'
            st.rerun()
    
    st.markdown(f"<p style='text-align:center; margin-top:50px; color:#444;'>Titoli caricati: {len(df)}</p>", unsafe_allow_code=True)

elif st.session_state.page == 'lista':
    if st.button("⬅️ TORNA ALLA HOME"):
        st.session_state.page = 'home'
        st.rerun()
    
    # (Tutta la logica della lista rimane uguale, ma sarà più bella grazie al CSS globale)
    st.title("Esplora i Titoli")
    search = st.text_input("🔍 Cerca per titolo...")
    
    display_df = df
    if st.session_state.filter == "airing" and 'status' in df.columns:
        display_df = df[df['status'].str.contains('airing', case=False, na=False)]
    
    if search:
        col_t = 'title' if 'title' in display_df.columns else display_df.columns[0]
        display_df = display_df[display_df[col_t].astype(str).str.contains(search, case=False, na=False)]
    
    # Selezione colonne e visualizzazione
    cols = [c for c in ['title', 'type', 'episodes'] if c in display_df.columns]
    st.dataframe(display_df[cols], use_container_width=True, hide_index=True)
