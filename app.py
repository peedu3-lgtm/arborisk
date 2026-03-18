import streamlit as st
from fpdf import FPDF
import datetime

st.set_page_config(page_title="Tööohutuse Riskianalüüs", page_icon="🛡️", layout="wide")

st.title("🛡️ Professionaalne Riskianalüüs (Tööinspektsiooni valmidus)")
st.write("Vastab töötervishoiu ja tööohutuse seaduse nõuetele.")

# --- ABIFUNKTSIOON RISKIDEEKS ---
def get_risk_level(t, r):
    score = t * r
    if score <= 4: return "MADAL", (0, 255, 0)
    if score <= 12: return "KESKMINE", (255, 255, 0)
    return "KÕRGE", (255, 0, 0)

# --- 1. ÜLDINFO ---
with st.expander("🏢 1. Ettevõtte ja objekti andmed", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        ettevote = st.text_input("Ettevõte", "Arboristiabi OÜ")
        aadress = st.text_input("Töö tegemise koht (aadress)")
        too_liik = st.text_input("Töö nimetus", "Puude raie ja hooldus")
    with col2:
        koostaja = st.text_input("Riskianalüüsi koostaja / Vastutav isik")
        kuupaev = st.date_input("Koostamise kuupäev", datetime.date.today())
        tootajad = st.text_area("Töös osalevad isikud (nimed)")

# --- 2. MAATRIKS-PÕHINE HINDAMINE ---
st.header("🔍 2. Ohutegurite hindamine")
st.info("Skaala: 1 (väga väike/ebaoluline) kuni 5 (väga tõenäoline/surmav)")

ohud = [
    "Kukkumine kõrgusest (ronimine, tõstuk, redel)",
    "Langevad oksad/tüved (vara ja inimeste ohutus)",
    "Lõikevigastused (mootorsaag, käsitööriistad)",
    "Elektrilöögi oht (liinid, trassid)",
    "Füüsiline koormus ja ergonoomika",
    "Müra ja vibratsioon",
    "Bioloogilised ohud (puugid, herilased, pinnas)",
    "Kõrvalised isikud ja liiklus tööalas"
]

hinnangud = {}

for oht in ohud:
    with st.container():
        st.subheader(oht)
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            t = st.slider(f"Tõenäosus (1-5)", 1, 5, 2, key=oht+"t")
        with c2:
            r = st.slider(f"Tagajärg (1-5)", 1, 5, 3, key=oht+"r")
        with c3:
            meede = st.text_input("Rakendatav ennetusmeede", placeholder="nt. Isikukaitsevahendid, ohutusvöö, valvur...", key=oht+"m")
        
        tase, varv = get_risk_level(t, r)
        st.caption(f"Riskitase: **{tase}** ({t*r} punkti)")
        hinnangud[oht] = {"t": t, "r": r, "meede": meede, "tase": tase}
        st.divider()

# --- 3. ISIKUKAITSEVAHENDID (IKV) ---
st.header("🦺 3. Kohustuslikud Isikukaitsevahendid")
ikv_list = ["Kiiver", "Näokaitse/Prillid", "Kõrvaklapid", "Saekaitsepüksid", "Turvajalanõud", "Kukumisvastane varustus", "Helkurvest", "Esmaabikomplekt"]
valitud_ikv = st.multiselect("Vali objektil kasutatavad IKV-d:", ikv_list, default=["Kiiver", "Näokaitse/Prillid", "Kõrvaklapid", "Esmaabikomplekt"])

# --- PDF GENEREERIMINE ---
class TiPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 12)
        self.cell(0, 10, "TÖÖKESKKONNA RISKIANALÜÜS JA OHUTUSPLAAN", ln=True, align='C')
        self.ln(5)

def create_ti_pdf():
    pdf = TiPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=9)
    
    # Päise tabel
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(50, 8, "Ettevõte:", 1, 0, 'L', True)
    pdf.cell(140, 8, ettevote, 1, 1)
    pdf.cell(50, 8, "Objekt:", 1, 0, 'L', True)
    pdf.cell(140, 8, aadress, 1, 1)
    pdf.cell(50, 8, "Vastutav isik:", 1, 0, 'L', True)
    pdf.cell(140, 8, koostaja, 1, 1)
    pdf.cell(50, 8, "Kuupäev:", 1, 0, 'L', True)
    pdf.cell(140, 8, str(kuupaev), 1, 1)
    
    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(0, 8, "RISKIDE HINDAMISE MAATRIKS", ln=True)
    
    # Riskitabeli päis
    pdf.set_font("Helvetica", 'B', 8)
    pdf.cell(65, 8, "Ohutegur", 1, 0, 'C', True)
    pdf.cell(15, 8, "T", 1, 0, 'C', True)
    pdf.cell(15, 8, "R", 1, 0, 'C', True)
    pdf.cell(25, 8, "Tase", 1, 0, 'C', True)
    pdf.cell(70, 8, "Ennetusmeede", 1, 1, 'C', True)
    
    pdf.set_font("Helvetica", size=8)
    for oht, andmed in hinnangud.items():
        pdf.cell(65, 8, oht, 1)
        pdf.cell(15, 8, str(andmed["t"]), 1, 0, 'C')
        pdf.cell(15, 8, str(andmed["r"]), 1, 0, 'C')
        pdf.cell(25, 8, andmed["tase"], 1, 0, 'C')
        pdf.multi_cell(70, 8, andmed["meede"], 1, 'L')
    
    pdf.ln(5)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(0, 8, f"Kasutatavad IKV-d: {', '.join(valitud_ikv)}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Helvetica", 'I', 9)
    pdf.multi_cell(0, 5, "Kinnitan, et olen teadlik tööga kaasnevatest ohtudest ja kohustun täitma ohutusnõudeid.\n\nAllkiri: __________________________")
    
    return pdf.output()

if st.button("🚀 GENEREERI AMETLIK DOKUMENT"):
    output = create_ti_pdf()
    st.download_button(
        label="📥 Laadi alla Tööinspektsioonile sobiv PDF",
        data=bytes(output),
        file_name=f"Riskianalyys_TI_{aadress}.pdf",
        mime="application/pdf"
    )
