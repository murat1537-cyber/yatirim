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
    tickers_dict = {
        "ABD Doları (USD/TRY)": "USDTRY=X",
        "Euro (EUR/TRY)": "EURTRY=X",
        "Gümüş (Silver)": "SI=F",
        "Alüminyum": "ALI=F",
        "Bitcoin": "BTC-TRY",
        "Altın (Ons)": "GC=F"
    }
    gekozen_ticker = st.selectbox("Geçmiş Grafiği İncele:", list(tickers_dict.keys()))

# --- STAP 2: Live Data Ophalen (NU MET FOUTAFHANDELING) ---
@st.cache_data(ttl=3600)
def haal_data_op(tickers):
    prijzen = {}
    historie = {}
    
    # 1. Probeer USD/TRY op te halen, met controle
    usd_data = yf.Ticker("USDTRY=X").history(period="1d")
    if not usd_data.empty:
        usd_try_koers = usd_data['Close'].iloc[-1]
    else:
        usd_try_koers = 32.0 # Nood-waarde als Yahoo Finance storing heeft
        st.sidebar.warning("Kon live USD/TRY koers niet ophalen.")
    
    # 2. Haal de rest van de tickers op
    for naam, symbool in tickers.items():
        t = yf.Ticker(symbool)
        hist = t.history(period="1y")['Close']
        
        # CONTROLE: Is de lijst leeg?
        if not hist.empty:
            if symbool in ["SI=F", "ALI=F", "GC=F"]:
                prijzen[naam] = hist.iloc[-1] * usd_try_koers
                historie[naam] = hist * usd_try_koers
            else:
                prijzen[naam] = hist.iloc[-1]
                historie[naam] = hist
        else:
            # Als er geen data is, vul een dummy-waarde in om een crash te voorkomen
            st.sidebar.error(f"Geen data gevonden voor {naam} ({symbool})")
            prijzen[naam] = 0.0001 # Voorkomt dat we later 'delen door nul'
            historie[naam] = pd.Series([0.0001])
            
    return prijzen, historie

live_prijzen, jaar_historie = haal_data_op(tickers_dict)

# --- STAP 3: Verdelingslogica ---
def bereken_tr_advies(budget, risico, prijzen):
    if risico == "Düşük": 
        verdeling = {"ABD Doları (USD/TRY)": 0.3, "Euro (EUR/TRY)": 0.3, "Altın (Ons)": 0.2, "Gümüş (Silver)": 0.1, "Alüminyum": 0.1}
    elif risico == "Orta": 
        verdeling = {"ABD Doları (USD/TRY)": 0.2, "Bitcoin": 0.2, "Altın (Ons)": 0.2, "Gümüş (Silver)": 0.2, "Alüminyum": 0.2}
    else: 
        verdeling = {"Bitcoin": 0.5, "Gümüş (Silver)": 0.2, "Alüminyum": 0.2, "Altın (Ons)": 0.1}
    
    rows = []
    for item, perc in verdeling.items():
        bedrag_try = budget * perc
        prijs_try = prijzen[item]
        # Bereken eenheden veilig
        eenheden = bedrag_try / prijs_try if prijs_try > 0.0001 else 0
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
