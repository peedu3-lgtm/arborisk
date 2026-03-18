import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

# --- ABIFUNKTSIOON TÄPITÄHTEDE JAOKS ---
def safe_str(text):
    """Asendab täpitähed, et vältida PDF-i vigu latin-1 koodis."""
    if not text: return ""
    rep = {'ä':'a','ö':'o','ü':'u','õ':'o','Ä':'A','Ö':'O','Ü':'U', 'Õ':'O', 'ž':'z', 'š':'s'}
    for k, v in rep.items():
        text = text.replace(k, v)
    return text

# --- TÄIUSTATUD PDF KLASS ---
class ArboristPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 14)
        self.cell(0, 10, "RISKIANALUUS JA OHUTUSPLAAN", ln=True, align='L')
        self.ln(2)

    def section_title(self, label):
        self.set_font("Helvetica", 'B', 10)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, f" {label}", 1, 1, 'L', True)

    def draw_info_row(self, label, value):
        self.set_font("Helvetica", 'B', 9)
        self.cell(50, 8, safe_str(label), 1, 0, 'L')
        self.set_font("Helvetica", '', 9)
        self.cell(140, 8, safe_str(value), 1, 1, 'L')

# --- RAKENDUSE SEADED ---
st.set_page_config(page_title="Arborisk Pro", layout="centered")

st.title("🌳 Arborisk Pro")
st.info("Täida väljad ja genereeri PDF. Mobiilis kasuta pildi lisamiseks kaamerat.")

# --- ANDMETE SISESTAMINE ---
with st.container():
    st.subheader("🏢 Üldinfo")
    ettevote = st.text_input("Ettevõte", "Framiter OÜ")
    vastutav = st.text_input("Vastutav isik", "Ivar Peedu")
    aadress = st.text_input("Objekti aadress", "Jaska-Kuusiku")

with st.expander("👤 Omaniku andmed"):
    omanik_nimi = st.text_input("Nimi")
    omanik_tel = st.text_input("Telefon")

with st.expander("🚑 Päästeinfo"):
    haigla = st.text_input("Lähim haigla", "Pärnu Haigla")
    paaste_info = st.text_input("Päästetee juhis", "Juurdepääs kruusateelt")
    hadaabi = st.text_input("Hädaabi", "112")

st.divider()

# --- RISKIDE HINDAMINE ---
st.subheader("⚠️ Riskide hindamine")

seadmete_list = ["Mootorsaag", "Tõstuk", "Vints", "Hakkur", "Kännufrees", "Kraana", "Käsisaag", "Ronimisvarustus", "Muu..."]
meetmete_list = ["Ohuala piiramine", "Isikukaitsevahendid (IKV)", "Liikluse reguleerimine", "Kõrvaliste isikute eemaldamine", "Liinide väljalülitus", "Muu..."]
ohud_list = ["Ohuala märgistus", "Ilmastikuolud", "Puu seisund", "Hooned/vara", "Elektriliinid", "Liiklus", "Pinnas"]

andmed = []

