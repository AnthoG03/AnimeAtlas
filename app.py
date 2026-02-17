import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. Configurazione Pagina
st.set_page_config(page_title="AnimeAtlas", page_icon="⛩️", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'filter' not in st.session_state:
    st.session_state.filter = 'all'

# 2. Motore di Caricamento
@st.cache_data(ttl=3600)
def load_all_data():
    urls = [
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/airing_anime.csv",
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/anilist_anime_data.csv",
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/jikan_anime_data.csv"
    ]
    templates_data = [
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/anilist_seasonal_{}.csv",
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/anime_seasonal_{}.csv"
    ]
    oggi, ieri = datetime.now().strftime("%Y%m%d"), (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    lista_df = []
    for url in urls:
        try: lista_df.append(pd.read_csv(url, on_bad_lines='skip'))
        except: continue
    for temp in templates_data:
        for d in [oggi, ieri]:
            try:
                lista_df.append(pd.read_csv(temp.format(d), on_bad_lines='skip'))
                break
            except: continue
    if not lista_df: return None
    full_df = pd.concat(lista_df, ignore_index=True)
    full_df.columns = [str(c).strip().lower() for c in full_df.columns]
    
    # Pulizia duplicati
    if 'title' in full_df.columns:
        full_df = full_df.drop_duplicates(subset=['title'])
    return full_df

df = load_all_data()

# --- INTERFACCIA ---

if st.session_state.page == 'home':
    st.write("#")
    st.title("⛩️ AnimeAtlas")
    st.markdown("### *Il tuo portale definitivo verso migliaia di storie.*")
    st.write(f"Database totale: **{len(df) if df is not None else 0}** titoli.")
    
    st.write("#")
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        with st.container(border=True):
            st.write("### 📚 Archivio Completo")
            if st.button("ACCEDI ALL'ARCHIVIO", use_container_width=True, type="primary"):
                st.session_state.filter = "all"
                st.session_state.page = 'lista'
                st.rerun()
            
    with col_c2:
        with st.container(border=True):
            st.write("### 📡 In Corso")
            if st.button("VEDI I SIMULCAST", use_container_width=True, type="primary"):
                st.session_state.filter = "airing"
                st.session_state.page = 'lista'
                st.rerun()

elif st.session_state.page == 'lista':
    if st.button("⬅️ Torna alla Home"):
        st.session_state.page = 'home'
        st.rerun()
    
    # FILTRAGGIO MANUALE
    if st.session_state.filter == "airing":
        st.title("📡 Anime In Corso")
        # Cerchiamo di capire che colonne abbiamo
        if 'status' in df.columns:
            # Filtro ultra-elastico: prende tutto ciò che NON è "Finished" o "Completed"
            # Spesso è più facile escludere i finiti che trovare quelli in corso
            non_finiti = df[~df['status'].astype(str).str.contains('Finished|Completed|Finished Airing', case=False, na=False)]
            # Di questi, prendiamo quelli che danno idea di essere attivi
            display_df = non_finiti[non_finiti['status'].astype(str).str.contains('Airing|Ongoing|Releasing|Currently', case=False, na=False)]
        else:
            display_df = df.head(100) # Se non c'è la colonna, limitiamo per non mostrare 22k
    else:
        st.title("📚 Archivio Completo")
        display_df = df

    # Ricerca
    search = st.text_input("🔍 Cerca un titolo...")
    if search:
        col_t = 'title' if 'title' in display_df.columns else display_df.columns[0]
        display_df = display_df[display_df[col_t].astype(str).str.contains(search, case=False, na=False)]

    # Tabella finale
    cols = [c for c in ['title', 'type', 'episodes'] if c in display_df.columns]
    st.dataframe(display_df[cols], use_container_width=True, hide_index=True)
    st.write(f"Risultati filtrati: {len(display_df)}")
