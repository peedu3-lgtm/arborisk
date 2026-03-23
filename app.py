import streamlit as st
from fpdf import FPDF
import datetime
import requests
from PIL import Image
import io

# --- 1. ILMAFUNKTSIOON ---
def get_weather(lat=59.437, lon=24.7535): # Vaikimisi Tallinn
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,is_day,precipitation,weather_code,wind_speed_10m&wind_speed_unit=ms"
        response = requests.get(url, timeout=5)
        data = response.json()
        current = data['current']
        
        # Weather code tõlkimine (lihtsustatud)
        w_code = current['weather_code']
        if w_code == 0: ilm = "Selge"
        elif w_code in [1, 2, 3]: ilm = "Vahelduv pilvisus"
        elif w_code in [51, 53, 55, 61, 63, 65]: ilm = "Sadu (vihm)"
        elif w_code in [71, 73, 75]: ilm = "Lumesadu"
        else: ilm = "Pilves/Sajune"
        
        return current['wind_speed_10m'], ilm, current['temperature_2m']
    except:
        return 5.0, "Andmed puuduvad", 0.0

# --- 2. ANDMETE ETTEVALMISTUS ---
toovahendid_valik = ["Mootorsaag", "Käsisaag", "Ronimisvarustus", "Korvtõstuk", "Hakkur", "Kännufrees", "Vints", "Kiilud ja haamer", "Piirdelint/koonused", "Plokid ja rigging-köied", "Muu..."]
meetmed_valik = ["Ohuala tähistamine ja piiramine", "Kõrvaliste isikute eemaldamine", "Isikukaitsevahendite (IKV) kandmine", "Varustuse eelnev kontroll", "Vintsimine ja suunamine", "Ohutu vahemaa hoidmine", "Töö peatamine ebasobiva ilmaga", "Muu..."]
t_r_valikud = [1, 2, 3, 4, 5]

ohud_base = [
    ["Kukkuvad oksad ja ladvaosad", "Puuvõra hooldus", "Mootorsaag", "Ohuala tähistamine ja piiramine", 2, 3],
    ["Kõrgusest kukkumine", "Ronimine/tõstuk", "Ronimisvarustus", "Isikukaitsevahendite (IKV) kandmine", 1, 4],
    ["Puu langemine vales suunas", "Tüve langetamine", "Vints", "Vintsimine ja suunamine", 1, 5],
    ["Herilased / Mesilased", "Nõelamine", "Muu...", "Esmaabikomplekti kontroll", 2, 3],
    ["Puugid / Lyme tõbi", "Bioloogiline oht", "Muu...", "Tööriiete kontroll", 3, 2]
]

# --- 3. PDF KLASS ---
class ArboristPDF(FPDF):
    def header(self):
        self.set_font("helvetica", 'B', 14)
        self.cell(0, 10, "TÖÖKOHA RISKIANALÜÜS JA OHUTUSPLAAN", ln=True, align='C')

# --- 4. KASUTAJALIIDES (Streamlit) ---
st.set_page_config(page_title="Arborisk Pro", layout="wide")
st.title("🌳 Arborisk Pro: Automaatne Ilm + Riskianalüüs")

st.header("1. ÜLDISED ANDMED JA ILMASTIK")
col_a, col_b = st.columns(2)

# Küsime ilmaandmed kohe alguses
auto_tuul, auto_ilm, auto_temp = get_weather()

with col_a:
    tooaandja = st.text_input("Tööandja", "Aiavana Hooldusteenused OÜ")
    vastutav = st.text_input("Vastutav isik", "Ivar Peedu")
    aadress = st.text_input("Objekti aadress", "")
    kellaaeg = st.text_input("Aeg", datetime.datetime.now().strftime("%H:%M"))

with col_b:
    st.subheader("Automaatne ilmaprognoos (Open-Meteo)")
    tuul = st.number_input("Tuule kiirus (m/s)", value=float(auto_tuul))
    ilm_tekst = st.text_input("Ilmastikuolud", value=f"{auto_ilm}, {auto_temp}°C")
    haigla = st.text_input("Lähim haigla/EMO", "PERH / TÜ Kliinikum")
    
    if tuul > 12:
        st.error(f"⚠️ HOIATUS: Tuul on {tuul} m/s! Kõrgtööd on ohtlikud.")

st.divider()

# --- 5. RISKID (Sama loogika mis varem) ---
st.header("2. RISKIDE HINDAMINE")
tabeli_andmed = []
for i, oht in enumerate(ohud_base):
    with st.expander(f"📍 {oht[0]}", expanded=False):
        c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 0.5, 0.5])
        with c1: kirj = st.text_input("Kirjeldus", value=oht[1], key=f"k{i}")
        with c2: 
            v_val = st.multiselect("Vahendid", toovahendid_valik, default=[oht[2]] if oht[2] in toovahendid_valik else [], key=f"v{i}")
            vahendid_str = ", ".join(v_val)
        with c3:
            m_val = st.multiselect("Meetmed", meetmed_valik, default=[oht[3]] if oht[3] in meetmed_valik else [], key=f"m{i}")
            meetmed_str = ", ".join(m_val)
        with c4: t = st.selectbox("T", t_r_valikud, index=t_r_valikud.index(oht[4]), key=f"t{i}")
        with c5: r = st.selectbox("R", t_r_valikud, index=t_r_valikud.index(oht[5]), key=f"r{i}")
        
        sk = t * r
        tase = "MADAL" if sk <= 4 else "KESKMINE" if sk <= 12 else "KÕRGE"
        st.write(f"Skoor: {sk} ({tase})")
        tabeli_andmed.append([oht[0], kirj, vahendid_str, meetmed_str, f"{sk} ({tase})"])

foto = st.file_uploader("Lisa foto", type=['jpg', 'jpeg', 'png'])

# --- 6. PDF GENEREERIMINE ---
def loe_pdf():
    pdf = ArboristPDF()
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "1. ÜLDISED ANDMED JA ILM", ln=True)
    pdf.set_font("helvetica", '', 10)
    with pdf.table(col_widths=(45, 145)) as table:
        table.row(["Tööandja", tooaandja])
        table.row(["Vastutav isik", vastutav])
        table.row(["Aadress", aadress])
        table.row(["Ilm objektil", f"{ilm_tekst}, tuul {tuul} m/s"])
        table.row(["Kuupäev/Aeg", f"{datetime.date.today()} / {kellaaeg}"])

    pdf.ln(5)
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "2. RISKIDE TABEL", ln=True)
    pdf.set_font("helvetica", '', 7)
    with pdf.table(col_widths=(35, 30, 40, 60, 25)) as table:
        table.row(["Ohutegur", "Kirjeldus", "Vahendid", "Meetmed", "Skoor"])
        for rida in tabeli_andmed: table.row(rida)

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
    st.download_button("📥 Laadi alla", bytes(output), f"Riskianalyys_{aadress}.pdf", "application/pdf")
