import streamlit as st
from fpdf import FPDF
import datetime
import requests
from PIL import Image
import io

# --- 1. ILMAFUNKTSIOON (Open-Meteo) ---
def get_weather(lat=58.5953, lon=25.0136):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,wind_speed_10m&wind_speed_unit=ms"
        response = requests.get(url, timeout=5)
        data = response.json()
        current = data['current']
        w_code = current['weather_code']
        if w_code == 0: ilm = "Selge"
        elif w_code in [1, 2, 3]: ilm = "Vahelduv pilvisus"
        elif w_code in [61, 63, 65]: ilm = "Vihmasadu"
        else: ilm = "Pilves"
        return current['wind_speed_10m'], ilm, current['temperature_2m']
    except:
        return 0.0, "Andmed puuduvad", 0.0

# --- 2. ANDMETE ETTEVALMISTUS ---
toovahendid_valik = [
    "Mootorsaag", "Käsisaag", "Ronimisvarustus", "Korvtõstuk", "Hakkur", 
    "Kännufrees", "Vints", "Kiilud ja haamer", "Piirdelint/koonused", 
    "Viskeliin ja raskus", "Plokid ja rigging-köied", "Muu..."
]

# LISATUD: Esmaabi ja allergiarohud meetmete nimekirja
meetmed_valik = [
    "Ohuala tähistamine ja piiramine", "Kõrvaliste isikute eemaldamine",
    "Isikukaitsevahendite (IKV) kandmine", "Varustuse eelnev kontroll",
    "Vintsimine ja suunamine", "Ohutu vahemaa hoidmine", 
    "Töö peatamine ebasobiva ilmaga", "Antivibratsioon-kindad",
    "Kõrvaklapid", "Sõidukite ümberparkimine", "Vara kaitse/kate",
    "Esmaabikomplekt", "Allergiaravimid (antihistamiinid)", "Muu..."
]

t_r_valikud = [1, 2, 3, 4, 5]

# KÕIK OHUD KOOS ESMAABI UUENDUSTEGA
ohud_base = [
    ["Kukkuvad oksad ja ladvaosad", "Puuvõra hooldus", "Mootorsaag", "Ohuala tähistamine ja piiramine", 2, 4],
    ["Kõrgusest kukkumine", "Ronimine/tõstuk", "Ronimisvarustus", "Isikukaitsevahendite (IKV) kandmine", 1, 5],
    ["Puu langemine vales suunas", "Tüve langetamine", "Vints", "Vintsimine ja suunamine", 1, 5],
    ["Müra ja Vibratsioon", "Tervisekahjustus (kuulmine/liigesed)", "Mootorsaag", "Kõrvaklapid", 3, 2],
    ["Kõrvalised isikud / Jalakäijad", "Vigastusoht ohualas", "Piirdelint/koonused", "Kõrvaliste isikute eemaldamine", 2, 3],
    ["Sõidukid (autod)", "Varaline kahju / pihtasaamine", "Piirdelint/koonused", "Sõidukite ümberparkimine", 2, 3],
    ["Võõras vara (aiad, katused)", "Löökkahjustused / purunemine", "Plokid ja rigging-köied", "Vara kaitse/kate", 2, 3],
    ["Herilased / Mesilased", "Nõelamine (allergiline šokk)", "Muu...", "Allergiaravimid (antihistamiinid)", 2, 3],
    ["Puugid / Lyme tõbi", "Bioloogiline oht", "Muu...", "Esmaabikomplekt", 3, 2],
    ["Elektrilöök", "Õhuliinid läheduses", "Muu...", "Ohutu vahemaa hoidmine", 1, 5]
]

# --- 3. PDF KLASS ---
class ArboristPDF(FPDF):
    def header(self):
        self.set_font("helvetica", 'B', 14)
        self.cell(0, 10, "TOOKOHA RISKIANALUUS JA OHUTUSPLAAN", ln=True, align='C')
        self.ln(2)

# --- 4. KASUTAJALIIDES ---
st.set_page_config(page_title="Arborisk Pro", layout="wide")
st.title("🌳 Arborisk Pro v4.1")

st.header("1. ÜLDISED ANDMED JA ILM")
col_a, col_b = st.columns(2)
auto_tuul, auto_ilm, auto_temp = get_weather()

with col_a:
    tooaandja = st.text_input("Tööandja", "Aiavana Hooldusteenused OÜ")
    vastutav = st.text_input("Vastutav isik", "Ivar Peedu")
    aadress = st.text_input("Objekti aadress", "")
    kellaaeg = st.text_input("Töö algusaeg", datetime.datetime.now().strftime("%H:%M"))

