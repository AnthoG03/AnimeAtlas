import streamlit as st
import pandas as pd

st.set_page_config(page_title="AnimeAtlas", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'home'

@st.cache_data(ttl=3600)
def load_data():
    u = "https://raw.githubusercontent.com/LeoRigasaki/Anime-dataset/main/data/raw/airing_anime.csv"
    try:
        return pd.read_csv(u)
    except:
        return None

df = load_data()

if st.session_state.page == 'home':
    st.title("AnimeAtlas")
    st.write("Benvenuto nell'archivio")
    if st.button("ENTRA NELL'ARCHIVIO"):
        st.session_state.page = 'lista'
        st.rerun()

elif st.session_state.page == 'lista':
    if st.button("Torna indietro"):
        st.session_state.page = 'home'
        st.rerun()
    st.title("Lista Anime")
    if df is not None:
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Errore caricamento")
