import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

# Proovime aktiveerida HEIC toe
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    HEIC_SUPPORT = False

# --- TÄIUSTATUD PDF KLASS ---
class ArboristPDF(FPDF):
    def header(self):
        # Kasutame standardfonti, aga puhastatud tekstiga
        self.set_font("Helvetica", 'B', 14)
        self.cell(0, 10, "TOOKOHA RISKIANALUUS JA OHUTUSPLAAN", ln=True, align='C')
        self.ln(5)

    def section_title(self, label):
        self.set_font("Helvetica", 'B', 10)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, f" {label}", 1, 1, 'L', True)

    def draw_info_row(self, label, value):
        self.set_font("Helvetica", 'B', 9)
        self.cell(55, 8, self.clean_text(label), 1, 0, 'L')
        self.set_font("Helvetica", '', 9)
        self.cell(135, 8, self.clean_text(value), 1, 1, 'L')

    def clean_text(self, text):
        """Asendab täpitähed sarnaste märkidega, et vältida vigu Helvetica fondis."""
        if not text: return ""
        rep = {'ä':'a','ö':'o','ü':'u','õ':'o','Ä':'A','Ö':'O','Ü':'U', 'Õ':'O', 'ž':'z', 'š':'s', 'Ž':'Z', 'Š':'S'}
        for k, v in rep.items():
            text = str(text).replace(k, v)
        return text

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", 'I', 8)
        self.cell(0, 10, f"Lehekülg {self.page_no()}", 0, 0, 'C')

# --- RAKENDUSE SEADED ---
st.set_page_config(page_title="Arborisk Pro", layout="centered")
st.title("🌳 Arborisk Pro")

# --- 1. ÜLDINFO ---
with st.container():
    st.info("📋 Objekti ja osapoolte andmed")
    ettevote = st.text_input("Tööandja / Ettevõte", "Framiter OÜ")
    vastutav = st.text_input("Vastutav isik", "Ivar Peedu")
    aadress = st.text_input("Töö aadress", "Jaska-Kuusiku")
    omanik = st.text_input("Objekti omanik / Klient", "") # TAGASI LISATUD
    kuupaev = datetime.date.today()

with st.expander("🚑 Esmaabi ja Päästeinfo"):
    hadaabi = st.text_input("Hädaabi", "112")
    haigla = st.text_input("Lähim haigla", "Pärnu Haigla")
    paaste_info = st.text_area("Juhised päästjatele", "Kruusatee, väravad lahti.")

st.divider()

# --- 2. RISKID ---
st.subheader("⚠️ Riskid")
seadmed = ["Mootorsaag", "Tõstuk", "Hakkur", "Vints", "Ronimisvarustus", "Muu..."]
meetmed = ["Ohuala piiramine", "IKV kandmine", "Liikluse reguleerimine", "Muu..."]
ohud = ["Kukkuvad oksad", "Kõrgus", "Elekter", "Liiklus", "Ilmastik"]

andmed = []
for oht in ohud:
    with st.expander(f"📍 {oht}"):
        c1, c2 = st.columns(2)
        t = c1.slider("T", 1, 5, 1, key=oht+"t")
        r = c2.slider("R", 1, 5, 1, key=oht+"r")
        
        märkus = st.text_input("Märkus", key=oht+"m")
        
        # Dünaamiline tööriistade valik
        s_valik = st.multiselect("Tööriistad", seadmed, key=oht+"s")
        if "Muu..." in s_valik:
            s_muu = st.text_input("Täpsusta tööriista", key=oht+"sm")
            s_valik = [x if x != "Muu..." else s_muu for x in s_valik]
            
        # Dünaamiline meetmete valik
        m_valik = st.multiselect("Meetmed", meetmed, key=oht+"me")
        if "Muu..." in m_valik:
            m_muu = st.text_input("Täpsusta meedet", key=oht+"mm")
            m_valik = [x if x != "Muu..." else m_muu for x in m_valik]
            
        andmed.append({"oht": oht, "märkus": märkus, "s": ", ".join(s_valik), "m": ", ".join(m_valik), "tr": t*r})

st.subheader("📸 Foto")
foto = st.file_uploader("Lisa pilt (JPG, PNG, HEIC)", type=['jpg', 'jpeg', 'png', 'heic'])

# --- 3. PDF GENEREERIMINE ---
def generate_pdf():
    pdf = ArboristPDF()
    pdf.add_page()
    
    # Andmed
    pdf.section_title("1. ULDISED ANDMED")
    pdf.draw_info_row("Ettevote", ettevote)
    pdf.draw_info_row("Vastutav", vastutav)
    pdf.draw_info_row("Aadress", aadress)
    pdf.draw_info_row("Omanik", omanik) # LISATUD PDF-i
    pdf.draw_info_row("Kuupaev", str(kuupaev))
    pdf.ln(5)
    
    # Tabeli päis
    pdf.section_title("2. RISKID")
    pdf.set_font("Helvetica", 'B', 8)
    w = [40, 50, 40, 40, 20]
    päis = ["Oht", "Markus", "Vahend", "Meede", "Skoor"]
    for i in range(len(päis)):
        pdf.cell(w[i], 8, päis[i], 1, 0, 'C', True)
    pdf.ln()

    # Tabeli sisu
    pdf.set_font("Helvetica", '', 7)
    for d in andmed:
        if pdf.get_y() > 250: pdf.add_page()
        cur_y = pdf.get_y()
        
        pdf.multi_cell(w[0], 6, pdf.clean_text(d['oht']), 1)
        h = pdf.get_y() - cur_y
        
        pdf.set_xy(10 + w[0], cur_y)
        pdf.multi_cell(w[1], 6, pdf.clean_text(d['märkus']), 1)
        h = max(h, pdf.get_y() - cur_y)
        
        pdf.set_xy(10 + w[0] + w[1], cur_y)
        pdf.multi_cell(w[2], 6, pdf.clean_text(d['s']), 1)
        h = max(h, pdf.get_y() - cur_y)
        
        pdf.set_xy(10 + w[0] + w[1] + w[2], cur_y)
        pdf.multi_cell(w[3], 6, pdf.clean_text(d['m']), 1)
        h = max(h, pdf.get_y() - cur_y)
        
        pdf.set_xy(10 + w[0] + w[1] + w[2] + w[3], cur_y)
        pdf.cell(w[4], h, str(d['tr']), 1, 1, 'C')
        pdf.set_y(cur_y + h)

    # Allkirjad
    pdf.ln(10)
    pdf.cell(90, 10, "Koostaja: ________________", 0)
    pdf.cell(90, 10, "Tootaja: ________________", 0, 1)

    # Pilt
    if foto:
        pdf.add_page()
        pdf.section_title("OBJEKTI FOTO")
        img = Image.open(foto)
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG', quality=75)
        img_io.seek(0)
        pdf.image(img_io, x=10, y=30, w=190)

    res = pdf.output()
    return bytes(res) if isinstance(res, (bytearray, bytes)) else res.encode('latin-1', errors='replace')

if st.button("🚀 GENEREERI PDF", use_container_width=True):
    try:
        final_pdf = generate_pdf()
        st.download_button("📥 LAADI ALLA", data=final_pdf, file_name=f"Risk_{aadress}.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"Viga: {e}")