for oht in ohud_list:
    with st.expander(f"📍 {oht}", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            t = st.selectbox(f"Tõenäosus (1-5)", range(1, 6), key=oht+"t")
        with c2:
            r = st.selectbox(f"Raskusaste (1-5)", range(1, 6), key=oht+"r")
        
        märkus = st.text_input("Märkus / Kirjeldus", key=oht+"m")
        s = st.selectbox("Kasutatav seade", seadmete_list, key=oht+"s")
        m = st.selectbox("Ennetav meede", meetmete_list, key=oht+"meede")
            
        skoor = t * r
        tase = "MADAL" if skoor <= 4 else "KESKMINE" if skoor <= 12 else "KÕRGE"
        andmed.append({"oht": oht, "märkus": märkus, "seade": s, "meede": m, "t": t, "r": r, "skoor": skoor, "tase": tase})
        st.write(f"Riskitase: **{tase}** ({skoor})")

st.subheader("📸 Objektifoto")
foto = st.file_uploader("Lisa foto või tee pilt", type=['jpg', 'jpeg', 'png'])

# --- PDF FUNKTSIOON ---
def generate_pdf():
    pdf = ArboristPDF()
    pdf.add_page()
    
    # 1. Info
    pdf.section_title("OBJEKTI JA OSAPOOLTE ANDMED")
    pdf.draw_info_row("Ettevote", ettevote)
    pdf.draw_info_row("Vastutav", vastutav)
    pdf.draw_info_row("Aadress", aadress)
    pdf.draw_info_row("Omanik", f"{omanik_nimi} {omanik_tel}")
    pdf.draw_info_row("Kuupaev", str(datetime.date.today()))
    pdf.ln(5)
    
    # 2. Pääste
    pdf.section_title("PAASTEINFO")
    pdf.draw_info_row("Hadaabi", hadaabi)
    pdf.draw_info_row("Haigla", haigla)
    pdf.draw_info_row("Juhis", paaste_info)
    pdf.ln(5)

    # 3. Tabeli päis
    pdf.set_font("Helvetica", 'B', 8)
    pdf.set_fill_color(240, 240, 240)
    w = [35, 45, 35, 35, 10, 10, 20] 
    pealkirjad = ["Oht", "Markus", "Seade", "Meede", "T", "R", "Skoor"]
    for i in range(len(pealkirjad)):
        pdf.cell(w[i], 8, pealkirjad[i], 1, 0, 'C', True)
    pdf.ln()

    # 4. Tabeli sisu
    pdf.set_font("Helvetica", '', 7)
    for d in andmed:
        start_y = pdf.get_y()
        # Kasutame safe_str funktsiooni igal pool
        pdf.multi_cell(w[0], 7, safe_str(d['oht']), 1)
        next_y = pdf.get_y()
        
        pdf.set_xy(10 + w[0], start_y)
        pdf.multi_cell(w[1], 7, safe_str(d['märkus']), 1)
        if pdf.get_y() > next_y: next_y = pdf.get_y()
        
        pdf.set_xy(10 + w[0] + w[1], start_y)
        pdf.cell(w[2], (next_y - start_y), safe_str(d['seade']), 1)
        pdf.cell(w[3], (next_y - start_y), safe_str(d['meede']), 1)
        pdf.cell(w[4], (next_y - start_y), str(d['t']), 1, 0, 'C')
        pdf.cell(w[5], (next_y - start_y), str(d['r']), 1, 0, 'C')
        
        if d['skoor'] >= 15: pdf.set_text_color(255, 0, 0)
        pdf.cell(w[6], (next_y - start_y), f"{d['skoor']}", 1, 1, 'C')
        pdf.set_text_color(0, 0, 0)
        pdf.set_y(next_y)

    # Pilt
    if foto:
        try:
            pdf.add_page()
            pdf.section_title("OBJEKTI FOTO")
            img = Image.open(foto)
            img = img.convert('RGB')
            img.thumbnail((800, 800)) 
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=70)
            pdf.image(img_byte_arr, x=15, y=30, w=180)
        except Exception as e:
            st.error(f"Pildi viga: {e}")

    # --- FIKSEERITUD OUTPUT ---
    # See osa parandab sinu ekraanipildil olnud vea
    pdf_output = pdf.output()
    if isinstance(pdf_output, str):
        return pdf_output.encode('latin-1', errors='replace')
    return pdf_output

# --- NUPUD ---
st.markdown("---")
if st.button("🚀 GENEREERI LÕPLIK PDF", use_container_width=True):
    with st.spinner("Valmistan faili ette..."):
        try:
            pdf_bytes = generate_pdf()
            st.success("Analüüs on valmis!")
            st.download_button(
                label="📥 LAADI PDF ALLA",
                data=pdf_bytes,
                file_name=f"Riskianalyys_{aadress.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Süsteemi viga: {e}")
