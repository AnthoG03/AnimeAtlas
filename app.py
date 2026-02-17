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
    if 'title' in full_df.columns:
        full_df = full_df.drop_duplicates(subset=['title'])
    return full_df

df = load_all_data()

# --- INTERFACCIA ---

if st.session_state.page == 'home':
    st.write("#")
    c_title1, c_title2, c_title3 = st.columns([1, 3, 1])
    with c_title2:
        st.title("⛩️ AnimeAtlas")
        st.markdown("### *Il tuo portale definitivo verso migliaia di storie.*")
        st.write(f"Database: **{len(df) if df is not None else 0}** titoli.")
    
    st.write("#")
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        with st.container(border=True):
            st.write("### 📚 Archivio Completo")
            st.write("Tutti gli anime (Conclusi e storici).")
            if st.button("ACCEDI ALL'ARCHIVIO", use_container_width=True, type="primary"):
                st.session_state.filter = "all" # Imposta filtro su tutto
                st.session_state.page = 'lista'
                st.rerun()
            
    with col_c2:
        with st.container(border=True):
            st.write("### 📡 In Corso")
            st.write("Solo gli anime attualmente in onda.")
            if st.button("VEDI I SIMULCAST", use_container_width=True, type="primary"):
                st.session_state.filter = "airing" # Imposta filtro su in corso
                st.session_state.page = 'lista'
                st.rerun()

elif st.session_state.page == 'lista':
    if st.button("⬅️ Torna alla Home"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.divider()

    # --- LOGICA DI FILTRAGGIO REALE ---
    display_df = df.copy()
    
    if st.session_state.filter == "airing":
        # Cerchiamo la parola 'airing' (ignorando maiuscole/minuscole) nella colonna status
        if 'status' in display_df.columns:
            display_df = display_df[display_df['status'].str.contains('Currently Airing|Airing', case=False, na=False)]
        st.title("📡 Anime In Corso")
    else:
        st.title("📚 Archivio Completo")

    # Ricerca e Ordinamento
    row1_c1, row1_c2 = st.columns([3, 1])
    search = row1_c1.text_input("Cerca anime...", placeholder="Es. Bleach...")
    f_ordine = row1_c2.selectbox("Ordine:", ["A-Z", "Z-A"])

    if search:
        col_t = 'title' if 'title' in display_df.columns else display_df.columns[0]
        display_df = display_df[display_df[col_t].astype(str).str.contains(search, case=False, na=False)]
    
    display_df = display_df.sort_values(by=display_df.columns[0], ascending=(f_ordine == "A-Z"))

    # Tabella
    cols_to_show = [c for c in ['title', 'type', 'episodes'] if c in display_df.columns]
    final_table = display_df[cols_to_show]
    final_table.columns = [c.upper() for c in cols_to_show]
    
    st.dataframe(final_table, use_container_width=True, hide_index=True)
    st.caption(f"Risultati: {len(final_table)}")
