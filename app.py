import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

# --- TÄIUSTATUD PDF KLASS ---
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

# --- RAKENDUSE LIIDES ---
st.set_page_config(page_title="Arborisk Pro", layout="wide")

with st.sidebar:
    st.header("🏢 Üldinfo ja Osapooled")
    ettevote = st.text_input("Ettevõte", "Framiter OÜ")
    vastutav = st.text_input("Vastutav isik / Koostaja", "Ivar Peedu")
    st.divider()
    
    st.subheader("👤 Objekti omanik")
    omanik_nimi = st.text_input("Omaniku nimi")
    omanik_tel = st.text_input("Omaniku telefon")
    aadress = st.text_input("Objekti aadress", "Jaska-Kuusiku")
    
    st.divider()
    st.subheader("🚑 Pääste ja esmaabi")
    haigla = st.text_input("Lähim haigla/E MO", "Pärnu Haigla")
    paaste_info = st.text_input("Päästetee/Juhised", "Juurdepääs kruusateelt")
    hadaabi = st.text_input("Hädaabi number", "112")
    
    st.divider()
    foto = st.file_uploader("Lisa objekti foto", type=['jpg', 'jpeg', 'png'])

st.title("🌳 Detailne Riskihindamine")

# Valikud tabeli jaoks
seadmete_list = ["Mootorsaag", "Tõstuk", "Vints", "Hakkur", "Kännufrees", "Kraana", "Käsisaag", "Ronimisvarustus", "Muu..."]
meetmete_list = ["Ohuala piiramine", "Isikukaitsevahendid (IKV)", "Liikluse reguleerimine", "Kõrvaliste isikute eemaldamine", "Liinide väljalülitus", "Muu..."]

ohud_list = [
    "Ohuala märgistus ja piiramine",
    "Ilmastikuolud (tuul, sademed)",
    "Puu seisund (mädanik, vead)",
    "Hooned ja lähedalasuv vara",
    "Elektriliinid ja tehnovõrgud",
    "Liiklus ja kõrvalised isikud",
    "Pinnase seisund ja kalle"
]

andmed = []
for oht in ohud_list:
    with st.expander(f"📍 {oht}", expanded=True):
        c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 0.7, 0.7])
        with c1: märkus = st.text_input("Märkus", key=oht+"m")
        with c2: 
            s = st.selectbox("Seade", seadmete_list, key=oht+"s")
            if s == "Muu...": s = st.text_input("Täpsusta seadet", key=oht+"sc")
        with c3:
            m = st.selectbox("Meede", meetmete_list, key=oht+"meede")
            if m == "Muu...": m = st.text_input("Täpsusta meedet", key=oht+"mc")
        with c4: t = st.number_input("T", 1, 5, 1, key=oht+"t")
        with c5: r = st.number_input("R", 1, 5, 1, key=oht+"r")
        
        skoor = t * r
        tase = "MADAL" if skoor <= 4 else "KESKMINE" if skoor <= 12 else "KÕRGE"
        andmed.append({"oht": oht, "märkus": märkus, "seade": s, "meede": m, "t": t, "r": r, "skoor": skoor, "tase": tase})

# --- PDF GENEREERIMINE ---
def generate_pdf():
    pdf = ArboristPDF()
    pdf.add_page()
    
    # 1. Kontaktid ja osapooled
    pdf.section_title("OBJEKTI JA OSAPOOLTE ANDMED")
    pdf.draw_info_row("Ettevõte", ettevote)
    pdf.draw_info_row("Vastutav isik", vastutav)
    pdf.draw_info_row("Objekti aadress", aadress)
    pdf.draw_info_row("Omanik", f"{omanik_nimi} / {omanik_tel}")
    pdf.draw_info_row("Kuupäev", str(datetime.date.today()))
    pdf.ln(4)
    
    # 2. Päästeinfo
    pdf.section_title("PÄÄSTEINFO JA ESMAABI")
    pdf.draw_info_row("Hädaabi", hadaabi)
    pdf.draw_info_row("Lähim haigla", haigla)
    pdf.draw_info_row("Päästetee juhis", paaste_info)
    pdf.ln(6)

    # 3. Riskide tabel (nüüd koos meetmega)
    pdf.set_font("Helvetica", 'B', 7)
    pdf.set_fill_color(240, 240, 240)
    # Tulpade laiused: 40, 45, 45, 30, 10, 10, 10
    pdf.cell(40, 8, "Ohutegur", 1, 0, 'C', True)
    pdf.cell(45, 8, "Kirjeldus / Märkus", 1, 0, 'C', True)
    pdf.cell(35, 8, "Seade", 1, 0, 'C', True)
    pdf.cell(35, 8, "Meede", 1, 0, 'C', True)
    pdf.cell(10, 8, "T", 1, 0, 'C', True)
    pdf.cell(10, 8, "R", 1, 0, 'C', True)
    pdf.cell(15, 8, "Skoor", 1, 1, 'C', True)

    pdf.set_font("Helvetica", '', 7)
    for d in andmed:
        y_start = pdf.get_y()
        pdf.multi_cell(40, 8, d['oht'], 1, 'L')
        pdf.set_xy(50, y_start)
        pdf.multi_cell(45, 8, d['märkus'], 1, 'L')
        pdf.set_xy(95, y_start)
        pdf.multi_cell(35, 8, d['seade'], 1, 'L')
        pdf.set_xy(130, y_start)
        pdf.multi_cell(35, 8, d['meede'], 1, 'L')
        pdf.set_xy(165, y_start)
        pdf.cell(10, 8, str(d['t']), 1, 0, 'C')
        pdf.cell(10, 8, str(d['r']), 1, 0, 'C')
        
        # Skoori värvimine
        if d['tase'] == "KÕRGE": pdf.set_text_color(200, 0, 0)
        elif d['tase'] == "KESKMINE": pdf.set_text_color(150, 100, 0)
        else: pdf.set_text_color(0, 120, 0)
        
        pdf.cell(15, 8, f"{d['skoor']} ({d['tase'][0]})", 1, 1, 'C')
        pdf.set_text_color(0, 0, 0)

    # 4. Selgitused
    pdf.ln(5)
    pdf.section_title("RISKIHINDAMISE SELGITUSED (T x R)")
    pdf.set_font("Helvetica", '', 7)
    pdf.multi_cell(0, 4, (
        "T (Tõenäosus): 1-Väga väike; 2-Väike; 3-Keskmine; 4-Suur; 5-Väga suur.\n"
        "R (Raskusaste): 1-Ebaoluline; 2-Kerge; 3-Keskmine; 4-Raske; 5-Surm.\n"
        "Riskitase: 1-4 Madal (lubatud); 5-12 Keskmine (lisameetmed); 15-25 Kõrge (KEELATUD!)."
    ), 1, 'L')

    # 5. Pilt
    if foto:
        pdf.add_page()
        pdf.section_title("OBJEKTI FOTO")
        img = Image.open(foto)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        pdf.image(buf, x=15, y=30, w=180)

    return pdf.output()

if st.button("🚀 GENEREERI LÕPLIK PDF"):
    pdf_out = generate_pdf()
    st.download_button("📥 Laadi alla PDF", bytes(pdf_out), f"Riskianalyys_{aadress}.pdf", "application/pdf")
