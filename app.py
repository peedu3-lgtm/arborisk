import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

# --- ABIFUNKTSIOON TÄPITÄHTEDE JAOKS ---
def safe_str(text):
    if not text: return ""
    rep = {'ä':'a','ö':'o','ü':'u','õ':'o','Ä':'A','Ö':'O','Ü':'U', 'Õ':'O', 'ž':'z', 'š':'s'}
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
        self.cell(0, 10, f"Lehekulg {self.page_no()}", 0, 0, 'C')

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

with st.expander("👤 Kliendi / Omaniku info"):
    omanik_nimi = st.text_input("Omaniku nimi")
    omanik_tel = st.text_input("Omaniku kontakttelefon")

with st.expander("🚑 Esmaabi ja Päästeinfo"):
    hadaabi = st.text_input("Hädaabi number", "112")
    haigla = st.text_input("Lähim EMO / Haigla", "Pärnu Haigla")
    paaste_info = st.text_area("Juhised päästemeeskonnale", "Juurdepääs kruusateelt, väravad avatud.")
    esmaabi_andja = st.text_input("Esmaabi andja kohapeal", vastutav)

st.divider()

# --- 2. RISKIDE HINDAMINE ---
st.subheader("⚠️ Ohutegurite hindamine")

seadmete_list = ["Mootorsaag", "Tõstuk", "Vints", "Hakkur", "Kännufrees", "Kraana", "Ronimisvarustus", "Muu..."]
meetmete_list = ["Ohuala tähistamine lindiga", "Kiivri ja IKV kandmine", "Liikluse reguleerija", "Elektriliini pinge väljalülitus", "Muu..."]
ohud_list = ["Kukkuvad oksad", "Kõrgusest kukkumine", "Lõikevigastused", "Elektrilöök", "Kolmandad isikud", "Ilmastik", "Müra"]

andmed = []
for oht in ohud_list:
    with st.expander(f"📍 OHT: {oht}", expanded=False):
        c1, c2 = st.columns(2)
        with c1: t = st.select_slider(f"Tõenäosus (T)", options=[1, 2, 3, 4, 5], key=oht+"t")
        with c2: r = st.select_slider(f"Tagajärg (R)", options=[1, 2, 3, 4, 5], key=oht+"r")
        
        märkus = st.text_input("Ohu täpsustus", key=oht+"m")
        s = st.multiselect("Töövahendid", seadmete_list, key=oht+"s")
        m = st.multiselect("Meetmed", meetmete_list, key=oht+"meede")
            
        skoor = t * r
        tase = "MADAL" if skoor <= 4 else "KESKMINE" if skoor <= 12 else "KÕRGE"
        andmed.append({"oht": oht, "märkus": märkus, "seade": ", ".join(s), "meede": ", ".join(m), "t": t, "r": r, "skoor": skoor, "tase": tase})

st.subheader("📸 Objekti fotod")
foto = st.file_uploader("Lisa foto töömaast", type=['jpg', 'jpeg', 'png'])

# --- 3. PDF FUNKTSIOON ---
def generate_pdf():
    pdf = ArboristPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # 1. Info
    pdf.section_title("1. ULDISED ANDMED")
    pdf.draw_info_row("Tooaandja", ettevote)
    pdf.draw_info_row("Vastutav isik", vastutav)
    pdf.draw_info_row("Objekti aadress", aadress)
    pdf.draw_info_row("Kuupaev", str(kuupaev))
    pdf.ln(5)
    
    # 2. Esmaabi
    pdf.section_title("2. ESMAABI JA PAASTEINFO")
    pdf.draw_info_row("Hadaabinumber", hadaabi)
    pdf.draw_info_row("Esmaabi andja", esmaabi_andja)
    pdf.draw_info_row("Paastetee juhis", paaste_info)
    pdf.ln(5)

    # 3. Metoodika kirjeldus (T ja R selgitus)
    pdf.section_title("3. RISKIHINDAMISE METOODIKA")
    pdf.set_font("Helvetica", '', 8)
    metoodika = (
        "T (Toenaosus): 1-Vaga vaike; 2-Vaike; 3-Keskmine; 4-Suur; 5-Pidev oht.\n"
        "R (Raskusaste/Tagajarg): 1-Ebaoluline; 2-Kerge vigastus; 3-Keskmine; 4-Raske (pusiivalu); 5-Surm.\n"
        "Riskitase (T x R): 1-4 Madal (lubatud); 5-12 Keskmine (vajab meetmeid); 15-25 Korge (TOO KEELATUD!)."
    )
    pdf.multi_cell(0, 5, metoodika, 1, 'L')
    pdf.ln(5)

    # 4. Tabel
    pdf.section_title("4. RISKIDE HINDAMINE")
    pdf.set_font("Helvetica", 'B', 8)
    w = [35, 40, 30, 45, 10, 10, 20]
    pealkirjad = ["Ohutegur", "Kirjeldus", "Toovahend", "Meetmed", "T", "R", "Indeks"]
    for i in range(len(pealkirjad)):
        pdf.cell(w[i], 8, pealkirjad[i], 1, 0, 'C', True)
    pdf.ln()

    pdf.set_font("Helvetica", '', 7)
    for d in andmed:
        start_y = pdf.get_y()
        pdf.multi_cell(w[0], 6, safe_str(d['oht']), 1)
        next_y = pdf.get_y()
        
        pdf.set_xy(10 + w[0], start_y)
        pdf.multi_cell(w[1], 6, safe_str(d['märkus']), 1)
        if pdf.get_y() > next_y: next_y = pdf.get_y()
        
        pdf.set_xy(10 + w[0] + w[1], start_y)
        pdf.multi_cell(w[2], 6, safe_str(d['seade']), 1)
        if pdf.get_y() > next_y: next_y = pdf.get_y()
        
        pdf.set_xy(10 + w[0] + w[1] + w[2], start_y)
        pdf.multi_cell(w[3], 6, safe_str(d['meede']), 1)
        if pdf.get_y() > next_y: next_y = pdf.get_y()
        
        h = next_y - start_y
        pdf.set_xy(10 + w[0] + w[1] + w[2] + w[3], start_y)
        pdf.cell(w[4], h, str(d['t']), 1, 0, 'C')
        pdf.cell(w[5], h, str(d['r']), 1, 0, 'C')
        if d['skoor'] >= 15: pdf.set_text_color(200, 0, 0)
        pdf.cell(w[6], h, f"{d['skoor']}", 1, 1, 'C')
        pdf.set_text_color(0, 0, 0)
        pdf.set_y(next_y)

    # Pilt - PARANDATUD LISAMINE
    if foto:
        try:
            pdf.add_page()
            pdf.section_title("LISA: OBJEKTI FOTO")
            # Muudame pildi formaati ja suurust, et fpdf sellega kindlalt hakkama saaks
            img = Image.open(foto)
            img = img.convert("RGB")
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=80)
            img_io.seek(0)
            # Kasutame ajutist nime või otsest IO-d
            pdf.image(img_io, x=15, y=30, w=180)
        except Exception as e:
            st.error(f"Pildi lisamise viga: {e}")

    # Allkirjad
    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 9)
    pdf.cell(95, 10, "Koostaja allkiri: ____________________", 0, 0, 'L')
    pdf.cell(95, 10, "Tootaja allkiri: ____________________", 0, 1, 'L')

    # OUTPUT PARANDUS
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
