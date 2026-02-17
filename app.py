import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Anime Database Dinamico", layout="wide")
st.title("⛩️ Database Completo (Auto-Aggiornante)")

@st.cache_data(ttl=3600)
def load_smart_data():
    # 1. Calcoliamo la data di oggi nel formato usato dal repo (YYYYMMDD)
    oggi = datetime.now().strftime("%Y%m%d")
    ieri = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    
    # Proviamo prima il file di oggi, poi quello di ieri come backup
    date_da_provare = [oggi, ieri]
    
    for data_str in date_da_provare:
        # Costruiamo il link con la data dinamica
        url = f"https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/anilist_anime_data_{data_str}.csv"
        try:
            df = pd.read_csv(url)
            return df, data_str # Ritorna i dati e la data trovata
        except:
            continue # Se fallisce, prova la data successiva
            
    return None, None

df, data_trovata = load_smart_data()

if df is not None:
    st.success(f"✅ Dati caricati con successo! Versione del: {data_trovata}")
    
    # --- RICERCA E FILTRI ---
    st.sidebar.header("Strumenti di ricerca")
    
    # Pulizia nomi colonne
    df.columns = [c.strip().lower() for c in df.columns]
    
    search = st.sidebar.text_input("Cerca un titolo (es. Blue Lock, Bleach):", "")
    
    # Filtro dinamico
    col_titolo = 'title' if 'title' in df.columns else df.columns[0]
    df_filtered = df[df[col_titolo].astype(str).str.contains(search, case=False, na=False)]

    # Layout metriche
    c1, c2 = st.columns(2)
    c1.metric("Titoli totali", len(df))
    c2.metric("Titoli trovati", len(df_filtered))

    # Visualizzazione
    st.dataframe(df_filtered, use_container_width=True)
else:
    st.error("❌ Impossibile trovare i file aggiornati. Potrebbe esserci un ritardo nell'aggiornamento del repository originale.")
    st.info("Prova a controllare il nome del file nella cartella 'raw' di LeoRigasaki.")
