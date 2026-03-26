import streamlit as st
from fpdf import FPDF
import datetime
import requests
from PIL import Image
import io
import pytz

# --- 0. ASUKOHAD JA KELLAAEG ---
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
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,wind_speed_10m&wind_speed_unit=ms"
        response = requests.get(url, timeout=5)
        data = response.json()
        current = data['current']
        w_code = current['weather_code']
        # Tõlgime koodid tekstiks
        if w_code == 0: ilm = "Selge"
        elif w_code in [1, 2, 3]: ilm = "Vahelduv pilvisus"
        elif w_code in [61, 63, 65]: ilm = "Vihmasadu"
        elif w_code in [71, 73, 75]: ilm = "Lumesadu"
        else: ilm = "Pilves"
        return round(current['wind_speed_10m'], 1), ilm, round(current['temperature_2m'], 1)
    except:
        return 0.0, "Määra käsitsi", 0.0

# --- 1. SEADISTUSED ---
toovahendid_valik = ["Mootorsaag", "Käsisaag", "Ronimisvarustus", "Korvtõstuk", "Hakkur", "Kännufrees", "Vints", "Kiilud ja haamer", "Piirdelint/koonused", "Plokid ja rigging-köied", "Muu..."]
meetmed_valik = ["Ohuala tähistamine", "IKV kandmine", "Varustuse kontroll", "Vintsimine", "Ohutu vahemaa hoidmine", "Töö peatamine", "Kõrvaklapid", "Sõidukite parkimine", "Vara kaitse", "Esmaabikomplekt", "Allergiaravimid", "Muu..."]

ohud_base = [
    ["Kukkuvad oksad", "Puuvõra hooldus", "Mootorsaag", "Ohuala tähistamine", 2, 4],
    ["Kukkumine", "Ronimine/tõstuk", "Ronimisvarustus", "IKV kandmine", 1, 5],
    ["Vale kukkumissuund", "Langetamine", "Vints", "Vintsimine", 1, 5],
    ["Müra ja Vibratsioon", "Tervisekahjustus", "Mootorsaag", "Kõrvaklapid", 3, 2],
    ["Kõrvalised isikud / Autod", "Vigastused ja varaline kahju", "Piirdelint", "Ohuala tähistamine", 2, 3],
    ["Vara (aiad, katused)", "Löökkahjustused", "Plokid ja rigging", "Vara kaitse", 2, 3],
    ["Herilased / Puugid", "Nõelamine / bioloogiline oht", "Muu...", "Allergiaravimid", 2, 3],
    ["Elektrilöök", "Õhuliinid läheduses", "Muu...", "Ohutu vahemaa", 1, 5]
]

# --- 2. PDF ---
class ArboristPDF(FPDF):
    def header(self):
        self.set_font("helvetica", 'B', 14)
        h_text = "TÖÖKOHA RISKIANALÜÜS JA OHUTUSPLAAN".encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 10, h_text, ln=True, align='C')

# --- 3. UI ---
st.set_page_config(page_title="Arborisk Pro", layout="wide")
st.title("🌳 Arborisk Pro v5.6")

st.header("1. ÜLDISED ANDMED JA ILM")
col_a, col_b = st.columns(2)

with col_b:
    valitud_maakond = st.selectbox("Vali maakond", list(MAAKONNAD.keys()))
    lat, lon = MAAKONNAD[valitud_maakond]
    auto_tuul, auto_ilm, auto_temp = get_weather(lat, lon)
    
    tuul = st.number_input("Tuule kiirus (m/s)", value=auto_tuul)
    ilm_tekst = st.text_input("Ilm ja temp", value=f"{auto_ilm}, {auto_temp}C")
    haigla = st.text_input("Lähim EMO", "PERH / TÜ Kliinikum")

with col_a:
    tooaandja = st.text_input("Tööandja", "Aiavana Hooldusteenused OÜ")
    vastutav = st.text_input("Vastutav isik", "Ivar Peedu")
    aadress = st.text_input("Objekti aadress", "")
    omanik_info = st.text_input("Omaniku kontakt", "")
    kellaaeg = st.text_input("Töö algusaeg", value=get_eesti_aeg())

