import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

# --- 1. SEADISTUS JA ANDMED ---
# See osa peab olema kõige ees!
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

# Baasohud, mis ilmuvad äpis automaatselt
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

# --- 2. PDF KLASS ---
class ArboristPDF(FPDF):
    def header(self):
        self.set_font("helvetica", 'B', 14)
        self.cell(0, 10, "TÖÖKOHA RISKIANALÜÜS JA OHUTUSPLAAN", ln=True, align='C')
        self.ln(5)

# --- 3. KASUTAJALIIDES (Streamlit) ---
st.set_page_config(page_title="Arborisk Pro", layout="wide")
st.title("🌳 Arborisk Pro: Ohutusplaan")

st.header("1. ÜLDISED ANDMED JA ESMAABI")
col_a, col_b = st.columns(2)
with col_a:
    tooaandja = st.text_input("Tööandja", "Aiavana Hooldusteenused OÜ")
    vastutav = st.text_input("Vastutav isik", "Ivar Peedu")
    aadress = st.text_input("Objekti aadress", "")
    omanik = st.text_input("Omaniku info", "")
with col_b:
    haigla = st.text_input("Lähim haigla/EMO", "PERH / TÜ Kliinikum")
    esmaabi = st.text_input("Esmaabivahendite asukoht", "Autos / Vööpaunal")
    juhis = st.text_area("Päästetee juhis", "Ligipääs tänavalt.")

st.divider()

st.header("2. RISKIDE HINDAMINE (T x R)")
tabeli_andmed = []

# Käime läbi kõik baasohud ja loome neile sisestusväljad
for i, oht in enumerate(ohud_base):
    with st.expander(f"📍 {oht[0]}", expanded=False):
        c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 0.5, 0.5])
        
        with c1:
            kirjeldus = st.text_input("Ohu kirjeldus", value=oht[1], key=f"k{i}")
        
        with c2:
            v_valitud = st.multiselect("Töövahendid", toovahendid_valik, default=[oht[2]] if oht[2] in toovahendid_valik else [], key=f"v{i}")
            v_lisa = st.text_input("Lisa muu vahend", key=f"vl{i}")
            vahendid_str = ", ".join(v_valitud) + (f", {v_lisa}" if v_lisa else "")

        with c3:
            m_valitud = st.multiselect("Meetmed", meetmed_valik, default=[oht[3]] if oht[3] in meetmed_valik else [], key=f"m{i}")
            m_lisa = st.text_input("Lisa muu meede", key=f"ml{i}")
            meetmed_str = ", ".join(m_valitud) + (f", {m_lisa}" if m_lisa else "")
            
        with c4: 
            t = st.selectbox("T", t_r_valikud, index=t_r_valikud.index(oht[4]), key=f"t{i}")
        with c5: 
            r = st.selectbox("R", t_r_valikud, index=t_r_valikud.index(oht[5]), key=f"r{i}")
        
        skoor = t * r
        tase = "MADAL" if skoor <= 4 else "KESKMINE" if skoor <= 12 else "KÕRGE"
        st.write(f"Skoor: **{skoor}** | Hinnang: **{tase}**")
        
        tabeli_andmed.append([oht[0], kirjeldus, vahendid_str, meetmed_str, f"{skoor} ({tase})"])

st.header("3. OBJEKTI FOTO")
foto = st.file_uploader("Lisa foto", type=['jpg', 'jpeg', 'png'])

# --- 4. PDF GENEREERIMINE ---
def loe_pdf():
    pdf = ArboristPDF()
    pdf.add_page()
    
    # Üldinfo
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "1. ÜLDISED ANDMED", ln=True)
    pdf.set_font("helvetica", '', 10)
    with pdf.table(col_widths=(45, 145)) as table:
        table.row(["Tööandja", tooaandja])
        table.row(["Vastutav isik", vastutav])
        table.row(["Aadress", aadress])
        table.row(["Haigla/Esmaabi", f"{haigla} / {esmaabi}"])
        table.row(["Kuupäev", str(datetime.date.today())])

    pdf.ln(5)
    
    # Riskid
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "2. RISKIDE HINDAMINE", ln=True)
    pdf.set_font("helvetica", '', 7)
    with pdf.table(col_widths=(35, 30, 40, 60, 25)) as table:
        table.row(["Ohutegur", "Kirjeldus", "Vahendid", "Meetmed", "Skoor"])
        for rida in tabeli_andmed:
            table.row(rida)

    # Allkirjad
    pdf.ln(10)
    pdf.cell(95, 10, "Koostaja allkiri: .........................", 0, 0)
    pdf.cell(95, 10, "Töötaja allkiri: .........................", 0, 1)

    if foto:
        pdf.add_page()
        img = Image.open(foto).convert("RGB")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        pdf.image(img_byte_arr, x=15, y=20, w=180)

    return pdf.output()

if st.button("🚀 GENEREERI PDF"):
    output = loe_pdf()
    st.download_button("📥 Laadi alla", bytes(output), "Riskianalyys.pdf", "application/pdf")
