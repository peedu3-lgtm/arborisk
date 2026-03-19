import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

class ArboristPDF(FPDF):
    def header(self):
        self.set_font("helvetica", 'B', 14)
        self.cell(0, 10, "TÖÖKOHA RISKIANALÜÜS JA OHUTUSPLAAN", ln=True, align='C')
        self.ln(5)

st.set_page_config(page_title="Arborisk Pro", layout="wide")

# 1. ÜLDISED ANDMED
st.header("1. ÜLDISED ANDMED")
c1, c2 = st.columns(2)
with c1:
    tooaandja = st.text_input("Tööandja", "Aiavana Hooldusteenused OÜ")
    vastutav = st.text_input("Vastutav isik", "Ivar Peedu")
    aadress = st.text_input("Objekti aadress", "")
with c2:
    omanik = st.text_input("Objekti omanik", "")
    haigla = st.text_input("Lähim haigla", "PERH")
    juhis = st.text_area("Päästetee juhis", "Ligipääs tänavalt.")

# 2. RISKID
st.header("2. RISKIDE HINDAMINE")
ohud_base = [
    ["Kukkuvad oksad", "Puuvõra hooldus", "Mootorsaag", "Ohuala piiramine"],
    ["Kõrgusest kukkumine", "Ronimine", "Ronimisvarustus", "IKV kontroll"],
    ["Ilmastik", "Välitöö", "-", "Töö peatamine"],
    ["Lõikevigastused", "Saega töö", "Mootorsaag", "Saepüksid, IKV"]
]

tabeli_andmed = []
for i, oht in enumerate(ohud_base):
    with st.expander(f"📍 {oht[0]}", expanded=True):
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 0.7, 0.7])
        with col1: kirj = st.text_input("Kirjeldus", value=oht[1], key=f"k{i}")
        with col2: vah = st.text_input("Töövahend", value=oht[2], key=f"v{i}")
        with col3: mee = st.text_input("Meede", value=oht[3], key=f"m{i}")
        with col4: t = st.number_input("T", 1, 5, 2, key=f"t{i}")
        with col5: r = st.number_input("R", 1, 5, 2, key=f"r{i}")
        
        skoor = t * r
        # Määrame vastuse skoori põhjal
        if skoor <= 4: vastus = "MADAL"
        elif skoor <= 12: vastus = "KESKMINE"
        else: vastus = "KÕRGE"
        
        tabeli_andmed.append([oht[0], kirj, vah, mee, f"{t}x{r}={skoor} ({vastus})"])

st.header("3. FOTO")
foto = st.file_uploader("Lisa pilt", type=['jpg', 'png'])

def genereeri_pdf():
    pdf = ArboristPDF()
    pdf.add_page()
    
    # Punkt 1
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "1. ÜLDISED ANDMED JA PÄÄSTEINFO", ln=True)
    pdf.set_font("helvetica", '', 10)
    with pdf.table(col_widths=(45, 145)) as table:
        table.row(["Tööandja", tooaandja])
        table.row(["Vastutav isik", vastutav])
        table.row(["Objekti aadress", aadress])
        table.row(["Lähim haigla", haigla])
        table.row(["Päästetee juhis", juhis])

    pdf.ln(10)
    
    # Punkt 2
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "2. RISKIDE HINDAMISE MAATRIKS", ln=True)
    pdf.set_font("helvetica", '', 8)
    with pdf.table(col_widths=(35, 30, 30, 60, 35)) as table:
        pdf.set_font("helvetica", 'B', 8)
        table.row(["Ohutegur", "Kirjeldus", "Töövahend", "Ennetusmeede", "Skoor ja Vastus"])
        pdf.set_font("helvetica", '', 8)
        for rida in tabeli_andmed:
            table.row(rida)

    # Punkt 3: Selgitused
    pdf.ln(10)
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 8, "RISKIHINDAMISE SELGITUSED", ln=True)
    pdf.set_font("helvetica", '', 7)
    with pdf.table(col_widths=(95, 95)) as table:
        table.row(["T (Tõenäosus)", "R (Raskusaste)"])
        table.row(["1-Väga väike; 2-Väike; 3-Keskmine; 4-Suur; 5-Väga suur", "1-Ebaoluline; 2-Kerge; 3-Keskmine; 4-Raske; 5-Surm"])
    
    pdf.ln(5)
    pdf.set_font("helvetica", 'I', 8)
    pdf.cell(0, 5, "Skoor 1-4: MADAL; 5-12: KESKMINE; 15-25: KÕRGE (Töö keelatud)", ln=True)

    # Allkirjad paberile (enne pilti)
    pdf.ln(10)
    pdf.set_font("helvetica", 'B', 9)
    pdf.cell(95, 10, "Koostaja allkiri: .................................", 0, 0)
    pdf.cell(95, 10, "Töötaja allkiri: .................................", 0, 1)

    # FOTO LÄHEB ALATI UUELE LEHELE, et tekst ei jookseks sisse
    if foto:
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 11)
        pdf.cell(0, 10, "3. OBJEKTI FOTO", ln=True)
        img = Image.open(foto)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        # Paigutame pildi nii, et see mahuks lehele
        pdf.image(img_byte_arr, x=15, y=30, w=180)

    return pdf.output()

if st.button("🚀 GENEREERI PDF"):
    pdf_res = genereeri_pdf()
    st.download_button("📥 Laadi alla", bytes(pdf_res), "Riskianalyys_Parandatud.pdf", "application/pdf")
