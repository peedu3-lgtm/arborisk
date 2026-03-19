import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

# --- TÄPITÄHTEDEGA PDF KLASS ---
class ArboristPDF(FPDF):
    def header(self):
        # Kasutame fonti 'helvetica', 'B' (bold), suurus 14
        self.set_font("helvetica", 'B', 14)
        self.cell(0, 10, "TÖÖKOHA RISKIANALÜÜS JA OHUTUSPLAAN", ln=True, align='C')
        self.ln(5)

# --- VALIKUD RIPPMEENÜÜDESSE ---
toovahendid_valik = [
    "", "Mootorsaag", "Käsisaag", "Ronimisvarustus", "Tõstuk", "Hakkur", 
    "Kännufrees", "Vints", "Kiilud ja haamer", "Piirdelint/koonused", "Muu..."
]

meetmed_valik = [
    "", "Ohuala tähistamine ja piiramine", "Kõrvaliste isikute eemaldamine",
    "Isikukaitsevahendite (IKV) kasutamine", "Varustuse eelnev kontroll",
    "Vintsimine ja suunamine", "Liikluse reguleerimine",
    "Ohutu vahemaa hoidmine", "Liinide väljalülitus/maandamine", 
    "Töö peatamine ebasobiva ilmaga", "Muu..."
]

# --- RAKENDUSE LIIDES ---
st.set_page_config(page_title="Arborisk Pro", layout="wide")
st.title("🌳 Professionaalne Riskianalüüs")

# 1. ÜLDISED ANDMED
st.header("1. ÜLDISED ANDMED JA PÄÄSTE")
c1, c2 = st.columns(2)
with c1:
    tooaandja = st.text_input("Tööandja (Ettevõte)", "Aiavana Hooldusteenused OÜ")
    vastutav = st.text_input("Vastutav isik / Koostaja", "Ivar Peedu")
    aadress = st.text_input("Objekti aadress", "")
with c2:
    omanik = st.text_input("Objekti omanik ja kontakt", "")
    haigla = st.text_input("Lähim haigla / EMO", "PERH")
    juhis = st.text_area("Päästetee juhis", "Ligipääs tänavalt.")

st.divider()

# 2. RISKIDE HINDAMINE
st.header("2. RISKIDE HINDAMINE")

# Standardohud (LISATUD ILMASTIK JA PUU LANGETAMINE)
ohud_base = [
    ["Kukkuvad oksad ja ladvaosad", "Puuvõra hooldus/langetamine", "Mootorsaag, köied", "Ohuala tähistamine"],
    ["Kõrgusest kukkumine", "Ronimine või tõstukitöö", "Ronimisvarustus", "IKV kandmine, kontroll"],
    ["Puu langemine vales suunas", "Tüve langetamine", "Vints, kiilud", "Vintsimine ja suunamine"],
    ["Ilmastikuolud (tuul, jää, äike)", "Töö välitingimustes", "-", "Töö peatamine ebasobiva ilmaga"],
    ["Lõikevigastused", "Saega töötamine", "Mootorsaag", "Saekaitsepüksid, õige töövõte"],
    ["Elektrilöök", "Töö liinide läheduses", "-", "Ohutu vahemaa hoidmine"],
    ["Kõrvalised isikud / Liiklus", "Töö avalikus kohas", "Piirdelind", "Piiramine ja reguleerimine"]
]

