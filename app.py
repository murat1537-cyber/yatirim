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
        "Bitcoin": "BTC-USD", 
        "Altın (Ons)": "GC=F"
    }
    gekozen_ticker = st.selectbox("Geçmiş Grafiği İncele:", list(tickers_dict.keys()))

# --- STAP 2: Live Data Ophalen ---
@st.cache_data(ttl=3600)
def haal_data_op(tickers):
    prijzen = {}
    historie = {}
    
    usd_data = yf.Ticker("USDTRY=X").history(period="1d")
    if not usd_data.empty:
        usd_try_koers = usd_data['Close'].iloc[-1]
    else:
        usd_try_koers = 32.0 
    
    for naam, symbool in tickers.items():
        t = yf.Ticker(symbool)
        hist = t.history(period="1y")['Close']
        
        if not hist.empty:
            if symbool in ["SI=F", "ALI=F", "GC=F", "BTC-USD"]:
                prijzen[naam] = hist.iloc[-1] * usd_try_koers
                historie[naam] = hist * usd_try_koers
            else:
                prijzen[naam] = hist.iloc[-1]
                historie[naam] = hist
        else:
            prijzen[naam] = 0.0001 
            historie[naam] = pd.Series([0.0001])
            
    return prijzen, historie, usd_try_koers

live_prijzen, jaar_historie, huidige_usd_try = haal_data_op(tickers_dict)

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


# --- STAP 5: NIEUW! De Kansen Radar ---
st.divider()
st.subheader("Radar: Fırsat Tarayıcı (Kansen Scanner) 🕵️‍♂️")

@st.cache_data(ttl=3600)
def scan_kansen():
    # Lijst met activa die de gebruiker normaal niet volgt
    extra_radars = {
        "Platin (Platina)": "PL=F",
        "Bakır (Koper)": "HG=F",
        "Paladyum (Palladium)": "PA=F",
        "İngiliz Sterlini (GBP)": "GBPTRY=X",
        "Japon Yeni (JPY)": "JPYTRY=X",
        "Ethereum": "ETH-USD"
    }
    
    meldingen = []
    
    for naam, symbool in extra_radars.items():
        # Haal data van 1 maand op
        data = yf.Ticker(symbool).history(period="1mo")
        if not data.empty and len(data) > 10:
            prijs_oud = data['Close'].iloc[0] # Prijs 30 dagen geleden
            prijs_nieuw = data['Close'].iloc[-1] # Prijs van vandaag
            
            # Wiskundige formule voor procentuele verandering
            verschil_pct = ((prijs_nieuw - prijs_oud) / prijs_oud) * 100
            
            # De regels voor een waarschuwing (meer dan 5% verandering)
            if verschil_pct > 5:
                meldingen.append(f"🔥 **Hızlı Yükseliş (Snelle stijging):** {naam} son 30 günde **%{verschil_pct:.2f}** arttı!")
            elif verschil_pct < -5:
                meldingen.append(f"📉 **Düşüş Fırsatı (Kans op dip):** {naam} son 30 günde **%{abs(verschil_pct):.2f}** düştü. (Ucuzlamış olabilir mi?)")
                
    return meldingen

# Toon de resultaten in een uitklapmenu zodat het netjes blijft
with st.expander("Gözden Kaçan Fırsatları Gör (Bekijk verborgen kansen)"):
    st.write("Sistemimiz son 30 günlük fiyat hareketlerini tarıyor. %5'ten fazla değişenleri burada listeliyoruz:")
    gevonden_kansen = scan_kansen()
    
    if len(gevonden_kansen) > 0:
        for kans in gevonden_kansen:
            st.markdown(kans) # Gebruik markdown voor mooie opmaak en emoji's
    else:
        st.info("Şu an piyasada büyük bir hareket tespit edilmedi. (Geen grote schommelingen gevonden op dit moment).")
