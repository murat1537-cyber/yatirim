import yfinance as yf
import smtplib
from email.mime.text import MIMEText

# --- STAP 1: De Kansen Scanner ---
def check_kansen():
    extra_radars = {
        "Platin (Platina)": "PL=F",
        "Bakır (Koper)": "HG=F",
        "Paladyum (Palladium)": "PA=F",
        "İngiliz Sterlini (GBP)": "GBPTRY=X",
        "Japon Yeni (JPY)": "JPYTRY=X",
        "Ethereum": "ETH-USD"
    }
    
    meldingen = []
    print("Markt wordt gescand...")
    
    for naam, symbool in extra_radars.items():
        data = yf.Ticker(symbool).history(period="1mo")
        if not data.empty and len(data) > 10:
            prijs_oud = data['Close'].iloc[0] 
            prijs_nieuw = data['Close'].iloc[-1] 
            
            verschil_pct = ((prijs_nieuw - prijs_oud) / prijs_oud) * 100
            
            if verschil_pct > 5:
                meldingen.append(f"🔥 Hızlı Yükseliş: {naam} son 30 günde %{verschil_pct:.2f} arttı!")
            elif verschil_pct < -5:
                meldingen.append(f"📉 Düşüş Fırsatı: {naam} son 30 günde %{abs(verschil_pct):.2f} düştü.")
                
    return meldingen

# --- STAP 2: De E-mail Versturen ---
def stuur_email(gevonden_kansen):
    # VUL HIER JE EIGEN GEGEVENS IN:
    afzender_email = "jouw_email@gmail.com" 
    app_wachtwoord = "dqko tmsz lynp zvri" # Zie instructies hieronder!
    ontvanger_email = "jouw_email@gmail.com" # Mag hetzelfde zijn, je stuurt het naar jezelf
    
    # We maken een mooie tekst van de lijst met meldingen
    bericht_tekst = "\n\n".join(gevonden_kansen)
    volledig_bericht = f"Merhaba,\n\nYatırım asistanın yeni fırsatlar buldu:\n\n{bericht_tekst}\n\nİyi günler!"
    
    # De e-mail opbouwen
    msg = MIMEText(volledig_bericht)
    msg['Subject'] = '🚀 AI Yatırım Asistanı: Yeni Fırsatlar!'
    msg['From'] = afzender_email
    msg['To'] = ontvanger_email
    
    # Verbinding maken met Gmail en versturen
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
    print(f"Er zijn {len(kansen)} kansen gevonden. E-mail wordt voorbereid...")
    stuur_email(kansen)
else:
    print("Geen kansen groter dan 5% gevonden vandaag. Geen e-mail verstuurd.")
