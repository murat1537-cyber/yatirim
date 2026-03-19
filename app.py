import streamlit as st
import pandas as pd
import yfinance as yf

# Configuratie
st.set_page_config(page_title="AI Investerings Dashboard", layout="wide")
st.title("📊 Investeringshulp met Historische Analyse")

# --- STAP 1: Gebruikersinput ---
with st.sidebar:
    st.header("Instellingen")
    budget = st.number_input("Budget (€)", min_value=50, value=1000)
    risico = st.select_slider("Risicoprofiel", options=["Laag", "Gemiddeld", "Hoog"])
    
    st.divider()
    # Keuze voor de grafiek
    tickers_dict = {
        "Aandelen (S&P 500)": "^GSPC",
        "Goud": "GC=F",
        "Bitcoin": "BTC-USD"
    }
    gekozen_ticker = st.selectbox("Bekijk historische trend van:", list(tickers_dict.keys()))

# --- STAP 2: Functies voor Data ---
@st.cache_data(ttl=3600)
def haal_koersen_en_historie(tickers):
    prijzen = {}
    historie_data = {}
    for naam, symbool in tickers.items():
        ticker_obj = yf.Ticker(symbool)
        # Haal data van het laatste jaar op
        hist = ticker_obj.history(period="1y")
        prijzen[naam] = hist['Close'].iloc[-1]
        historie_data[naam] = hist['Close']
    return prijzen, historie_data

live_prijzen, jaar_historie = haal_koersen_en_historie(tickers_dict)

# --- STAP 3: Hoofdoverzicht ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Portefeuille Advies")
    # Verdelingslogica (zelfde als voorheen)
    verdeling = {"Laag": {"Goud": 0.6, "Aandelen (S&P 500)": 0.3, "Bitcoin": 0.1},
                 "Gemiddeld": {"Goud": 0.3, "Aandelen (S&P 500)": 0.5, "Bitcoin": 0.2},
                 "Hoog": {"Goud": 0.1, "Aandelen (S&P 500)": 0.4, "Bitcoin": 0.5}}[risico]
    
    advies_lijst = []
    for item, perc in verdeling.items():
        bedrag = budget * perc
        advies_lijst.append([item, f"{perc*100}%", f"€{bedrag:.2f}", round(bedrag/live_prijzen[item], 4)])
    
    df_advies = pd.DataFrame(advies_lijst, columns=["Activa", "%", "Bedrag", "Aantal"])
    st.table(df_advies)

with col2:
    st.subheader(f"Trend: {gekozen_ticker}")
    # Toon de grafiek van de gekozen ticker
    st.line_chart(jaar_historie[gekozen_ticker])

st.success("De data wordt automatisch ververst met de nieuwste beurskoersen.")
