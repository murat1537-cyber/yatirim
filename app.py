import streamlit as st
import pandas as pd

# Titel van de app
st.title("🚀 Mijn AI Investeringshulp")
st.subheader("Ontvang een suggestie voor je portfolio op basis van jouw profiel.")

# Stap 1: Gebruikersinput
budget = st.number_input("Wat is je totale investeringsbudget (€)?", min_value=100, value=1000)
risico = st.select_slider(
    "Wat is je risicobereidheid?",
    options=["Laag", "Gemiddeld", "Hoog"]
)

# Stap 2: De "AI" Logica (Eenvoudig algoritme)
def bereken_verdeling(budget, risico):
    if risico == "Laag":
        verdeling = {"Obligaties": 0.7, "Aandelen": 0.2, "Cash/Goud": 0.1}
    elif risico == "Gemiddeld":
        verdeling = {"Obligaties": 0.4, "Aandelen": 0.5, "Crypto": 0.1}
    else: # Hoog risico
        verdeling = {"Obligaties": 0.1, "Aandelen": 0.6, "Crypto": 0.3}
    
    # Omzetten naar bedragen
    resultaat = {item: percentage * budget for item, percentage in verdeling.items()}
    return resultaat

# Stap 3: Resultaten tonen
if st.button("Genereer Advies"):
    advies = bereken_verdeling(budget, risico)
    
    st.write(f"### Aanbevolen verdeling voor een {risico} risicoprofiel:")
    
    # Tabel tonen
    df = pd.DataFrame(list(advies.items()), columns=["Categorie", "Bedrag (€)"])
    st.table(df)
    
    # Grafiek tonen
    st.bar_chart(df.set_index("Categorie"))
    
    st.success("Dit is een technisch voorbeeld. Doe altijd eigen onderzoek voor je investeert!")
