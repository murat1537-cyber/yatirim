import streamlit as st
import pandas as pd
import yfinance as yf

# Titel en Styling
st.set_page_config(page_title="AI Investment Tracker", layout="wide")
st.title("📈 Live AI Investeringsdashboard")
st.markdown("Dit dashboard haalt **live beurskoersen** op om je budget te verdelen.")

# --- STAP 1: Gebruikersinput ---
with st.sidebar:
    st.header("Instellingen")
    budget = st.number_input("Investeringsbudget (€)", min_value=50, value=1000)
    risico = st.select_slider("Risicoprofiel", options=["Laag", "Gemiddeld", "Hoog"])

# --- STAP 2: Live Data Ophalen ---
@st.cache_data(ttl=3600) # Slaat data 1 uur op om de app snel te houden
def haal_koersen_op():
    tickers = {
        "Aandelen (S&P 500)": "^GSPC",
        "Goud": "GC=F",
        "Bitcoin": "BTC-USD"
    }
    prijzen = {}
    for naam, ticker in tickers.items():
        data = yf.Ticker(ticker)
        # Haal de laatst bekende prijs op
        prijzen[naam] = data.history(period="1d")['Close'].iloc[-1]
    return prijzen

live_prijzen = haal_koersen_op()

# --- STAP 3: Verdelingslogica ---
def bereken_advies(budget, risico, prijzen):
    if risico == "Laag":
        verdeling = {"Goud": 0.6, "Aandelen (S&P 500)": 0.3, "Bitcoin": 0.1}
    elif risico == "Gemiddeld":
        verdeling = {"Goud": 0.3, "Aandelen (S&P 500)": 0.5, "Bitcoin": 0.2}
    else: # Hoog
        verdeling = {"Goud": 0.1, "Aandelen (S&P 500)": 0.4, "Bitcoin": 0.5}
    
    data_rows = []
    for item, percentage in verdeling.items():
        bedrag = budget * percentage
        prijs = prijzen[item]
        eenheden = bedrag / prijs
        data_rows.append([item, f"{percentage*100}%", f"€{bedrag:,.2f}", f"€{prijs:,.2f}", round(eenheden, 4)])
    
    return pd.DataFrame(data_rows, columns=["Activa", "Verdeling", "Bedrag", "Huidige Prijs", "Aantal te kopen"])

# --- STAP 4: Resultaten tonen ---
if st.button("Update Portfolio met Live Koersen"):
    df_advies = bereken_advies(budget, risico, live_prijzen)
    
    st.subheader(f"Geadviseerde Portefeuille ({risico} Risico)")
    st.table(df_advies)
    
    # Visuele weergave
    st.bar_chart(df_advies.set_index("Activa")["Aantal te kopen"])
    st.info("De prijzen zijn live opgehaald via de Yahoo Finance API.")