st.divider()

# --- UUS: PUU JA KESKKOND ---
st.header("2. PUU JA KESKKONNA SEISUND")
col_c, col_d = st.columns(2)
with col_c:
    puu_andmed = st.text_area("Puu liik, mõõtmed ja seisund", 
        placeholder="Seenhaigused, õõnsused, mädanik, kalle jne...")
with col_d:
    keskkond_andmed = st.text_area("Teed, rajad ja pinnas", 
        placeholder="Liiklus, pinnase kalle, kaugus hoonetest...")

st.divider()

st.header("3. RISKIDE HINDAMINE")
tabeli_andmed = []
for i, oht in enumerate(ohud_base):
    with st.expander(f"📍 {oht[0]}", expanded=False):
        c1, c2, c3, c4, c5 = st.columns([1.5, 2, 2, 0.5, 0.5])
        with c1: kirj = st.text_input("Kirjeldus", value=oht[1], key=f"k{i}")
        with c2:
            v_val = st.multiselect("Varustus", toovahendid_valik, default=[oht[2]] if oht[2] in toovahendid_valik else [], key=f"v{i}")
            v_kokku = ", ".join(v_val)
        with c3:
            m_val = st.multiselect("Meetmed", meetmed_valik, default=[oht[3]] if oht[3] in meetmed_valik else [], key=f"m{i}")
            m_kokku = ", ".join(m_val)
        with c4: t = st.selectbox("T", [1,2,3,4,5], index=oht[4]-1, key=f"t{i}")
        with c5: r = st.selectbox("R", [1,2,3,4,5], index=oht[5]-1, key=f"r{i}")
        sk = t * r
        st.write(f"Skoor: **{sk}**")
        tabeli_andmed.append([oht[0], kirj, v_kokku, m_kokku, f"{sk}"])

foto = st.file_uploader("Lisa foto objektist", type=['jpg', 'jpeg', 'png'])

def loe_pdf():
    pdf = ArboristPDF()
    pdf.add_page()
    def enc(txt): return str(txt).encode('latin-1', 'replace').decode('latin-1')

    # 1. Üldinfo
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, enc("1. ÜLDISED ANDMED"), ln=True)
    pdf.set_font("helvetica", '', 10)
    with pdf.table(col_widths=(45, 145)) as table:
        table.row([enc("Tooandja/Vastutav"), enc(f"{tooaandja} / {vastutav}")])
        table.row([enc("Aadress/Omanik"), enc(f"{aadress} / {omanik_info}")])
        table.row([enc("Ilm / Aeg"), enc(f"{ilm_tekst}, tuul {tuul} m/s | Kell: {kellaaeg}")])

    # 2. Puu info
    pdf.ln(5)
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, enc("2. PUU JA KESKKONNA SEISUND"), ln=True)
    pdf.set_font("helvetica", '', 10)
    with pdf.table(col_widths=(45, 145)) as table:
        table.row([enc("Puu seisund"), enc(puu_andmed)])
        table.row([enc("Keskkond"), enc(keskkond_andmed)])

    # 3. Riskitabel
    pdf.ln(5)
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, enc("3. RISKIDE HINDAMISE MAATRIKS"), ln=True)
    pdf.set_font("helvetica", '', 6)
    with pdf.table(col_widths=(30, 30, 40, 65, 25)) as table:
        table.row([enc("Oht"), enc("Kirjeldus"), enc("Varustus"), enc("Meetmed"), enc("Skoor")])
        for rida in tabeli_andmed:
            table.row([enc(item) for item in rida])

    pdf.ln(10)
    pdf.cell(95, 10, enc("Koostaja allkiri: ........................."), 0, 0)
    pdf.cell(95, 10, enc("Tootaja allkiri: ........................."), 0, 1)

    if foto:
        pdf.add_page()
        img = Image.open(foto).convert("RGB")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        pdf.image(img_byte_arr, x=15, y=25, w=180)
    return pdf.output()

if st.button("🚀 GENEREERI LÕPLIK PDF"):
    output = loe_pdf()
    st.download_button("📥 Laadi alla", bytes(output), f"Riskianalyys_{aadress}.pdf", "application/pdf")
