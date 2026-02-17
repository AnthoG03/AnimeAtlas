import streamlit as st
import pandas as pd

# Impostazione pagina semplice
st.set_page_config(page_title="Anime Mega Database", layout="wide")

st.title("⛩️ Anime Mega Explorer")
st.write("Caricamento dell'archivio completo...")

@st.cache_data(ttl=3600)
def load_mega_data():
    # Puntiamo ai file master che contengono tutto l'archivio
    urls = [
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/anilist_anime_data.csv",
        "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/jikan_anime_data.csv"
    ]
    
    lista_df = []
    for url in urls:
        try:
            # Carichiamo il file
            temp_df = pd.read_csv(url, on_bad_lines='skip')
            lista_df.append(temp_df)
        except:
            continue
            
    if not lista_df:
        return None
    
    # Uniamo i file
    full_df = pd.concat(lista_df, ignore_index=True)
    
    # Pulizia nomi colonne: tutto minuscolo e senza spazi
    full_df.columns = [str(c).strip().lower() for c in full_df.columns]
    
    # Rimuoviamo i duplicati basandoci sul titolo
    if 'title' in full_df.columns:
        full_df = full_df.drop_duplicates(subset=['title'])
    
    return full_df

# Esecuzione
df = load_mega_data()

if df is not None:
    # Barra laterale semplice
    st.sidebar.header("Filtri")
    search = st.sidebar.text_input("Cerca anime (es. Dragon Ball):", "")

    # Cerchiamo la colonna del titolo
    col_titolo = 'title' if 'title' in df.columns else df.columns[0]
    
    # Applichiamo la ricerca
    df_filtered = df[df[col_titolo].astype(str).str.contains(search, case=False, na=False)]

    # Filtro Voto se presente
    if 'score' in df.columns:
        df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)
        voto = st.sidebar.slider("Voto minimo:", 0.0, 10.0, 0.0)
        df_filtered = df_filtered[df_filtered['score'] >= voto]

    # Metriche
    st.success(f"Database caricato con successo!")
    st.metric("Totale Titoli", len(df_filtered))
    
    # Tabella
    st.dataframe(df_filtered, use_container_width=True)
else:
    st.error("Errore nel caricamento. Controlla che i file nel repository siano accessibili.")