tabeli_andmed = []
for i, oht in enumerate(ohud_base):
    with st.expander(f"📍 {oht[0]}", expanded=True):
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 0.7, 0.7])
        
        with col1:
            kirjeldus = st.text_input("Ohu kirjeldus", value=oht[1], key=f"k{i}")
        with col2:
            v_valik = st.selectbox("Töövahend", toovahendid_valik, index=toovahendid_valik.index(oht[2]) if oht[2] in toovahendid_valik else 0, key=f"v{i}")
            vahend = v_valik if v_valik != "Muu..." else st.text_input("Täpsusta vahendit", key=f"vc{i}")
        with col3:
            m_valik = st.selectbox("Ennetusmeede", meetmed_valik, index=meetmed_valik.index(oht[3]) if oht[3] in meetmed_valik else 0, key=f"m{i}")
            meede = m_valik if m_valik != "Muu..." else st.text_input("Täpsusta meedet", key=f"mc{i}")
        with col4: t = st.number_input("T", 1, 5, 2, key=f"t{i}")
        with col5: r = st.number_input("R", 1, 5, 3, key=f"r{i}")
        
        skoor = t * r
        tabeli_andmed.append([oht[0], kirjeldus, vahend, meede, f"{t}x{r}={skoor}"])

st.header("3. OBJEKTI FOTO")
foto = st.file_uploader("Vali pilt (JPG/PNG)", type=['jpg', 'jpeg', 'png'])

# --- PDF GENEREERIMINE ---
def genereeri_pdf():
    pdf = ArboristPDF()
    pdf.add_page()
    
    # Määrame fondi, mis toetab täpitähti (latin-1 asemel kasutab fpdf2 automaatselt asendust)
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "1. ÜLDISED ANDMED JA PÄÄSTEINFO", ln=True)
    pdf.set_font("helvetica", '', 10)
    
    with pdf.table(col_widths=(45, 145)) as table:
        table.row(["Tööandja", tooaandja])
        table.row(["Vastutav isik", vastutav])
        table.row(["Objekti aadress", aadress])
        table.row(["Objekti omanik", omanik])
        table.row(["Lähim haigla", haigla])
        table.row(["Päästetee juhis", juhis])
        table.row(["Kuupäev", str(datetime.date.today())])

    pdf.ln(8)
    
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "2. RISKIDE HINDAMISE MAATRIKS", ln=True)
    pdf.set_font("helvetica", '', 8)
    
    with pdf.table(col_widths=(35, 35, 35, 65, 20)) as table:
        pdf.set_font("helvetica", 'B', 8)
        table.row(["Ohutegur", "Kirjeldus", "Töövahend", "Ennetusmeede", "Skoor"])
        pdf.set_font("helvetica", '', 8)
        for rida in tabeli_andmed:
            table.row(rida)

    pdf.ln(8)
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 8, "RISKIHINDAMISE SELGITUSED (T x R)", ln=True)
    pdf.set_font("helvetica", '', 7)
    with pdf.table(col_widths=(95, 95)) as table:
        table.row(["T (Tõenäosus)", "R (Raskusaste / Tagajärg)"])
        table.row(["1-Väga väike; 2-Väike; 3-Keskmine; 4-Suur; 5-Väga suur", "1-Ebaoluline; 2-Kerge; 3-Keskmine; 4-Raske; 5-Surm"])
    
    pdf.ln(5)
    pdf.set_font("helvetica", 'I', 8)
    pdf.cell(0, 5, "Riskitase: 1-4 Madal; 5-12 Keskmine; 15-25 Kõrge (TÖÖ KEELATUD!)", ln=True)

    if foto:
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 11)
        pdf.cell(0, 10, "3. OBJEKTI FOTO", ln=True)
        img = Image.open(foto)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        pdf.image(img_byte_arr, x=15, y=30, w=180)

    pdf.ln(20)
    pdf.set_font("helvetica", 'B', 9)
    pdf.cell(95, 10, "Koostaja allkiri: .................................", 0, 0)
    pdf.cell(95, 10, "Töötaja allkiri: .................................", 0, 1)
    
    return pdf.output()

if st.button("🚀 GENEREERI RISKIANALÜÜS"):
    try:
        pdf_res = genereeri_pdf()
        st.download_button(
            label="📥 Laadi alla PDF",
            data=bytes(pdf_res),
            file_name=f"Riskianalyys_{aadress}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Viga PDF-i loomisel: {e}")
