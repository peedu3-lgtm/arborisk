import streamlit as st
from fpdf import FPDF
import datetime
import io

# --- KORREKTNE PDF KLASS TÄPITÄHTEDEGA ---
class ArboristPDF(FPDF):
    def header(self):
        # Helvetica toetab täpitähti fpdf2 raamistikus automaatselt
        self.set_font("Helvetica", 'B', 14)
        self.cell(0, 10, "TÖÖKOHA RISKIANALÜÜS JA OHUTUSPLAAN", ln=True, align='C')
        self.ln(5)

# --- ÄPI LIIDES ---
st.set_page_config(page_title="Arboristi Riskianalüüs", layout="wide")

st.header("1. ÜLDISED ANDMED")
col_a, col_b = st.columns(2)
with col_a:
    tooaandja = st.text_input("Tööandja", "")
    vastutav = st.text_input("Vastutav isik", "")
    aadress = st.text_input("Objekti aadress", "")
with col_b:
    omanik = st.text_input("Objekti omanik ja kontakt", "")
    haigla = st.text_input("Lähim haigla / EMO", "")
    juhis = st.text_area("Päästetee juhis / Kirjeldus", "")

st.divider()
st.header("2. RISKIDE HINDAMINE")

# Tühi nimekiri, mida kasutaja hakkab täitma
ohud_list = [
    "Ohuala märgistus ja piiramine",
    "Ilmastikuolud (tuul, sademed)",
    "Puu seisund (mädanik, tüvevead)",
    "Hooned ja lähedalasuv vara",
    "Elektriliinid ja tehnovõrgud",
    "Liiklus ja kõrvalised isikud",
    "Pinnase seisund ja kalle",
    "Müra ja vibratsioon"
]

tabeli_sisu = []
for i, oht in enumerate(ohud_list):
    with st.expander(f"📍 {oht}", expanded=True):
        c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 3, 0.7, 0.7])
        with c1: st.write(f"**{oht}**")
        with c2: kirjan = st.text_input("Kirjeldus", key=f"k{i}")
        with c3: vahen = st.text_input("Töövahend", key=f"v{i}")
        with c4: meede = st.text_area("Meetmed", key=f"m{i}")
        with c5: t_val = st.number_input("T", 1, 5, 1, key=f"t{i}")
        with c6: r_val = st.number_input("R", 1, 5, 1, key=f"r{i}")
        
        skoor = t_val * r_val
        tabeli_sisu.append([oht, kirjan, vahen, meede, f"{t_val}x{r_val}={skoor}"])

def genereeri_pdf():
    pdf = ArboristPDF()
    pdf.add_page()
    
    # 1. Üldandmed
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(0, 8, "1. ÜLDISED ANDMED JA PÄÄSTEINFO", ln=True)
    pdf.set_font("Helvetica", '', 10)
    with pdf.table(col_widths=(45, 145), border=1) as table:
        table.row(["Tööandja", tooaandja])
        table.row(["Vastutav isik", vastutav])
        table.row(["Objekti aadress", aadress])
        table.row(["Objekti omanik", omanik])
        table.row(["Lähim haigla", haigla])
        table.row(["Päästetee juhis", juhis])
        table.row(["Kuupäev", str(datetime.date.today())])

    pdf.ln(10)
    
    # 2. Riskide tabel
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(0, 8, "2. RISKIDE HINDAMINE", ln=True)
    pdf.set_font("Helvetica", '', 8)
    
    with pdf.table(col_widths=(35, 35, 35, 65, 20), border=1) as table:
        pdf.set_font("Helvetica", 'B', 8)
        table.row(["Ohutegur", "Kirjeldus", "Töövahend", "Meetmed", "Skoor (TxR)"])
        pdf.set_font("Helvetica", '', 8)
        for rida in tabeli_sisu:
            table.row(rida)

    # 3. T ja R selgitused (Lisasin need siia, et dokument oleks täielik)
    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(0, 8, "RISKIHINDAMISE SELGITUSED (T x R)", ln=True)
    pdf.set_font("Helvetica", '', 8)
    
    with pdf.table(col_widths=(95, 95), border=1) as table:
        table.row(["T (Tõenäosus)", "R (Raskusaste / Tagajärg)"])
        table.row(["1 - Väga väike (peaaegu võimatu)", "1 - Ebaoluline (ei vaja esmaabi)"])
        table.row(["2 - Väike (juhtub harva)", "2 - Kerge (vajab esmaabi / lühike puhkus)"])
        table.row(["3 - Keskmine (võib juhtuda)", "3 - Keskmine (luumurd, haiglaravi)"])
        table.row(["4 - Suur (juhtub sageli)", "4 - Raske (püsiv tervisekahjustus)"])
        table.row(["5 - Väga suur (kindel õnnetus)", "5 - Katastroofiline (surm)"])

    pdf.ln(5)
    pdf.set_font("Helvetica", 'I', 8)
    pdf.multi_cell(0, 5, "Riskitase: 1-4 Madal (lubatud); 5-12 Keskmine (vajab lisameetmeid); 15-25 Kõrge (TÖÖ KEELATUD!)")

    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 9)
    pdf.cell(95, 10, "Koostaja allkiri: .................................", 0, 0)
    pdf.cell(95, 10, "Töötaja allkiri: .................................", 0, 1)

    return pdf.output()

if st.button("🚀 GENEREERI RISKIANALÜÜS"):
    pdf_bytes = genereeri_pdf()
    st.download_button(
        label="📥 Laadi alla PDF",
        data=bytes(pdf_bytes),
        file_name=f"Riskianalyys_{aadress}.pdf",
        mime="application/pdf"
    )