with col_b:
    tuul = st.number_input("Tuule kiirus (m/s)", value=float(auto_tuul))
    ilm_tekst = st.text_input("Ilm (prognoos)", value=f"{auto_ilm}, {auto_temp}C")
    haigla = st.text_input("Lähim EMO", "PERH / TÜ Kliinikum")
    if tuul > 12: st.error("⚠️ HOIATUS: Tuul üle 12 m/s! Kõrgtööd peatada!")

st.divider()

st.header("2. RISKIDE HINDAMINE")
tabeli_andmed = []

for i, oht in enumerate(ohud_base):
    with st.expander(f"📍 {oht[0]}", expanded=False):
        c1, c2, c3, c4, c5 = st.columns([1.5, 2, 2, 0.5, 0.5])
        
        with c1:
            kirj = st.text_input("Ohu kirjeldus", value=oht[1], key=f"k{i}")
        
        with c2:
            v_val = st.multiselect("Vali varustus listist", toovahendid_valik, default=[oht[2]] if oht[2] in toovahendid_valik else [], key=f"v{i}")
            v_lisa = st.text_input("VÕI kirjuta ise varustus:", key=f"vl{i}")
            v_kokku = ", ".join(v_val) + (f", {v_lisa}" if v_lisa else "")
        
        with c3:
            m_val = st.multiselect("Vali meetmed listist", meetmed_valik, default=[oht[3]] if oht[3] in meetmed_valik else [], key=f"m{i}")
            m_lisa = st.text_input("VÕI kirjuta ise meede:", key=f"ml{i}")
            m_kokku = ", ".join(m_val) + (f", {m_lisa}" if m_lisa else "")
                
        with c4: t = st.selectbox("T", t_r_valikud, index=t_r_valikud.index(oht[4]), key=f"t{i}")
        with c5: r = st.selectbox("R", t_r_valikud, index=t_r_valikud.index(oht[5]), key=f"r{i}")
        
        sk = t * r
        tase = "MADAL" if sk <= 4 else "KESKMINE" if sk <= 12 else "KÕRGE"
        st.write(f"Skoor: **{sk} ({tase})**")
        tabeli_andmed.append([oht[0], kirj, v_kokku, m_kokku, f"{sk} ({tase})"])

foto = st.file_uploader("Lisa foto objektist", type=['jpg', 'jpeg', 'png'])

# --- 5. PDF GENEREERIMINE ---
def loe_pdf():
    pdf = ArboristPDF()
    pdf.add_page()
    
    # 1. Üldandmed
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "1. ULDISED ANDMED JA TÖÖTINGIMUSED", ln=True)
    pdf.set_font("helvetica", '', 10)
    with pdf.table(col_widths=(45, 145)) as table:
        table.row(["Tooandja", tooaandja])
        table.row(["Vastutav / Aadress", f"{vastutav} / {aadress}"])
        table.row(["Ilm / Tuul", f"{ilm_tekst} / {tuul} m/s"])
        table.row(["Kuupaev / Kell", f"{datetime.date.today()} / {kellaaeg}"])

    pdf.ln(5)
    
    # 2. Riskide tabel
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "2. RISKIDE HINDAMISE MAATRIKS", ln=True)
    pdf.set_font("helvetica", '', 6)
    with pdf.table(col_widths=(30, 30, 40, 65, 25)) as table:
        table.row(["Oht", "Kirjeldus", "Varustus", "Meetmed", "Skoor (T x R)"])
        for rida in tabeli_andmed:
            table.row(rida)

    # 3. Selgitused
    pdf.ln(8)
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 8, "RISKIMAATRIKSI SELGITUSED", ln=True)
    pdf.set_font("helvetica", '', 7)
    with pdf.table(col_widths=(95, 95)) as table:
        table.row(["TOENAOSUS (T)", "TAGAJARG (R)"])
        table.row(["1 - Vaike (harva)", "1 - Ebaoluline (esmaabi pole vaja)"])
        table.row(["3 - Keskmine (voib esineda)", "3 - Raske vigastus (toovoimetus)"])
        table.row(["5 - Kindel (ilmneb sageli)", "5 - Eriti raske (surm)"])
    
    pdf.ln(2)
    pdf.cell(0, 5, "Hinnang: 1-4 Madal; 5-12 Keskmine; 15-25 KORGE (Too ohtlik!)", ln=True)

    # 4. Allkirjad
    pdf.ln(10)
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(95, 10, "Koostaja allkiri: .........................", 0, 0)
    pdf.cell(95, 10, "Tootaja allkiri: .........................", 0, 1)

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
