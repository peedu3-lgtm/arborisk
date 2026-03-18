import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

# --- PROFESSIONAALNE PDF KLASS ---
class ArboristPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 14)
        self.cell(0, 10, "RISKIANALÜÜS PUUHOOLDUSTÖÖDEL", ln=True, align='L')
        self.ln(2)

    def draw_info_row(self, label, value, width=190):
        self.set_font("Helvetica", 'B', 9)
        self.cell(50, 8, label, 1, 0, 'L')
        self.set_font("Helvetica", '', 9)
        self.cell(width-50, 8, str(value), 1, 1, 'L')

# --- ÄPI LIIDES ---
st.set_page_config(page_title="Arboristi Riskianalüüs", layout="centered")

with st.sidebar:
    st.header("📋 Üldinfo")
    ettevote = st.text_input("Ettevõte", "Arboristiabi OÜ")
    tellija = st.text_input("Tellija nimi ja telefon")
    aadress = st.text_input("Objekti aadress")
    too_kirjeldus = st.text_input("Tehtav töö")
    tootajad = st.text_input("Töötajad objektil")
    vastutav = st.text_input("Vastutav isik")
    abitool = st.text_input("Abitelefon", "112 või lähim arborist...")
    kuupaev = st.date_input("Kuupäev", datetime.date.today())
    
    st.divider()
    st.header("📸 Lisa foto")
    foto = st.file_uploader("Vali fail", type=['jpg', 'jpeg', 'png'])

st.title("🌳 Riskide hindamine objektil")

# Tabeli sisu koostamine (Vastavalt sinu saadetud vormile)
valdkonnad = [
    ("Ohuala märgistused", "Mootorsaag"),
    ("Ilmaolud", "Ronimisvarustus"),
    ("Puu liik, seisund (mädanik jne)", "Sektsiooniline langetamine"),
    ("Hooned, vara asukoht", "Vints"),
    ("Tehnovõrgud (liinid, trassid)", "Kemikaalid"),
    ("Teed, liiklusthedus", "Tõstuk"),
    ("Pinnase seisund, kalle", "Hakkur / Oksapurusti"),
    ("Naaberpuude seisund", "Kännufrees"),
    ("Looduskaitselised väärtused", "Kraana"),
    ("Bioloogilised ohud (herilased)", "Muud mehhanismid"),
    ("Kõrvalised isikud objektil", "Isikukaitsevahendid")
]

andmed = []
for silt_oht, silt_seade in valdkonnad:
    st.markdown(f"### {silt_oht}")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        kirjeldus = st.text_input("Eripära kirjeldus", key=silt_oht+"_k")
    with col2:
        t = st.selectbox("T (1-5)", [1,2,3,4,5], key=silt_oht+"_t", index=0)
    with col3:
        r = st.selectbox("R (1-5)", [1,2,3,4,5], key=silt_oht+"_r", index=1)
    
    risk_tase = "MADAL" if t*r <= 4 else "KESKMINE" if t*r <= 12 else "KÕRGE"
    andmed.append({
        "valdkond": silt_oht,
        "kirjeldus": kirjeldus,
        "seade": silt_seade,
        "tase": risk_tase,
        "skoor": f"{t}x{r}={t*r}"
    })
    st.divider()

# --- PDF LOOMINE ---
def genereeri_puhas_pdf():
    pdf = ArboristPDF()
    pdf.add_page()
    
    # 1. Ülapaneel (Üldinfo)
    pdf.draw_info_row("Ettevõte", ettevote)
    pdf.draw_info_row("Tellija nimi ja tel", tellija)
    pdf.draw_info_row("Objekti aadress", aadress)
    pdf.draw_info_row("Tehtav töö", too_kirjeldus)
    pdf.draw_info_row("Töötajad objektil", tootajad)
    pdf.draw_info_row("Vastutav isik", vastutav)
    pdf.draw_info_row("Abitelefon", abitool)
    pdf.draw_info_row("Kuupäev", str(kuupaev))
    pdf.ln(5)

    # 2. Riskide tabeli päis
    pdf.set_font("Helvetica", 'B', 8)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(50, 10, "Tööala eripära", 1, 0, 'C', True)
    pdf.cell(60, 10, "Kirjeldus", 1, 0, 'C', True)
    pdf.cell(40, 10, "Kasutatav seade", 1, 0, 'C', True)
    pdf.cell(40, 10, "Riskitase (TxR)", 1, 1, 'C', True)

    # 3. Tabeli read (Dünaamilise kõrgusega)
    pdf.set_font("Helvetica", '', 8)
    for r in andmed:
        # Arvutame vajaliku kõrguse vastavalt tekstile
        text_height = 8 
        
        # Joonistame lahtrid
        curr_x = pdf.get_x()
        curr_y = pdf.get_y()
        
        pdf.multi_cell(50, text_height, r['valdkond'], 1, 'L')
        pdf.set_xy(curr_x + 50, curr_y)
        pdf.multi_cell(60, text_height, r['kirjeldus'], 1, 'L')
        pdf.set_xy(curr_x + 110, curr_y)
        pdf.multi_cell(40, text_height, r['seade'], 1, 'L')
        pdf.set_xy(curr_x + 150, curr_y)
        
        # Värvime riskitaseme
        if r['tase'] == "KÕRGE": pdf.set_text_color(200, 0, 0)
        elif r['tase'] == "KESKMINE": pdf.set_text_color(150, 100, 0)
        else: pdf.set_text_color(0, 120, 0)
        
        pdf.cell(40, text_height, f"{r['tase']} ({r['skoor']})", 1, 1, 'C')
        pdf.set_text_color(0, 0, 0)

    # 4. Pilt eraldi lehel
    if foto:
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 10, "OBJEKTI FOTO", ln=True)
        img = Image.open(foto)
        # Muudame pildi suurust, et see mahuks lehele
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        pdf.image(img_byte_arr, x=15, y=30, w=180)

    pdf.ln(10)
    pdf.set_font("Helvetica", 'I', 9)
    pdf.cell(0, 10, f"Riskianalüüsi koostas: {vastutav} ......................................... Kuupäev: {kuupaev}", ln=True)

    return pdf.output()

if st.button("✅ GENEREERI PDF"):
    pdf_bytes = genereeri_puhas_pdf()
    st.download_button(
        label="📥 Laadi alla korrektne PDF",
        data=bytes(pdf_bytes),
        file_name=f"Riskianalyys_{aadress}.pdf",
        mime="application/pdf"
    )
