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
        self.set_font("helvetica", 'I', 8)
        self.cell(0, 5, f"Genereeritud: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True, align='R')
        self.ln(5)

# --- VALIKUD ---
toovahendid_valik = [
    "Mootorsaag", "Käsisaag", "Ronimisvarustus", "Korvtõstuk", "Hakkur", 
    "Kännufrees", "Vints", "Kiilud ja haamer", "Piirdelint/koonused", 
    "Viskeliin ja raskus", "Plokid ja rigging-köied", "Muu..."
]

meetmed_valik = [
    "Ohuala tähistamine ja piiramine", "Kõrvaliste isikute eemaldamine",
    "Isikukaitsevahendite (IKV) kandmine", "Varustuse eelnev kontroll",
    "Vintsimine ja suunamine", "Ohutu vahemaa hoidmine", 
    "Töö peatamine ebasobiva ilmaga", "Putukatõrjevahendi kasutamine", 
    "Esmaabikomplekti kontroll (allergia)", "Tööriiete kontroll (puugid)", "Muu..."
]

t_r_valikud = [1, 2, 3, 4, 5]

# --- ALUSANDMED (Uuendatud bioloogiliste ohtudega) ---
ohud_base = [
    ["Kukkuvad oksad ja ladvaosad", "Puuvõra hooldus", "Mootorsaag", "Ohuala tähistamine ja piiramine", 2, 3],
    ["Kõrgusest kukkumine", "Ronimine/tõstuk", "Ronimisvarustus", "Isikukaitsevahendite (IKV) kandmine", 1, 4],
    ["Puu langemine vales suunas", "Tüve langetamine", "Vints", "Vintsimine ja suunamine", 1, 5],
    ["Herilased / Mesilased", "Nõelamine (anafülaksia oht)", "Muu...", "Esmaabikomplekti kontroll (allergia)", 2, 3],
    ["Puugid / Lyme tõbi", "Bioloogiline oht", "Muu...", "Tööriiete kontroll (puugid)", 3, 2],
    ["Elektrilöök", "Õhuliinid läheduses", "Muu...", "Ohutu vahemaa hoidmine", 1, 5],
    ["Lõikevigastused", "Saega töötamine", "Mootorsaag", "Isikukaitsevahendite (IKV) kandmine", 2, 4],
    ["Kolmandad isikud / Liiklus", "Avalik ala", "Piirdelint/koonused", "Kõrvaliste isikute eemaldamine", 2, 2]
]

st.set_page_config(page_title="Arborisk Pro", layout="wide")
st.title("🌳 Arborisk Pro: Ohutusplaan")

# 1. ÜLDISED ANDMED
st.header("1. ÜLDISED ANDMED JA ESMAABI")
c1, c2 = st.columns(2)
with c1:
    tooaandja = st.text_input("Tööandja", "Aiavana Hooldusteenused OÜ")
    vastutav = st.text_input("Vastutav isik (pädev isik)", "Ivar Peedu")
    aadress = st.text_input("Objekti aadress", "")
    omanik_info = st.text_input("Objekti omanik ja kontakt", "")

with c2:
    haigla = st.text_input("Lähim haigla/EMO", "PERH / Tartu Ülikooli Kliinikum")
    esmaabi_koht = st.text_input("Esmaabivahendite asukoht", "Autos / Koostaja vööpaunal")
    juhis = st.text_area("Päästetee juhis", "Vaba ligipääs operatiivsõidukitele.")

st.divider()

# 2. RISKIDE HINDAMINE
st.header("2. RISKIDE HINDAMINE (T x R)")
tabeli_andmed = []

for i, oht in enumerate(ohud_base):
    with st.expander(f"📍 {oht[0]}", expanded=False):
        col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 0.6, 0.6])
        
        with col1:
            kirj = st.text_input("Ohu kirjeldus", value=oht[1], key=f"k{i}")
        with col2:
            v_val = st.selectbox("Töövahend", toovahendid_valik, index=toovahendid_valik.index(oht[2]) if oht[2] in toovahendid_valik else 0, key=f"v{i}")
            vahend = v_val if v_val != "Muu..." else st.text_input("Täpsusta vahendit", key=f"vc{i}")
        with col3:
            m_val = st.selectbox("Ennetusmeede", meetmed_valik, index=meetmed_valik.index(oht[3]) if oht[3] in meetmed_valik else 0, key=f"m{i}")
            meede = m_val if m_val != "Muu..." else st.text_input("Täpsusta meedet", key=f"mc{i}")
        with col4: 
            t = st.selectbox("T", t_r_valikud, index=t_r_valikud.index(oht[4]), key=f"t{i}")
        with col5: 
            r = st.selectbox("R", t_r_valikud, index=t_r_valikud.index(oht[5]), key=f"r{i}")
        
        skoor = t * r
        tase = "MADAL" if skoor <= 4 else "KESKMINE" if skoor <= 12 else "KÕRGE"
        color = "green" if tase == "MADAL" else "orange" if tase == "KESKMINE" else "red"
        st.markdown(f"Hinnang: :{color}[**{tase}**] (Skoor: {skoor})")
        
        tabeli_andmed.append([oht[0], kirj, vahend, meede, f"{t}x{r}={skoor} ({tase})"])

