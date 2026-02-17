import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. Configurazione Pagina
st.set_page_config(page_title="AnimeAtlas", page_icon="⛩️", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# 2. Motore di Caricamento (Il tuo codice collaudato)
@st.cache_data(ttl=3600)
def load_all_data():
    oggi = datetime.now().strftime("%Y%m%d")
    ieri = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    date_da_provare = [oggi, ieri]
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
    for url in urls:
        try: lista_df.append(pd.read_csv(url, on_bad_lines='skip'))
        except: continue
    for temp in templates_data:
        for d in date_da_provare:
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
    # Spaziatura iniziale
    st.write("#")
    
    # Area Titolo Centrale
    c_title1, c_title2, c_title3 = st.columns([1, 3, 1])
    with c_title2:
        st.title("⛩️ AnimeAtlas")
        st.markdown("### *Il tuo portale definitivo verso migliaia di storie.*")
        st.write(f"Database sincronizzato con successo: **{len(df) if df is not None else 0}** titoli.")
    
    st.write("#") # Altro spazio
    
    # Pulsanti di Navigazione
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        with st.container(border=True): # Crea una cornice intorno al pulsante
            st.write("### 📚 Archivio Storico")
            st.write("Esplora l'intero database globale.")
            if st.button("ACCEDI ALL'ARCHIVIO", use_container_width=True, type="primary"):
                st.session_state.filter = "all"
                st.session_state.page = 'lista'
                st.rerun()
            
    with col_c2:
        with st.container(border=True):
            st.write("### 📡 Simulcast")
            st.write("Scopri gli anime in onda ora.")
            if st.button("GUARDA COSA C'È IN CORSO", use_container_width=True, type="primary"):
                st.session_state.filter = "airing"
                st.session_state.page = 'lista'
                st.rerun()

elif st.session_state.page == 'lista':
    # Barra superiore di navigazione
    top_c1, top_c2 = st.columns([1, 4])
    with top_c1:
        if st.button("⬅️ Torna alla Home", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
    
    st.divider()

    # Filtriamo in base alla scelta
    if st.session_state.filter == "airing":
        if 'status' in df.columns:
            display_df = df[df['status'].str.contains('airing', case=False, na=False)]
        else:
            display_df = df.head(1000)
    else:
        display_df = df

    # Filtri di Ricerca
    st.title("🔍 Esplora i titoli")
    row1_c1, row1_c2, row1_c3 = st.columns([3, 1, 1])
    
    search = row1_c1.text_input("Cerca anime...", placeholder="Es. Bleach, One Piece...")
    f_tipo = row1_c2.selectbox("Tipo:", ["Tutti", "TV", "Movie", "OVA"])
    f_ordine = row1_c3.selectbox("Ordine:", ["A-Z", "Z-A"])

    # Logica Filtri
    if search:
        col_t = 'title' if 'title' in display_df.columns else display_df.columns[0]
        display_df = display_df[display_df[col_t].astype(str).str.contains(search, case=False, na=False)]
    
    if f_tipo != "Tutti":
        display_df = display_df[display_df['type'].str.contains(f_tipo, case=False, na=False)]
    
    display_df = display_df.sort_values(by=display_df.columns[0], ascending=(f_ordine == "A-Z"))

    # Tabella
    st.write("#")
    cols_to_show = []
    for c in ['title', 'type', 'episodes']:
        if c in display_df.columns: cols_to_show.append(c)
    
    final_table = display_df[cols_to_show]
    final_table.columns = [c.upper() for c in cols_to_show]
    
    # Visualizzazione moderna
    st.dataframe(
        final_table, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "TITLE": "Titolo dell'Opera",
            "TYPE": "Formato",
            "EPISODES": st.column_config.NumberColumn("N° Episodi", format="%d")
        }
    )
    st.caption(f"Risultati trovati: {len(final_table)}")
