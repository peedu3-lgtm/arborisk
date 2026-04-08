import streamlit as st
from fpdf import FPDF
import datetime
import requests
from PIL import Image
import io
import pytz

# --- 1. ASUKOHAD JA KELLAAEG ---
MAAKONNAD = {
    "Harjumaa": (59.33, 24.75), "Tartumaa": (58.37, 26.72), "Pärnumaa": (58.38, 24.50),
    "Ida-Virumaa": (59.35, 27.41), "Saaremaa": (58.25, 22.48), "Viljandimaa": (58.36, 25.59),
    "Lääne-Virumaa": (59.34, 26.35), "Võrumaa": (57.84, 27.00), "Raplamaa": (58.99, 24.79),
    "Järvamaa": (58.88, 25.56), "Läänemaa": (58.94, 23.54), "Jõgevamaa": (58.74, 26.39),
    "Põlvamaa": (58.05, 27.05), "Valgamaa": (57.77, 26.03), "Hiiumaa": (58.88, 22.59)
}

def get_eesti_aeg():
    try:
        eesti_tz = pytz.timezone('Europe/Tallinn')
        return datetime.datetime.now(eesti_tz).strftime("%H:%M")
    except:
        return datetime.datetime.now().strftime("%H:%M")

def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m&wind_speed_unit=ms"
        response = requests.get(url, timeout=3)
        data = response.json()
        return round(data['current']['wind_speed_10m'], 1), f"{data['current']['temperature_2m']}°C"
    except:
        return 0.0, "N/A"

# --- 2. ANDMETE VALIKUD ---
OHUD_BASE = [
    ["Kukkuvad oksad", "Puuvõra hooldus", 2, 4],
    ["Kukkumine", "Ronimine/tõstuk", 1, 5],
    ["Vale kukkumissuund", "Tüve langetamine", 1, 5],
    ["Müra ja Vibratsioon", "Tervisekahjustus", 3, 2],
    ["Isikud/Autod", "Vigastusoht ohualas", 2, 3],
    ["Võõras vara", "Löökkahjustus", 2, 3],
    ["Putukad", "Nõelamine/puugid", 2, 3],
    ["Elekter", "Õhuliinid läheduses", 1, 5]
]

TOORIISTAD = ["Mootorsaag", "Käsisaag", "Ronimisvarustus", "Korvtõstuk", "Hakkur", "Vints", "Kiilud", "Piirdelint", "Rigging", "Muu"]
MEETMED = ["Ohuala tähistamine", "IKV kandmine", "Varustuse kontroll", "Vintsimine", "Ohutu vahemaa", "Kõrvaklapid", "Sõidukite parkimine", "Vara kaitse", "Esmaabi", "Muu"]

# --- 3. UI ÜLESEHITUS ---
st.set_page_config(page_title="Arborisk Pro v7.0", layout="wide")
st.title("🌳 Arborisk Pro v7.0")

st.header("1. ÜLDISED ANDMED JA KONTAKT")
col1, col2 = st.columns(2)

with col2:
    valitud_maakond = st.selectbox("Vali maakond", list(MAAKONNAD.keys()))
    lat, lon = MAAKONNAD[valitud_maakond]
    auto_tuul, auto_temp = get_weather(lat, lon)
    tuul = st.number_input("Tuule kiirus (m/s)", value=auto_tuul)
    ilm_tekst = st.text_input("Ilm/Temp", value=auto_temp)
    haigla = st.text_input("Lähim EMO / Esmaabi", "")

with col1:
    tooaandja = st.text_input("Tööandja", "Framiter OÜ")
    vastutav = st.text_input("Vastutav isik / Teostaja", value="") 
    aadress = st.text_input("Objekti aadress", "")
    omanik_info = st.text_input("Tellija / Omaniku kontakt", "")
    kellaaeg = st.text_input("Töö algusaeg", value=get_eesti_aeg())

st.divider()

st.header("2. PUU JA KESKKONNA SEISUND")
col3, col4 = st.columns(2)
with col3:
    puu_liik = st.text_input("Puu liik")
    puu_korgus = st.number_input("Puu kõrgus (m)", min_value=0, value=20)
    puu_seisund = st.text_area("Seisund (seenhaigused, mädanik, kalle jne)")
with col4:
    ohuala = puu_korgus * 2
    st.metric("Ohuala raadius (m)", f"{ohuala} m")
    keskkond = st.text_area("Keskkond (teed, rajad, pinnas, hooned)")
    paaste_info = st.text_input("Ligipääs päästetele (värava koodid jne)")

st.divider()

st.header("3. RISKIDE HINDAMINE")
tabeli_andmed = []