st.header("3. OBJEKTI FOTO")
foto = st.file_uploader("Lisa foto objektist (vajalik TI-le)", type=['jpg', 'jpeg', 'png'])

def genereeri_pdf():
    pdf = ArboristPDF()
    pdf.add_page()
    
    # 1. Üldandmed
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "1. ÜLDISED ANDMED", ln=True)
    pdf.set_font("helvetica", '', 10)
    with pdf.table(col_widths=(45, 145)) as table:
        table.row(["Tööandja", tooaandja])
        table.row(["Vastutav isik", vastutav])
        table.row(["Objekti aadress", aadress])
        table.row(["Omaniku info", omanik_info])
        table.row(["Lähim haigla", haigla])
        table.row(["Esmaabi asukoht", esmaabi_koht])

    pdf.ln(5)
    
    # 2. Riskitabel
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "2. RISKIDE HINDAMISE MAATRIKS", ln=True)
    pdf.set_font("helvetica", '', 7)
    with pdf.table(col_widths=(35, 30, 30, 65, 30)) as table:
        pdf.set_font("helvetica", 'B', 7)
        table.row(["Ohutegur", "Kirjeldus", "Töövahend", "Ennetusmeede", "Skoor (Hinnang)"])
        pdf.set_font("helvetica", '', 7)
        for rida in tabeli_andmed:
            # Värvime read vastavalt riskile
            if "KÕRGE" in rida[4]:
                pdf.set_fill_color(255, 204, 204)
            elif "KESKMINE" in rida[4]:
                pdf.set_fill_color(255, 255, 204)
            else:
                pdf.set_fill_color(255, 255, 255)
            table.row(rida)

    # 3. Allkirjad ja kinnitus
    pdf.ln(10)
    pdf.set_font("helvetica", 'B', 10)
    pdf.multi_cell(0, 5, "KINNITUS: Olen tutvunud riskianalüüsiga ja kohustun täitma ohutusnõudeid.")
    pdf.ln(5)
    pdf.cell(95, 10, f"Koostaja: {vastutav}", 0, 0)
    pdf.cell(95, 10, "Allkiri: .................................", 0, 1)
    pdf.ln(2)
    pdf.cell(95, 10, "Töötaja(d): .................................", 0, 0)
    pdf.cell(95, 10, "Allkiri: .................................", 0, 1)

    if foto:
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 11)
        pdf.cell(0, 10, "LISA: OBJEKTI FOTO", ln=True)
        img = Image.open(foto)
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        pdf.image(img_byte_arr, x=15, y=30, w=180)

    return pdf.output()

if st.button("🚀 GENEREERI JA KONTROLLI"):
    res = genereeri_pdf()
    st.success("Dokument on valmis!")
    st.download_button("📥 Laadi alla PDF (Tööinspektsioonile)", bytes(res), f"Riskianalyys_{aadress}.pdf", "application/pdf")
