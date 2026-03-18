import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

# --- PDF KLASS KOOS PILDI TOETUSEGA ---
class RiskPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 16)
        self.cell(0, 10, "RISKIANALÜÜS JA OHUTUSPLAAN", ln=True, align='C')
        self.ln(10)

    def draw_table_header(self):
        self.set_font("Helvetica", 'B', 9)
        self.set_fill_color(230, 230, 230)
        self.cell(60, 10, "Ohutegur", 1, 0, 'C', True)
        self.cell(15, 10, "T", 1, 0, 'C', True)
        self.cell(15, 10, "R", 1, 0, 'C', True)
        self.cell(30, 10, "Riskitase", 1, 0, 'C', True)
        self.cell(70, 10, "Ennetusmeede", 1, 1, 'C', True)

# --- PEAMINE RAKENDUS ---
st.title("🌳 Arboristi Riskianalüüs")

with st.sidebar:
    st.header("📋 Üldinfo")
    ettevote = st.text_input("Ettevõte", "Arboristiabi OÜ")
    vastutav = st.text_input("Vastutav isik", "Ivar Peedu")
    objekt = st.text_input("Objekti aadress", "Männi tee 4")
    kuupaev = st.date_input("Kuupäev", datetime.date.today())
    
    st.divider()
    st.header("📸 Objekti foto")
    uploaded_file = st.file_uploader("Lisa foto objektist või ohust", type=['jpg', 'jpeg', 'png'])

st.subheader("🔍 Ohutegurite hindamine")
ohud = [
    "Kukkumine kõrgusest (ronimine, tõstuk)",
    "Langevad oksad ja tüveosad",
    "Lõikevigastused (mootorsaag)",
    "Elektrilöögi oht (liinid, kaablid)",
    "Liiklus, piirded ja kõrvalised isikud",
    "Maa-alused trassid ja kaevetööd"
]

hinnangud = []
for oht in ohud:
    col1, col2, col3, col4 = st.columns([2, 1, 1, 3])
    with col1: st.write(f"**{oht}**")
    with col2: t = st.selectbox("T", [1,2,3,4,5], key=oht+"t", index=1)
    with col3: r = st.selectbox("R", [1,2,3,4,5], key=oht+"r", index=2)
    with col4: meede = st.text_input("Meede", key=oht+"m", value="Kasutada nõuetekohast varustust")
    
    score = t * r
    tase = "MADAL" if score <= 4 else "KESKMINE" if score <= 12 else "KÕRGE"
    hinnangud.append([oht, str(t), str(r), tase, meede])

def genereeri_pdf():
    pdf = RiskPDF()
    pdf.add_page()
    
    # Päise info tabel
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(40, 8, "Ettevõte:", 1)
    pdf.set_font("Helvetica", '', 10)
    pdf.cell(150, 8, ettevote, 1, 1)
    
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(40, 8, "Objekt:", 1)
    pdf.set_font("Helvetica", '', 10)
    pdf.cell(150, 8, objekt, 1, 1)
    
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(40, 8, "Koostaja:", 1)
    pdf.set_font("Helvetica", '', 10)
    pdf.cell(150, 8, f"{vastutav} / {kuupaev}", 1, 1)
    pdf.ln(10)

    # Riskitabel
    pdf.draw_table_header()
    pdf.set_font("Helvetica", '', 8)
    
    for rida in hinnangud:
        curr_y = pdf.get_y()
        pdf.multi_cell(60, 10, rida[0], 1, 'L')
        pdf.set_xy(pdf.get_x() + 60, curr_y)
        pdf.cell(15, 10, rida[1], 1, 0, 'C')
        pdf.cell(15, 10, rida[2], 1, 0, 'C')
        
        # Värviloogika
        if rida[3] == "MADAL": pdf.set_text_color(0, 100, 0)
        elif rida[3] == "KESKMINE": pdf.set_text_color(150, 100, 0)
        else: pdf.set_text_color(200, 0, 0)
        
        pdf.cell(30, 10, rida[3], 1, 0, 'C')
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(70, 10, rida[4], 1, 'L')

    # PILDI LISAMINE PDF-I
    if uploaded_file is not None:
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 10, "Objekti foto / Lisa:", ln=True)
        
        # Töötleme pilti, et see mahuks lehele
        img = Image.open(uploaded_file)
        # Muudame pildi ajutiseks failiks
        img_path = "temp_image.png"
        img.save(img_path)
        # Lisame pildi (laius 180mm, et jääks äärtest ruumi)
        pdf.image(img_path, x=15, y=30, w=180)

    pdf.ln(20)
    # Kui pilt on pikk, võib allkiri nihkuda uuele lehele
    if pdf.get_y() > 250: pdf.add_page()
    pdf.set_font("Helvetica", 'I', 10)
    pdf.cell(0, 10, f"Analüüsi koostas: {vastutav} ................................... Kuupäev: {kuupaev}", ln=True)

    return pdf.output()

if st.button("🚀 Valmista dokument"):
    pdf_out = genereeri_pdf()
    st.download_button(
        label="📥 Laadi alla PDF (koos pildiga)",
        data=bytes(pdf_out),
        file_name=f"Riskianalyys_{objekt}.pdf",
        mime="application/pdf"
    )
    st.success("Dokument on edukalt genereeritud!")
