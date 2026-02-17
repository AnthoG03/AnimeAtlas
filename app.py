import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. Configurazione Pagina
st.set_page_config(page_title="AnimeAtlas", page_icon="⛩️", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# 2. Motore di Caricamento - CARICA TUTTO SENZA ESCLUSIONI
@st.cache_data(ttl=3600)
def load_all_data():
    oggi = datetime.now().strftime("%Y%m%d")
    ieri = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    date_da_provare = [oggi, ieri]
    
    # Lista link Master (quelli grossi) e Seasonal
    urls = [
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/airing_anime.csv",
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/anilist_anime_data.csv",
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/jikan_anime_data.csv"
    ]
    
    templates_data = [
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/anilist_seasonal_{}.csv",
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/anime_seasonal_{}.csv"
    ]
    
    lista_df = []
    # Carichiamo i fissi
    for url in urls:
        try: lista_df.append(pd.read_csv(url, on_bad_lines='skip'))
        except: continue
    
    # Carichiamo i stagionali con data
    for temp in templates_data:
        for d in date_da_provare:
            try:
                lista_df.append(pd.read_csv(temp.format(d), on_bad_lines='skip'))
                break
            except: continue
            
    if not lista_df: return None
    
    full_df = pd.concat(lista_df, ignore_index=True)
    full_df.columns = [str(c).strip().lower() for c in full_df.columns]
    
    # Pulizia minima per non perdere pezzi
    if 'title' in full_df.columns:
        full_df = full_df.drop_duplicates(subset=['title'])
    
    return full_df

df = load_all_data()

# --- INTERFACCIA ---

if st.session_state.page == 'home':
    st.write("")
    st.title("⛩️ AnimeAtlas")
    st.subheader("Il tuo archivio anime definitivo")
    st.write(f"Database attuale: {len(df) if df is not None else 0} titoli")
    st.divider()
    
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        if st.button("🏁 ARCHIVIO COMPLETO", use_container_width=True):
            st.session_state.filter = "all"
            st.session_state.page = 'lista'
            st.rerun()
            
    with col_c2:
        if st.button("📡 IN CORSO (Season)", use_container_width=True):
            st.session_state.filter = "airing"
            st.session_state.page = 'lista'
            st.rerun()

elif st.session_state.page == 'lista':
    if st.button("⬅️ Torna alla Home"):
        st.session_state.page = 'home'
        st.rerun()
    
    # Filtriamo in base alla scelta
    if st.session_state.filter == "airing":
        # Filtro morbido: cerchiamo la parola 'airing' nello status
        if 'status' in df.columns:
            display_df = df[df['status'].str.contains('airing', case=False, na=False)]
        else:
            display_df = df.head(1000) # Fallback
    else:
        display_df = df

    st.title("Esplora i Titoli")

    # Ricerca e Ordinamento
    c1, c2 = st.columns([3, 1])
    search = c1.text_input("🔍 Cerca per titolo...")
    f_ordine = c2.selectbox("Ordine:", ["A-Z", "Z-A"])

    if search:
        col_t = 'title' if 'title' in display_df.columns else display_df.columns[0]
        display_df = display_df[display_df[col_t].astype(str).str.contains(search, case=False, na=False)]
    
    display_df = display_df.sort_values(by=display_df.columns[0], ascending=(f_ordine == "A-Z"))

    st.divider()
    
    # Selezioniamo solo le colonne che vuoi tu (se esistono)
    cols_to_show = []
    for c in ['title', 'type', 'episodes']:
        if c in display_df.columns: cols_to_show.append(c)
    
    final_table = display_df[cols_to_show]
    final_table.columns = [c.capitalize() for c in cols_to_show]
    
    st.dataframe(final_table, use_container_width=True, hide_index=True)
    st.caption(f"Visualizzando {len(final_table)} titoli")
