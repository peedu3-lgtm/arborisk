import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

# --- PROFESSIONAALNE PDF KLASS ---
class ArboristPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 14)
        self.cell(0, 10, "RISKIANALÜÜS JA OHUTUSPLAAN", ln=True, align='L')
        self.ln(2)

    def section_title(self, label):
        self.set_font("Helvetica", 'B', 10)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, f" {label}", 1, 1, 'L', True)

    def draw_info_row(self, label, value):
        self.set_font("Helvetica", 'B', 9)
        self.cell(45, 8, label, 1, 0, 'L')
        self.set_font("Helvetica", '', 9)
        self.cell(145, 8, str(value), 1, 1, 'L')

# --- ÄPI LIIDES ---
st.set_page_config(page_title="Arboristi Riskianalüüs", layout="wide")

with st.sidebar:
    st.header("📋 Üldinfo")
    ettevote = st.text_input("Ettevõte", "Arboristiabi OÜ")
    aadress = st.text_input("Objekti aadress")
    vastutav = st.text_input("Vastutav isik / Koostaja")
    kuupaev = st.date_input("Kuupäev", datetime.date.today())
    
    st.divider()
    st.header("📸 Objekti foto")
    foto = st.file_uploader("Vali fail", type=['jpg', 'jpeg', 'png'])

st.title("🌳 Tööohutuse hindamine")

# Seadmete nimekiri valikuks
seadmete_valik = [
    "Mootorsaag", "Käsisid", "Ronimisvarustus", "Tõstuk", "Kännufrees", 
    "Oksapurusti", "Vints", "Kraana", "Minilaadur", "Isikukaitsevahendid (IKV)", "Muu..."
]

ohud_list = [
    "Ohuala märgistus ja piiramine",
    "Ilmastikuolud (tuul, sademed)",
    "Puu seisund (mädanik, tüvevead)",
    "Hooned ja lähedalasuv vara",
    "Elektriliinid ja tehnovõrgud",
    "Liiklus ja kõrvalised isikud",
    "Pinnase seisund ja kalle"
]

andmed = []
st.subheader("🔍 Ohutegurite analüüs")

for oht in ohud_list:
    with st.expander(f"📍 {oht}", expanded=True):
        c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
        with c1:
            kirjeldus = st.text_input("Eripära / Märkused", key=oht+"_k")
        with c2:
            seade = st.selectbox("Kasutatav seade/meede", seadmete_valik, key=oht+"_s")
            if seade == "Muu...":
                seade = st.text_input("Täpsusta seadet", key=oht+"_custom")
        with c3:
            t = st.number_input("T (1-5)", 1, 5, 2, key=oht+"_t")
        with c4:
            r = st.number_input("R (1-5)", 1, 5, 3, key=oht+"_r")
        
        skoor = t * r
        tase = "MADAL" if skoor <= 4 else "KESKMINE" if skoor <= 12 else "KÕRGE"
        andmed.append({"oht": oht, "kirjeldus": kirjeldus, "seade": seade, "t": t, "r": r, "tase": tase, "skoor": skoor})

# --- PDF LOOMINE ---
def loo_pdf():
    pdf = ArboristPDF()
    pdf.add_page()
    
    # 1. Päis
    pdf.draw_info_row("Ettevõte", ettevote)
    pdf.draw_info_row("Objekti aadress", aadress)
    pdf.draw_info_row("Vastutav isik", vastutav)
    pdf.draw_info_row("Kuupäev", str(kuupaev))
    pdf.ln(5)

    # 2. Tabeli päis
    pdf.set_font("Helvetica", 'B', 8)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(50, 10, "Ohutegur", 1, 0, 'C', True)
    pdf.cell(55, 10, "Kirjeldus / Märkused", 1, 0, 'C', True)
    pdf.cell(45, 10, "Seade / Meede", 1, 0, 'C', True)
    pdf.cell(10, 10, "T", 1, 0, 'C', True)
    pdf.cell(10, 10, "R", 1, 0, 'C', True)
    pdf.cell(20, 10, "Skoor", 1, 1, 'C', True)

    # 3. Tabeli sisu
    pdf.set_font("Helvetica", '', 8)
    for d in andmed:
        start_x = pdf.get_x()
        start_y = pdf.get_y()
        h = 10 # Rea baaskõrgus
        
        pdf.multi_cell(50, h, d['oht'], 1, 'L')
        pdf.set_xy(start_x + 50, start_y)
        pdf.multi_cell(55, h, d['kirjeldus'], 1, 'L')
        pdf.set_xy(start_x + 105, start_y)
        pdf.multi_cell(45, h, d['seade'], 1, 'L')
        pdf.set_xy(start_x + 150, start_y)
        pdf.cell(10, h, str(d['t']), 1, 0, 'C')
        pdf.cell(10, h, str(d['r']), 1, 0, 'C')
        
        # Värvime skoori vastavalt tasemele
        if d['tase'] == "KÕRGE": pdf.set_text_color(200, 0, 0)
        elif d['tase'] == "KESKMINE": pdf.set_text_color(150, 100, 0)
        else: pdf.set_text_color(0, 120, 0)
        
        pdf.cell(20, h, f"{d['skoor']} ({d['tase'][0]})", 1, 1, 'C')
        pdf.set_text_color(0, 0, 0)

    # 4. T ja R selgitused (UUS OSA)
    pdf.ln(10)
    pdf.section_title("RISKIHINDAMISE SELGITUSED (T x R)")
    pdf.set_font("Helvetica", '', 8)
    pdf.multi_cell(0, 5, (
        "T (Tõenäosus): 1-Väga väike; 2-Väike; 3-Keskmine; 4-Suur; 5-Väga suur (peaaegu kindel).\n"
        "R (Raskusaste): 1-Ebaoluline (plaaster); 2-Kerge (haigusleht); 3-Keskmine (luumurd); 4-Raske (invaliidsus); 5-Surm.\n"
        "Riskitase: 1-4 Madal (lubatud); 5-12 Keskmine (vajab lisameetmeid); 15-25 Kõrge (TÖÖ KEELATUD!)."
    ), 1, 'L')

    # 5. Pilt
    if foto:
        pdf.add_page()
        pdf.section_title("OBJEKTI FOTO")
        img = Image.open(foto)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        pdf.image(img_byte_arr, x=15, y=30, w=180)

    return pdf.output()

if st.button("🚀 GENEREERI PDF"):
    pdf_bytes = loo_pdf()
    st.download_button(
        label="📥 Laadi alla täiendatud PDF",
        data=bytes(pdf_bytes),
        file_name="Riskianalyys_Arborist.pdf",
        mime="application/pdf"
    )
