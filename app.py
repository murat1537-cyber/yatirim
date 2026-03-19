import streamlit as st
import pandas as pd
import yfinance as yf

# Configuratie
st.set_page_config(page_title="TR Investerings Dashboard", layout="wide")
st.title("🇹🇷 AI Yatırım Asistanı (TRY Bazlı)")

# --- STAP 1: Gebruikersinput ---
with st.sidebar:
    st.header("Ayarlar (Instellingen)")
    budget_try = st.number_input("Toplam Bütçe (TRY)", min_value=500, value=10000, step=500)
    risico = st.select_slider("Risk Profili", options=["Düşük", "Orta", "Yüksek"])
    
    st.divider()
    # Uitgebreide lijst met tickers
    tickers_dict = {
        "ABD Doları (USD/TRY)": "USDTRY=X",
        "Euro (EUR/TRY)": "EURTRY=X",
        "Gümüş (Silver)": "SI=F",
        "Alüminyum": "ALI=F",
        "Bitcoin": "BTC-TRY",
        "Altın (Ons)": "GC=F"
    }
    gekozen_ticker = st.selectbox("Geçmiş Grafiği İncele:", list(tickers_dict.keys()))

# --- STAP 2: Live Data Ophalen ---
@st.cache_data(ttl=3600)
def haal_data_op(tickers):
    prijzen = {}
    historie = {}
    # We halen ook de goudprijs in USD op om later om te rekenen naar TRY indien nodig
    usd_try_data = yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    
    for naam, symbool in tickers.items():
        t = yf.Ticker(symbool)
        hist = t.history(period="1y")['Close']
        
        # Correctie: Metalen worden in USD getoond, we rekenen ze om naar TRY
        if symbool in ["SI=F", "ALI=F", "GC=F"]:
            prijzen[naam] = hist.iloc[-1] * usd_try_data
            historie[naam] = hist * usd_try_data
        else:
            prijzen[naam] = hist.iloc[-1]
            historie[naam] = hist
            
    return prijzen, historie

live_prijzen, jaar_historie = haal_data_op(tickers_dict)

# --- STAP 3: Verdelingslogica (Aangepast voor nieuwe assets) ---
def bereken_tr_advies(budget, risico, prijzen):
    if risico == "Düşük": # Laag risico: Veel USD/EUR en Goud
        verdeling = {"ABD Doları (USD/TRY)": 0.3, "Euro (EUR/TRY)": 0.3, "Altın (Ons)": 0.2, "Gümüş (Silver)": 0.1, "Alüminyum": 0.1}
    elif risico == "Orta": # Gemiddeld: Mix van valuta, metalen en crypto
        verdeling = {"ABD Doları (USD/TRY)": 0.2, "Bitcoin": 0.2, "Altın (Ons)": 0.2, "Gümüş (Silver)": 0.2, "Alüminyum": 0.2}
    else: # Hoog risico: Veel Bitcoin en metalen
        verdeling = {"Bitcoin": 0.5, "Gümüş (Silver)": 0.2, "Alüminyum": 0.2, "Altın (Ons)": 0.1}
    
    rows = []
    for item, perc in verdeling.items():
        bedrag_try = budget * perc
        prijs_try = prijzen[item]
        eenheden = bedrag_try / prijs_try
        rows.append([item, f"%{perc*100}", f"₺{bedrag_try:,.2f}", f"₺{prijs_try:,.2f}", round(eenheden, 4)])
    
    return pd.DataFrame(rows, columns=["Varlık", "Oran", "Miktar (TRY)", "Güncel Fiyat (TRY)", "Alınabilir Adet"])

# --- STAP 4: Tonen op scherm ---
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader(f"Portföy Önerisi ({risico} Risk)")
    df_result = bereken_tr_advies(budget_try, risico, live_prijzen)
    st.dataframe(df_result, use_container_width=True)

with col2:
    st.subheader(f"Trend Analizi: {gekozen_ticker}")
    st.line_chart(jaar_historie[gekozen_ticker])

st.info("Not: Metal fiyatları (Gümüş/Alüminyum) ve Altın, USD bazlı piyasalardan çekilip güncel kurla TRY'ye çevrilmiştir.")
