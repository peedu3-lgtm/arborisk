import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

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
        self.cell(50, 8, label, 1, 0, 'L')
        self.set_font("Helvetica", '', 9)
        self.cell(140, 8, str(value), 1, 1, 'L')

# --- RAKENDUSE SEADED ---
st.set_page_config(page_title="Arborisk Pro", layout="centered") # 'centered' on mobiilis parem

st.title("🌳 Arborisk Pro")
st.markdown("---")

# --- ANDMETE SISESTAMINE ---
# Kasutame konteinereid, et mobiilis oleks parem ülevaade
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
    with st.container():
        st.markdown(f"**📍 {oht}**")
        # Mobiilis on 2 veergu max, mis töötab
        col1, col2 = st.columns(2)
        with col1:
            t = st.selectbox(f"T (1-5)", range(1, 6), key=oht+"t", index=0)
        with col2:
            r = st.selectbox(f"R (1-5)", range(1, 6), key=oht+"r", index=0)
        
        märkus = st.text_input("Märkus / Kirjeldus", key=oht+"m")
        
        c3, c4 = st.columns(2)
        with c3:
            s = st.selectbox("Seade", seadmete_list, key=oht+"s")
        with c4:
            m = st.selectbox("Meede", meetmete_list, key=oht+"meede")
            
        skoor = t * r
        tase = "MADAL" if skoor <= 4 else "KESKMINE" if skoor <= 12 else "KÕRGE"
        andmed.append({"oht": oht, "märkus": märkus, "seade": s, "meede": m, "t": t, "r": r, "skoor": skoor, "tase": tase})
        st.markdown(f"Riskitase: **{tase}** ({skoor})")
        st.divider()

foto = st.file_uploader("📸 Lisa objekti foto (vajadusel)", type=['jpg', 'jpeg', 'png'])

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
    w = [35, 45, 35, 35, 10, 10, 20] # Veergude laiused
    pealkirjad = ["Oht", "Markus", "Seade", "Meede", "T", "R", "Skoor"]
    for i in range(len(pealkirjad)):
        pdf.cell(w[i], 8, pealkirjad[i], 1, 0, 'C', True)
    pdf.ln()

    # 4. Tabeli sisu
    pdf.set_font("Helvetica", '', 7)
    for d in andmed:
        start_y = pdf.get_y()
        pdf.multi_cell(w[0], 7, d['oht'], 1)
        end_y = pdf.get_y()
        
        pdf.set_xy(pdf.get_x() + w[0], start_y)
        pdf.multi_cell(w[1], 7, d['märkus'][:30], 1) # Piirame teksti pikkust tabelis
        
        pdf.set_xy(pdf.get_x() + w[0] + w[1], start_y)
        pdf.cell(w[2], 7, d['seade'], 1)
        pdf.cell(w[3], 7, d['meede'], 1)
        pdf.cell(w[4], 7, str(d['t']), 1, 0, 'C')
        pdf.cell(w[5], 7, str(d['r']), 1, 0, 'C')
        
        # Värv skoorile
        if d['skoor'] >= 15: pdf.set_text_color(255, 0, 0)
        pdf.cell(w[6], 7, f"{d['skoor']}", 1, 1, 'C')
        pdf.set_text_color(0, 0, 0)

    # Pilt
    if foto:
        try:
            pdf.add_page()
            img = Image.open(foto)
            img = img.convert('RGB')
            img.thumbnail((500, 500)) # Surume pildi väiksemaks mobiili jaoks
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            pdf.image(img_byte_arr, x=10, y=20, w=180)
        except:
            st.warning("Pildi lisamine ebaõnnestus.")

    return pdf.output(dest='S').encode('latin-1', errors='ignore')

# --- NUPUD ---
st.markdown("### 🏁 Lõpetamine")
if st.button("🚀 GENEREERI PDF", use_container_width=True):
    pdf_data = generate_pdf()
    st.download_button(
        label="📥 Laadi PDF alla",
        data=pdf_data,
        file_name=f"Riskianalyys_{aadress}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