for i, oht in enumerate(OHUD_BASE):
    with st.expander(f"📍 {oht[0]}", expanded=False):
        c1, c2, c3, c4, c5 = st.columns([1.5, 2, 2, 0.5, 0.5])
        with c1: 
            kirj = st.text_input("Kirjeldus", value=oht[1], key=f"k{i}")
        with c2:
            v_val = st.multiselect("Varustus", TOORIISTAD, key=f"v{i}")
            v_lisa = st.text_input("VÕI kirjuta ise varustus:", key=f"vl{i}")
            v_kokku = ", ".join(v_val) + (f" {v_lisa}" if v_lisa else "")
        with c3:
            m_val = st.multiselect("Meetmed", MEETMED, key=f"m{i}")
            m_lisa = st.text_input("VÕI kirjuta ise meede:", key=f"ml{i}")
            m_kokku = ", ".join(m_val) + (f" {m_lisa}" if m_lisa else "")
        with c4: t = st.selectbox("T", [1,2,3,4,5], index=oht[2]-1, key=f"t{i}")
        with c5: r = st.selectbox("R", [1,2,3,4,5], index=oht[3]-1, key=f"r{i}")
        
        skoor = t * r
        tabeli_andmed.append([oht[0], kirj, v_kokku, m_kokku, str(skoor)])
        st.write(f"Skoor: **{skoor}**")

foto = st.file_uploader("Lisa foto objektist", type=['jpg', 'jpeg', 'png'])

# --- 4. PDF GENEREERIMINE ---
def genereeri_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Täpitähtede tugi
    def enc(txt):
        return str(txt).encode('latin-1', 'replace').decode('latin-1')

    # Pealkiri
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 12, enc("TÖÖKOHA RISKIANALÜÜS"), ln=True, align='C')
    pdf.ln(5)

    # 1. Üldandmed (Suurem tekst ja reavahe)
    pdf.set_font("helvetica", 'B', 13)
    pdf.cell(0, 10, enc("1. ÜLDISED ANDMED"), ln=True)
    pdf.set_font("helvetica", '', 12)
    with pdf.table(col_widths=(55, 135), line_height=9) as table:
        table.row([enc("Tööandja"), enc(tooaandja)])
        table.row([enc("Vastutav / Teostaja"), enc(vastutav)])
        table.row([enc("Objekti aadress"), enc(aadress)])
        table.row([enc("Tellija / Omanik"), enc(omanik_info)])
        table.row([enc("Ilm / Aeg"), enc(f"{ilm_tekst}, {tuul} m/s | {datetime.date.today()} / {kellaaeg}")])

    # 2. Puu ja keskkond
    pdf.ln(8)
    pdf.set_font("helvetica", 'B', 13)
    pdf.cell(0, 10, enc("2. PUU JA KESKKONNA SEISUND"), ln=True)
    pdf.set_font("helvetica", '', 12)
    with pdf.table(col_widths=(55, 135), line_height=9) as table:
        table.row([enc("Puu liik & seisund"), enc(f"{puu_liik}: {puu_seisund}")])
        table.row([enc("Ohuala raadius"), enc(f"{ohuala} m")])
        table.row([enc("Keskkond / Ligipääs"), enc(f"{keskkond} | {paaste_info}")])

    # 3. Riskitabel (Suurem reavahe, loetav tekst)
    pdf.ln(8)
    pdf.set_font("helvetica", 'B', 13)
    pdf.cell(0, 10, enc("3. RISKIDE HINDAMISE TABEL"), ln=True)
    pdf.set_font("helvetica", '', 9)
    with pdf.table(col_widths=(30, 35, 40, 65, 20), line_height=7) as table:
        table.row([enc("Oht"), enc("Kirjeldus"), enc("Varustus"), enc("Meetmed"), enc("Skoor")])
        for rida in tabeli_andmed:
            table.row([enc(item) for item in rida])

    # Selgitused ja allkirjad
    pdf.ln(10)
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 5, enc("Skoor: 1-4 Madal | 5-12 Keskmine | 15-25 KÕRGE (TÖÖ KEELATUD!)"), ln=True)
    pdf.ln(10)
    pdf.cell(95, 10, enc("Koostaja allkiri: ........................."), 0, 0)
    pdf.cell(95, 10, enc("Töötaja allkiri: ........................."), 0, 1)

    if foto:
        pdf.add_page()
        img = Image.open(foto).convert("RGB")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        pdf.image(img_byte_arr, x=15, y=25, w=180)

    return pdf.output()

if st.button("🚀 GENEREERI LÕPLIK PDF"):
    output = genereeri_pdf()
    st.download_button("📥 LAADI ALLA PDF", bytes(output), f"Riskianalyys_{aadress}.pdf", "application/pdf")
