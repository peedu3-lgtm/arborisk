import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

# Proovime importida HEIC tuge
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

# --- ABIFUNKTSIOON TÄPITÄHTEDE JAOKS ---
def safe_str(text):
    if not text: return ""
    # Standardne Helvetica ei toeta täpitähti, asendame need visuaalselt sarnastega
    rep = {'ä':'a','ö':'o','ü':'u','õ':'o','Ä':'A','Ö':'O','Ü':'U', 'Õ':'O', 'ž':'z', 'š':'s', 'Ž':'Z', 'Š':'S'}
    for k, v in rep.items():
        text = str(text).replace(k, v)
    return text

# --- TÄIUSTATUD PDF KLASS ---
class ArboristPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 14)
        self.cell(0, 10, "TOOKOHA RISKIANALUUS JA OHUTUSPLAAN", ln=True, align='C')
        self.set_font("Helvetica", 'I', 8)
        self.cell(0, 5, "Vastavalt Tootervishoiu ja toohutuse seadusele", ln=True, align='C')
        self.ln(5)

    def section_title(self, label):
        self.set_font("Helvetica", 'B', 10)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, f" {label}", 1, 1, 'L', True)

    def draw_info_row(self, label, value):
        self.set_font("Helvetica", 'B', 9)
        self.cell(55, 8, safe_str(label), 1, 0, 'L')
        self.set_font("Helvetica", '', 9)
        self.cell(135, 8, safe_str(value), 1, 1, 'L')

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
    kuupaev = datetime.date.today()

with st.expander("🚑 Esmaabi ja Päästeinfo"):
    hadaabi = st.text_input("Hädaabi number", "112")
    haigla = st.text_input("Lähim EMO / Haigla", "Pärnu Haigla")
    paaste_info = st.text_area("Juhised päästemeeskonnale", "Juurdepääs kruusateelt, väravad avatud.")
    esmaabi_andja = st.text_input("Esmaabi andja kohapeal", vastutav)

st.divider()

# --- 2. RISKIDE HINDAMINE ---
st.subheader("⚠️ Ohutegurite hindamine")

seadmete_valik = ["Mootorsaag", "Akusaag", "Tõstuk", "Vints", "Hakkur", "Kännufrees", "Kraana", "Ronimisvarustus", "Käsisaag", "Hekilõikur", "Lehepuhur", "Muu..."]
meetmete_valik = ["Ohuala tähistamine lindiga", "Kiivri ja IKV kandmine", "Liikluse reguleerija", "Elektriliini pinge väljalülitus", "Kõrvaliste isikute eemaldamine", "Töö peatamine tuulega", "Muu..."]
ohud_list = ["Kukkuvad oksad", "Kõrgusest kukkumine", "Lõikevigastused", "Elektrilöök", "Kolmandad isikud", "Ilmastik", "Müra/Vibratsioon", "Pinnase langus"]

andmed = []
for oht in ohud_list:
    with st.expander(f"📍 OHT: {oht}", expanded=False):
        c1, c2 = st.columns(2)
        with c1: t = st.select_slider(f"Tõenäosus (T)", options=[1, 2, 3, 4, 5], key=oht+"t")
        with c2: r = st.select_slider(f"Tagajärg (R)", options=[1, 2, 3, 4, 5], key=oht+"r")
        
        märkus = st.text_input("Ohu täpsustus", key=oht+"m")
        
        s_sel = st.multiselect("Töövahendid", seadmete_valik, key=oht+"s")
        if "Muu..." in s_sel:
            s_muu = st.text_input("Lisa muu töövahend", key=oht+"s_muu")
            s_sel = [x if x != "Muu..." else s_muu for x in s_sel]
            
        m_sel = st.multiselect("Meetmed", meetmete_valik, key=oht+"meede")
        if "Muu..." in m_sel:
            m_muu = st.text_input("Lisa muu meede", key=oht+"m_muu")
            m_sel = [x if x != "Muu..." else m_muu for x in m_sel]
            
        skoor = t * r
        andmed.append({
            "oht": oht, 
            "märkus": märkus, 
            "seade": ", ".join(s_sel), 
            "meede": ", ".join(m_sel), 
            "t": t, "r": r, "skoor": skoor
        })

st.subheader("📸 Objekti fotod")
# Lisatud HEIC failitüüp
foto = st.file_uploader("Lisa foto töömaast (JPG, PNG, HEIC)", type=['jpg', 'jpeg', 'png', 'heic'])

