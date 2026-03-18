import streamlit as st
from fpdf import FPDF
import datetime

# --- LEHE SEADISTUS ---
st.set_page_config(page_title="Arboristi Riskianalüüs", page_icon="🌳")

st.title("🌳 Arboristi ja Haljastuse Riskianalüüs")
st.write("Täida väljad ja genereeri ametlik PDF-dokument.")

# --- 1. ÜLDINFO ---
st.header("1. Üldinfo")
col1, col2 = st.columns(2)
with col1:
    ettevote = st.text_input("Ettevõte", "Arboristiabi OÜ")
    aadress = st.text_input("Objekti aadress")
    vastutav = st.text_input("Vastutav isik")
with col2:
    tellija = st.text_input("Tellija / Kontakt")
    kuupaev = st.date_input("Kuupäev", datetime.date.today())
    too_liik = st.selectbox("Tehtav töö põhiliik", [
        "Hoolduslõikus (kõrghaljastus)", "Sektsiooniline langetamine", 
        "Suunatud langetamine", "Ilu- ja pargipuude istutamine", 
        "Haljastus- ja pinnasetööd", "Hekkide pügamine", 
        "Viljapuude hoolduslõikus", "Parkide ja haljasalade hooldus", 
        "Kändude freesimine", "Võsa lõikus"
    ])

# --- 2. ASUKOHT JA PINNAS ---
st.header("2. Asukoha ja pinnase analüüs")
col3, col4 = st.columns(2)
with col3:
    ohuala = st.selectbox("Ohuala tähistus", ["Piiratud ohutuslindiga", "Valvuritega julgestatud", "Piiramata (eravaldus)", "Töötsoon tähistatud koonustega"])
    ilm = st.selectbox("Ilmastikuolud", ["Sobilik (tuul alla 8m/s)", "Tugev tuul", "Sadu / Mudane pinnas", "Kuumuskaitse"])
with col4:
    pinnas = st.selectbox("Pinnas ja trassid", ["Ei ole", "Maa-alused kaablid/trassid (kaevetööd!)", "Pehme/Vajuv pinnas", "Kivine/Raske pinnas", "Järsk kalle/Nõlv"])
    liiklus = st.selectbox("Liiklusolud", ["Vähene", "Tihe autoliiklus", "Jalakäijad", "Kergliiklustee servas"])

# --- 3. TEHNIKA JA TERVIS ---
st.header("3. Tehnika ja töötervishoid")
col5, col6 = st.columns(2)
with col5:
    tehnika = st.selectbox("Põhitehnika", ["Käsitööriistad", "Mootorsaag / Hekilõikur", "Miniekskavaator / Laadur", "Tõstuk / Kraana"])
    korgustood = st.selectbox("Töökõrgus", ["Maapinnalt töötamine", "Redelilt töötamine", "Ronimisvarustus / Topeltkinnitus", "Tõstuk / Korvstabiilsus"])
with col6:
    ergonoomika = st.selectbox("Terviseriskid", ["Ei ole", "Raskete koormate tõstmine", "Pidev sundasend", "Masinate vibratsioon"])

# --- PDF GENEREERIMINE ---
class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 15)
        self.cell(0, 12, "RISKIANALÜÜS: HALJASTUS JA PUUHOOLDUS", ln=True, align='C')

def create_pdf():
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    pdf.cell(50, 8, "Ettevõte:", 1)
    pdf.cell(140, 8, ettevote, 1, 1)
    pdf.cell(50, 8, "Objekt:", 1)
    pdf.cell(140, 8, aadress, 1, 1)
    pdf.cell(50, 8, "Töö liik:", 1)
    pdf.cell(140, 8, too_liik, 1, 1)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(0, 10, " RISKID JA MEETMED", 1, 1, 'L')
    pdf.set_font("Helvetica", size=9)
    riskid = [("Ohuala", ohuala), ("Ilm", ilm), ("Pinnas", pinnas), ("Tehnika", tehnika)]
    for r_l, r_v in riskid:
        pdf.cell(60, 8, r_l, 1)
        pdf.cell(130, 8, r_v, 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

if st.button("Genereeri PDF"):
    pdf_bytes = create_pdf()
    st.download_button(label="📥 Laadi PDF alla", data=pdf_bytes, file_name="Riskianalyys.pdf", mime="application/pdf")
