import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Anime Complete Database", page_icon="⛩️", layout="wide")

st.title("⛩️ Database Completo (Auto-Aggiornante)")

@st.cache_data(ttl=3600)
def load_data_from_repo():
    # 1. Otteniamo la data di oggi e ieri nel formato YYYYMMDD
    oggi = datetime.now().strftime("%Y%m%d")
    ieri = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    
    date_da_provare = [oggi, ieri]
    
    # 2. Proviamo a caricare i diversi file stagionali che vediamo negli screenshot
    for data_str in date_da_provare:
        # Proviamo il file AniList Seasonal (il più completo)
        url = f"https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/anilist_seasonal_{data_str}.csv"
        try:
            df = pd.read_csv(url)
            return df, data_str, "AniList"
        except:
            # Se fallisce, proviamo quello di Jikan
            url_jikan = f"https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/jikan_seasonal_{data_str}.csv"
            try:
                df = pd.read_csv(url_jikan)
                return df, data_str, "Jikan"
            except:
                continue
                
    return None, None, None

# Esecuzione del caricamento
df, data_f, fonte = load_data_from_repo()

if df is not None:
    st.success(f"✅ Dati caricati! Fonte: {fonte} | Data: {data_f}")
    
    # Pulizia colonne
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    # Filtri
    st.sidebar.header("🔍 Ricerca")
    search = st.sidebar.text_input("Inserisci il nome di un anime:", "")
    
    # Identificazione colonna titolo
    col_titolo = 'title' if 'title' in df.columns else df.columns[0]
    
    df_filtered = df[df[col_titolo].astype(str).str.contains(search, case=False, na=False)]
    
    # Visualizzazione Metriche
    c1, c2 = st.columns(2)
    c1.metric("Totale Database", len(df))
    c2.metric("Risultati Ricerca", len(df_filtered))
    
    # Tabella
    st.dataframe(df_filtered, use_container_width=True)
else:
    st.error("❌ Errore nel caricamento dei dati stagionali.")
    st.info("I file nel repository di Leo potrebbero essere in fase di aggiornamento. Riprova tra pochi minuti.")
