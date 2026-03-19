import yfinance as yf
import smtplib
from email.mime.text import MIMEText
import os # NIEUW: Dit helpt ons de veilige kluis te openen

# --- STAP 1: De Kansen Scanner ---
# (Dit deel blijft precies hetzelfde als in je vorige code)
def check_kansen():
    extra_radars = {"Platin": "PL=F", "Bakır": "HG=F", "Paladyum": "PA=F", "GBP": "GBPTRY=X", "JPY": "JPYTRY=X", "Ethereum": "ETH-USD"}
    meldingen = []
    for naam, symbool in extra_radars.items():
        data = yf.Ticker(symbool).history(period="1mo")
        if not data.empty and len(data) > 10:
            prijs_oud, prijs_nieuw = data['Close'].iloc[0], data['Close'].iloc[-1]
            verschil_pct = ((prijs_nieuw - prijs_oud) / prijs_oud) * 100
            if verschil_pct > 5:
                meldingen.append(f"🔥 Hızlı Yükseliş: {naam} son 30 günde %{verschil_pct:.2f} arttı!")
            elif verschil_pct < -5:
                meldingen.append(f"📉 Düşüş Fırsatı: {naam} son 30 günde %{abs(verschil_pct):.2f} düştü.")
    return meldingen

# --- STAP 2: De E-mail Versturen (VEILIG GEMAAKT) ---
def stuur_email(gevonden_kansen):
    afzender_email = "jouw_email@gmail.com" # VUL DIT IN
    ontvanger_email = "jouw_email@gmail.com" # VUL DIT IN
    
    # VEILIGHEID: Haal het wachtwoord uit de GitHub kluis
    app_wachtwoord = os.environ.get("EMAIL_WACHTWOORD") 
    
    if app_wachtwoord is None:
        print("Fout: Wachtwoord niet gevonden in de kluis!")
        return

    bericht_tekst = "\n\n".join(gevonden_kansen)
    volledig_bericht = f"Merhaba,\n\nYatırım asistanın yeni fırsatlar buldu:\n\n{bericht_tekst}\n\nİyi günler!"
    
    msg = MIMEText(volledig_bericht)
    msg['Subject'] = '🚀 AI Yatırım Asistanı: Yeni Fırsatlar!'
    msg['From'] = afzender_email
    msg['To'] = ontvanger_email
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(afzender_email, app_wachtwoord)
        server.send_message(msg)
        server.quit()
        print("✅ E-mail met succes verstuurd!")
    except Exception as e:
        print(f"❌ Er ging iets mis bij het versturen: {e}")

# --- STAP 3: Het script starten ---
kansen = check_kansen()
if len(kansen) > 0:
    stuur_email(kansen)
else:
    print("Geen acties nodig vandaag.")
