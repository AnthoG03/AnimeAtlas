import streamlit as st
import pandas as pd

# Configurazione base
st.set_page_config(page_title="Anime Explorer", layout="wide")

st.title("⛩️ Anime Database Explorer")

# Funzione per caricare i dati
@st.cache_data(ttl=3600)
def load_data():
    url = "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/anime_data.csv"
    try:
        data = pd.read_csv(url)
        # Convertiamo i voti in numeri (se possibile)
        if 'score' in data.columns:
            data['score'] = pd.to_numeric(data['score'], errors='coerce').fillna(0)
        return data
    except:
        return None

df = load_data()

if df is not None:
    # Barra laterale
    st.sidebar.header("Filtri")
    search = st.sidebar.text_input("Cerca titolo:", "")
    
    # Filtro punteggio
    voto = st.sidebar.slider("Voto minimo:", 0.0, 10.0, 6.0)

    # Applichiamo i filtri
    # (Controlliamo che le colonne esistano davvero nel CSV)
    df_filtered = df[df['title'].str.contains(search, case=False, na=False)]
    df_filtered = df_filtered[df_filtered['score'] >= voto]

    # Visualizzazione
    st.metric("Titoli trovati", len(df_filtered))
    
    # Mostriamo la tabella
    st.dataframe(df_filtered, use_container_width=True)
else:
    st.error("Impossibile caricare i dati. Controlla il link al CSV.")
