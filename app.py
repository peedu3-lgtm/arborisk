import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

# HEIC failide toe aktiveerimine (vajab: pip install pillow-heif)
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

# --- TÄIUSTATUD PDF KLASS ---
class ArboristPDF(FPDF):
    def header(self):
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
        """Asendab täpitähed, et vältida vigu standardse Helvetica fondiga."""
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
    vastutav = st.text_input("Tööjuht / Vastutav isik", "Ivar Peedu")
    aadress = st.text_input("Töö teostamise aadress", "Jaska-Kuusiku")
    # --- OMANIKU RIDA LISATUD SIIN ---
    omanik_info = st.text_input("Objekti omanik / Klient (Nimi ja Tel)", "") 
    kuupaev = datetime.date.today()

with st.expander("🚑 Esmaabi ja Päästeinfo"):
    hadaabi = st.text_input("Hädaabi", "112")
    haigla = st.text_input("Lähim haigla", "Pärnu Haigla")
    paaste_info = st.text_area("Juhised päästjatele", "Kruusatee, väravad lahti.")

st.divider()

# --- 2. RISKIDE HINDAMINE ---
st.subheader("⚠️ Ohutegurite hindamine")

seadmete_valik = ["Mootorsaag", "Akusaag", "Tõstuk", "Vints", "Hakkur", "Kännufrees", "Kraana", "Ronimisvarustus", "Käsisaag", "Muu..."]
meetmete_valik = ["Ohuala tähistamine lindiga", "Kiivri ja IKV kandmine", "Liikluse reguleerija", "Elektriliini pinge väljalülitus", "Kõrvaliste isikute eemaldamine", "Muu..."]
ohud_list = ["Kukkuvad oksad", "Kõrgusest kukkumine", "Lõikevigastused", "Elektrilöök", "Kolmandad isikud", "Ilmastik", "Müra/Vibratsioon"]

andmed = []
for oht in ohud_list:
    with st.expander(f"📍 OHT: {oht}", expanded=False):
        c1, c2 = st.columns(2)
        with c1: t = st.select_slider(f"Tõenäosus (T)", options=[1, 2, 3, 4, 5], key=oht+"t")
        with c2: r = st.select_slider(f"Tagajärg (R)", options=[1, 2, 3, 4, 5], key=oht+"r")
        
        märkus = st.text_input("Ohu täpsustus", key=oht+"m")
        
        # --- MUU VALIKU LOOGIKA TÖÖRIISTADELE ---
        s_sel = st.multiselect("Töövahendid", seadmete_valik, key=oht+"s")
        if "Muu..." in s_sel:
            s_muu = st.text_input("Lisa muu töövahend", key=oht+"s_muu")
            s_sel = [x if x != "Muu..." else s_muu for x in s_sel]
            
        # --- MUU VALIKU LOOGIKA MEETMETELE ---
        m_sel = st.multiselect("Meetmed", meetmete_valik, key=oht+"meede")
        if "Muu..." in m_sel:
            m_muu = st.text_input("Lisa muu meede", key=oht+"m_muu")
            m_sel = [x if x != "Muu..." else m_muu for x in m_sel]
            
        andmed.append({
            "oht": oht, 
            "märkus": märkus, 
            "seade": ", ".join(s_sel), 
            "meede": ", ".join(m_sel), 
            "t": t, "r": r, "skoor": t*r
        })

st.subheader("📸 Foto")
foto = st.file_uploader("Lisa foto (JPG, PNG, HEIC)", type=['jpg', 'jpeg', 'png', 'heic'])

# --- 3. PDF FUNKTSIOON ---
def generate_pdf():
    pdf = ArboristPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # 1. Üldinfo tabel
    pdf.section_title("1. ULDISED ANDMED")
    pdf.draw_info_row("Tooaandja", ettevote)
    pdf.draw_info_row("Vastutav isik", vastutav)
    pdf.draw_info_row("Objekti aadress", aadress)
    # --- OMANIKU RIDA LISATUD PDF-I ---
    pdf.draw_info_row("Objekti omanik", omanik_info) 
    pdf.draw_info_row("Kuupaev", str(kuupaev))
    pdf.ln(5)
    
    # 2. Esmaabi
    pdf.section_title("2. ESMAABI JA PAASTEINFO")
    pdf.draw_info_row("Hadaabi", hadaabi)
    pdf.draw_info_row("Haigla", haigla)
    pdf.draw_info_row("Paastetee juhis", paaste_info)
    pdf.ln(5)

    # 3. Riskide tabel
    pdf.section_title("3. RISKIDE HINDAMINE")
    pdf.set_font("Helvetica", 'B', 8)
    pdf.set_fill_color(240, 240, 240)
    w = [40, 45, 35, 45, 25]
    pealkirjad = ["Ohutegur", "Kirjeldus", "Toovahend", "Meetmed", "Skoor (TxR)"]
    for i in range(len(pealkirjad)):
        pdf.cell(w[i], 8, pealkirjad[i], 1, 0, 'C', True)
    pdf.ln()

    pdf.set_font("Helvetica", '', 7)
    for d in andmed:
        if pdf.get_y() > 240: pdf.add_page()
        start_y = pdf.get_y()

        # Multi-cell lahtrite kõrguse jälgimine
        pdf.multi_cell(w[0], 6, pdf.clean_text(d['oht']), 1)
        h1 = pdf.get_y() - start_y
        
        pdf.set_xy(10 + w[0], start_y)
        pdf.multi_cell(w[1], 6, pdf.clean_text(d['märkus']), 1)
        h2 = pdf.get_y() - start_y
        
        pdf.set_xy(10 + w[0] + w[1], start_y)
        pdf.multi_cell(w[2], 6, pdf.clean_text(d['seade']), 1)
        h3 = pdf.get_y() - start_y
        
        pdf.set_xy(10 + w[0] + w[1] + w[2], start_y)
        pdf.multi_cell(w[3], 6, pdf.clean_text(d['meede']), 1)
        h4 = pdf.get_y() - start_y
        
        max_h = max(h1, h2, h3, h4)
        pdf.set_xy(10 + w[0] + w[1] + w[2] + w[3], start_y)
        pdf.cell(w[4], max_h, str(d['skoor']), 1, 1, 'C')
        pdf.set_y(start_y + max_h)

    # Allkirjad
    pdf.ln(10)
    pdf.cell(95, 10, "Koostaja allkiri: ____________________", 0, 0, 'L')
    pdf.cell(95, 10, "Tootaja allkiri: ____________________", 0, 1, 'L')

    # Foto lisamine eraldi lehele
    if foto:
        pdf.add_page()
        pdf.section_title("LISA: OBJEKTI FOTO")
        img = Image.open(foto)
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG', quality=75)
        img_io.seek(0)
        pdf.image(img_io, x=10, y=30, w=190)

    out = pdf.output()
    return bytes(out) if isinstance(out, (bytearray, bytes)) else out.encode('latin-1', errors='replace')

# --- NUPUD ---
if st.button("🚀 GENEREERI PDF", use_container_width=True):
    try:
        pdf_bytes = generate_pdf()
        st.success("Dokument valmis!")
        st.download_button("📥 LAADI ALLA", data=pdf_bytes, file_name=f"Riskianalyys_{aadress}.pdf", mime="application/pdf", use_container_width=True)
    except Exception as e:
        st.error(f"Viga: {e}")
