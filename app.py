import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Anime Mega Explorer", layout="wide")

st.title("⛩️ Anime Mega Database")
st.write("Unione dei 4 database di LeoRigasaki (Airing + Seasonal)")

@st.cache_data(ttl=3600)
def load_all_data():
    oggi = datetime.now().strftime("%Y%m%d")
    ieri = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    date_da_provare = [oggi, ieri]
    
    # 1. Link fisso
    urls_fisso = [
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/airing_anime.csv"
    ]
    
    # 2. Template per i link con data
    templates_data = [
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/anilist_seasonal_{}.csv",
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/anime_seasonal_{}.csv",
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/jikan_seasonal_{}.csv"
    ]
    
    lista_df = []
    
    # Carichiamo il file fisso
    for url in urls_fisso:
        try:
            df_temp = pd.read_csv(url)
            lista_df.append(df_temp)
        except:
            continue
            
    # Carichiamo i file con data (prova oggi, se fallisce prova ieri)
    for temp in templates_data:
        caricato = False
        for d in date_da_provare:
            if caricato: break
            try:
                url_dinamico = temp.format(d)
                df_temp = pd.read_csv(url_dinamico)
                lista_df.append(df_temp)
                caricato = True
            except:
                continue
                
    if not lista_df:
        return None
        
    # Unione di tutti i file trovati
    full_df = pd.concat(lista_df, ignore_index=True)
    
    # Pulizia standard
    full_df.columns = [str(c).strip().lower() for c in full_df.columns]
    if 'title' in full_df.columns:
        full_df = full_df.drop_duplicates(subset=['title'])
    elif 'name' in full_df.columns:
        full_df = full_df.drop_duplicates(subset=['name'])
        
    return full_df

# Esecuzione
df = load_all_data()

if df is not None:
    st.sidebar.header("🔍 Filtri")
    search = st.sidebar.text_input("Cerca titolo:", "")
    
    # Identifica colonna titolo
    col_titolo = 'title' if 'title' in df.columns else (df.columns[0] if len(df.columns)>0 else None)
    
    if col_titolo:
        df_filtered = df[df[col_titolo].astype(str).str.contains(search, case=False, na=False)]
    else:
        df_filtered = df

    # Metriche e Tabella
    st.success(f"Database pronto! Abbiamo unito i file disponibili.")
    st.metric("Totale Anime trovati", len(df_filtered))
    st.dataframe(df_filtered, use_container_width=True)
else:
    st.error("⚠️ Non sono riuscito a recuperare nessuno dei 4 file. Controlla i permessi del repository.")
