import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

# --- PDF KLASS ---
class ArboristPDF(FPDF):
    def header(self):
        self.set_font("helvetica", 'B', 14)
        self.cell(0, 10, "TÖÖKOHA RISKIANALÜÜS JA OHUTUSPLAAN", ln=True, align='C')
        self.ln(5)

# --- VALIKUD RIPPMEENÜÜDESSE ---
toovahendid_valik = [
    "Mootorsaag", "Käsisaag", "Ronimisvarustus", "Korvtõstuk", "Hakkur", 
    "Vints", "Kiilud ja haamer", "Piirdelint/koonused", "Muu..."
]

meetmed_valik = [
    "Ohuala tähistamine ja piiramine", "Kõrvaliste isikute eemaldamine",
    "Isikukaitsevahendite (IKV) kandmine", "Varustuse eelnev kontroll",
    "Vintsimine ja suunamine", "Ohutu vahemaa hoidmine", 
    "Töö peatamine ebasobiva ilmaga", "Muu..."
]

st.set_page_config(page_title="Arborisk Pro", layout="wide")
st.title("🌳 Professionaalne Riskianalüüs")

# 1. ÜLDISED ANDMED
st.header("1. ÜLDISED ANDMED JA ESMAABI")
c1, c2 = st.columns(2)
with c1:
    tooaandja = st.text_input("Tööandja", "Aiavana Hooldusteenused OÜ")
    vastutav = st.text_input("Vastutav isik", "Ivar Peedu")
    aadress = st.text_input("Objekti aadress", "")
with c2:
    haigla = st.text_input("Lähim haigla/EMO", "PERH")
    esmaabi_koht = st.text_input("Esmaabivahendite asukoht", "Autos / Koostaja vööpaunal")
    juhis = st.text_area("Päästetee juhis", "Ligipääs tänavalt.")

st.divider()

# 2. RISKIDE HINDAMINE
st.header("2. RISKIDE HINDAMINE (T x R)")

# Põhjalik nimekiri standardohtudest
ohud_base = [
    ["Kukkuvad oksad ja ladvaosad", "Puuvõra hooldus", "Mootorsaag", "Ohuala tähistamine ja piiramine"],
    ["Kõrgusest kukkumine", "Ronimine/tõstuk", "Ronimisvarustus", "Isikukaitsevahendite (IKV) kandmine"],
    ["Puu langemine vales suunas", "Tüve langetamine", "Vints", "Vintsimine ja suunamine"],
    ["Ilmastikuolud", "Tuul, äike, jää", "Muu...", "Töö peatamine ebasobiva ilmaga"],
    ["Lõikevigastused", "Saega töötamine", "Mootorsaag", "Isikukaitsevahendite (IKV) kandmine"],
    ["Elektrilöök", "Õhuliinid", "Muu...", "Ohutu vahemaa hoidmine"],
    ["Kolmandad isikud / Liiklus", "Avalik ala", "Piirdelint/koonused", "Kõrvaliste isikute eemaldamine"],
    ["Müra ja vibratsioon", "Seadmete kasutus", "Hakkur", "Isikukaitsevahendite (IKV) kandmine"]
]

tabeli_andmed = []
for i, oht in enumerate(ohud_base):
    with st.expander(f"📍 {oht[0]}", expanded=False):
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 0.7, 0.7])
        
        with col1:
            kirj = st.text_input("Kirjeldus", value=oht[1], key=f"k{i}")
        
        with col2:
            v_val = st.selectbox("Töövahend", toovahendid_valik, index=toovahendid_valik.index(oht[2]) if oht[2] in toovahendid_valik else 0, key=f"v{i}")
            vahend = v_val if v_val != "Muu..." else st.text_input("Täpsusta vahendit", key=f"vc{i}")
        
        with col3:
            m_val = st.selectbox("Ennetusmeede", meetmed_valik, index=meetmed_valik.index(oht[3]) if oht[3] in meetmed_valik else 0, key=f"m{i}")
            meede = m_val if m_val != "Muu..." else st.text_input("Täpsusta meedet", key=f"mc{i}")
            
        with col4: t = st.number_input("T", 1, 5, 2, key=f"t{i}")
        with col5: r = st.number_input("R", 1, 5, 2, key=f"r{i}")
        
        skoor = t * r
        tase = "MADAL" if skoor <= 4 else "KESKMINE" if skoor <= 12 else "KÕRGE"
        tabeli_andmed.append([oht[0], kirj, vahend, meede, f"{t}x{r}={skoor} ({tase})"])

st.header("3. OBJEKTI FOTO")
foto = st.file_uploader("Lisa foto", type=['jpg', 'jpeg', 'png'])

def genereeri_pdf():
    pdf = ArboristPDF()
    pdf.add_page()
    
    # 1. Üldandmed
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "1. ÜLDISED ANDMED JA PÄÄSTEINFO", ln=True)
    pdf.set_font("helvetica", '', 10)
    with pdf.table(col_widths=(45, 145)) as table:
        table.row(["Tööandja", tooaandja])
        table.row(["Vastutav isik", vastutav])
        table.row(["Objekti aadress", aadress])
        table.row(["Esmaabi asukoht", esmaabi_koht])
        table.row(["Päästetee juhis", juhis])
        table.row(["Kuupäev", str(datetime.date.today())])

    pdf.ln(8)
    
    # 2. Riskitabel
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "2. RISKIDE HINDAMISE MAATRIKS", ln=True)
    pdf.set_font("helvetica", '', 8)
    with pdf.table(col_widths=(35, 30, 30, 60, 35)) as table:
        pdf.set_font("helvetica", 'B', 8)
        table.row(["Ohutegur", "Kirjeldus", "Töövahend", "Ennetusmeede", "Skoor (Hinnang)"])
        pdf.set_font("helvetica", '', 8)
        for rida in tabeli_andmed:
            table.row(rida)

    # 3. Selgitused ja allkirjad
    pdf.ln(8)
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 8, "RISKIHINDAMISE SELGITUSED", ln=True)
    pdf.set_font("helvetica", '', 7)
    with pdf.table(col_widths=(95, 95)) as table:
        table.row(["T (Tõenäosus)", "R (Raskusaste)"])
        table.row(["1-Väga väike; 2-Väike; 3-Keskmine; 4-Suur; 5-Väga suur", "1-Ebaoluline; 2-Kerge; 3-Keskmine; 4-Raske; 5-Surm"])
    
    pdf.ln(4)
    pdf.set_font("helvetica", 'I', 8)
    pdf.cell(0, 5, "Hinnang: 1-4 Madal; 5-12 Keskmine; 15-25 Kõrge (KEELATUD!)", ln=True)

    pdf.ln(10)
    pdf.set_font("helvetica", 'B', 9)
    pdf.cell(95, 10, "Koostaja allkiri: .................................", 0, 0)
    pdf.cell(95, 10, "Töötaja allkiri: .................................", 0, 1)

    if foto:
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 11)
        pdf.cell(0, 10, "3. OBJEKTI FOTO", ln=True)
        img = Image.open(foto)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        pdf.image(img_byte_arr, x=15, y=30, w=180)

    return pdf.output()

if st.button("🚀 GENEREERI LÕPLIK PDF"):
    res = genereeri_pdf()
    st.download_button("📥 Laadi alla", bytes(res), f"Riskianalyys_{aadress}.pdf", "application/pdf")