# --- 3. PDF FUNKTSIOON ---
def generate_pdf():
    pdf = ArboristPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # Info sektsioonid
    pdf.section_title("1. ULDISED ANDMED")
    pdf.draw_info_row("Tooaandja", ettevote)
    pdf.draw_info_row("Vastutav isik", vastutav)
    pdf.draw_info_row("Objekti aadress", aadress)
    pdf.draw_info_row("Kuupaev", str(kuupaev))
    pdf.ln(5)
    
    pdf.section_title("2. ESMAABI JA PAASTEINFO")
    pdf.draw_info_row("Hadaabinumber", hadaabi)
    pdf.draw_info_row("Esmaabi andja", esmaabi_andja)
    pdf.draw_info_row("Paastetee juhis", paaste_info)
    pdf.ln(5)

    pdf.section_title("3. RISKIHINDAMISE METOODIKA")
    pdf.set_font("Helvetica", '', 8)
    metoodika = "T (Toenaosus): 1-5 | R (Raskusaste): 1-5\nRiskitase: 1-4 Madal; 5-12 Keskmine; 15-25 Korge (TOO KEELATUD!)"
    pdf.multi_cell(0, 5, metoodika, 1, 'L')
    pdf.ln(5)

    # Riskide tabel
    pdf.section_title("4. RISKIDE HINDAMINE")
    pdf.set_font("Helvetica", 'B', 8)
    pdf.set_fill_color(240, 240, 240)
    w = [35, 40, 30, 45, 10, 10, 20]
    pealkirjad = ["Ohutegur", "Kirjeldus", "Toovahend", "Meetmed", "T", "R", "Skoor"]
    for i in range(len(pealkirjad)):
        pdf.cell(w[i], 8, pealkirjad[i], 1, 0, 'C', True)
    pdf.ln()

    pdf.set_font("Helvetica", '', 7)
    for d in andmed:
        # Arvutame maksimaalse kõrguse selles reas
        row_height = 6
        # Kontroll, kas järgmine rida mahub lehele (et ei jookseks jalusesse või pildi sisse)
        if pdf.get_y() > 240:
            pdf.add_page()
            # Joonistame päise uuesti
            pdf.set_font("Helvetica", 'B', 8)
            for i in range(len(pealkirjad)):
                pdf.cell(w[i], 8, pealkirjad[i], 1, 0, 'C', True)
            pdf.ln()
            pdf.set_font("Helvetica", '', 7)

        start_x = pdf.get_x()
        start_y = pdf.get_y()

        # Multi-cell lahtrid
        pdf.multi_cell(w[0], row_height, safe_str(d['oht']), 1)
        h1 = pdf.get_y() - start_y
        
        pdf.set_xy(start_x + w[0], start_y)
        pdf.multi_cell(w[1], row_height, safe_str(d['märkus']), 1)
        h2 = pdf.get_y() - start_y
        
        pdf.set_xy(start_x + w[0] + w[1], start_y)
        pdf.multi_cell(w[2], row_height, safe_str(d['seade']), 1)
        h3 = pdf.get_y() - start_y
        
        pdf.set_xy(start_x + w[0] + w[1] + w[2], start_y)
        pdf.multi_cell(w[3], row_height, safe_str(d['meede']), 1)
        h4 = pdf.get_y() - start_y
        
        max_h = max(h1, h2, h3, h4)
        
        # Joonistame numbrite lahtrid täiskõrgusega
        pdf.set_xy(start_x + w[0] + w[1] + w[2] + w[3], start_y)
        pdf.cell(w[4], max_h, str(d['t']), 1, 0, 'C')
        pdf.cell(w[5], max_h, str(d['r']), 1, 0, 'C')
        
        if d['skoor'] >= 15: pdf.set_text_color(200, 0, 0)
        pdf.cell(w[6], max_h, str(d['skoor']), 1, 1, 'C')
        pdf.set_text_color(0, 0, 0)
        
        pdf.set_y(start_y + max_h)

    # Allkirjad (alati uuel lehel või piisava vahega)
    if pdf.get_y() > 220: pdf.add_page()
    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 9)
    pdf.cell(95, 10, "Koostaja allkiri: ____________________", 0, 0, 'L')
    pdf.cell(95, 10, "Tootaja allkiri: ____________________", 0, 1, 'L')

    # Foto lisamine uuele lehele, et vältida kattumist
    if foto:
        pdf.add_page()
        pdf.section_title("LISA: OBJEKTI FOTO")
        img = Image.open(foto)
        img = img.convert("RGB")
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG', quality=75)
        img_io.seek(0)
        # Arvutame pildi suuruse, et see mahuks lehele
        pdf.image(img_io, x=10, y=30, w=190)

    # OUTPUT byte-formatis
    out = pdf.output()
    return bytes(out) if isinstance(out, (bytearray, bytes)) else out.encode('latin-1', errors='replace')

# --- NUPUD ---
if st.button("🚀 GENEREERI PDF", use_container_width=True):
    try:
        pdf_bytes = generate_pdf()
        st.success("Dokument valmis!")
        st.download_button("📥 LAADI ALLA", data=pdf_bytes, file_name=f"Riskianalyys_{aadress.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)
    except Exception as e:
        st.error(f"Viga: {e}")
