import streamlit as st
import pandas as pd

# 1. Configurazione estetica
st.set_page_config(page_title="Anime Mega Database", page_icon="🚀", layout="wide")

# Un po' di stile per non renderlo troppo "base"
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stDataFrame { border: 2px solid #ff4b4b; border-radius: 10px; }
    </style>
    """, unsafe_allow_code=True)

st.title("⛩️ Anime Mega Explorer")
st.write("Unione di tutti i database di LeoRigasaki (AniList + MyAnimeList)")

@st.cache_data(ttl=3600)
def load_mega_data():
    # Lista dei file principali per avere TUTTO l'archivio
    # Questi sono i file "master" che contengono migliaia di titoli
    urls = [
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/anilist_anime_data.csv",
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/jikan_anime_data.csv"
    ]
    
    lista_df = []
    for url in urls:
        try:
            temp_df = pd.read_csv(url)
            lista_df.append(temp_df)
        except:
            continue
            
    if not lista_df:
        return None
    
    # Uniamo i file e togliamo i duplicati
    full_df = pd.concat(lista_df, ignore_index=True)
    
    # Pulizia nomi colonne
    full_df.columns = [str(c).strip().lower() for c in full_df.columns]
    
    # Rimuoviamo i doppioni basandoci sul titolo
    if 'title' in full_df.columns:
        full_df = full_df.drop_duplicates(subset=['title'])
    
    return full_df

df = load_mega_data()

if df is not None:
    # --- SIDEBAR ---
    st.sidebar.header("🔍 Cerca nel Database")
    search = st.sidebar.text_input("Inserisci titolo (es. Naruto, Death Note):", "")
    
    # Filtro Voto (se esiste la colonna score)
    if 'score' in df.columns:
        df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)
        voto_min = st.sidebar.slider("Filtra per voto minimo:", 0.0, 10.0, 0.0)
        df = df[df['score'] >= voto_min]

    # --- FILTRO RICERCA ---
    col_titolo = 'title' if 'title' in df.columns else df.columns[0]
    df_filtered = df[df[col_titolo].astype(str).str.contains(search, case=False, na=False)]

    # --- CONTATORI ---
    c1, c2 = st.columns(2)
    with c1:
        st.metric("📦 Totale Titoli Caricati", len(df))
    with c2:
        st.metric("🎯 Risultati Trovati", len(df_filtered))

    # --- TABELLA ---
    st.dataframe(df_filtered, use_container_width=True)
    
    st.info(f"💡 Consiglio: Abbiamo unito più file per darti l'archivio completo. Se cerchi un classico, ora dovresti trovarlo!")
else:
    st.error("⚠️ Non sono riuscito a caricare i database principali. Il repository potrebbe aver cambiato struttura.")
