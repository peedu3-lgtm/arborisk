import streamlit as st
from fpdf import FPDF
import datetime
import requests
from PIL import Image
import io
import pytz

# --- 0. SEADISTUSED ---
MAAKONNAD = {
    "Harjumaa": (59.33, 24.75), "Tartumaa": (58.37, 26.72), "Pärnumaa": (58.38, 24.50),
    "Ida-Virumaa": (59.35, 27.41), "Saaremaa": (58.25, 22.48), "Viljandimaa": (58.36, 25.59),
    "Lääne-Virumaa": (59.34, 26.35), "Võrumaa": (57.84, 27.00), "Raplamaa": (58.99, 24.79),
    "Järvamaa": (58.88, 25.56), "Läänemaa": (58.94, 23.54), "Jõgevamaa": (58.74, 26.39),
    "Põlvamaa": (58.05, 27.05), "Valgamaa": (57.77, 26.03), "Hiiumaa": (58.88, 22.59)
}

LANG = {
    "ET": {
        "title": "TÖÖKOHA RISKIANALÜÜS", "employer": "Tööandja", "responsible": "Vastutav isik", 
        "address": "Objekti aadress", "owner": "Omaniku kontakt", "time": "Töö algusaeg",
        "weather": "Tuul (m/s)", "temp": "Ilm/Temp", "county": "Vali maakond", 
        "tree": "Puu liik ja seisund", "env": "Teed, rajad ja pinnas", 
        "risk_tab": "RISKIDE HINDAMINE", "hazard": "Oht", "desc": "Kirjeldus", 
        "tools": "Varustus", "measures": "Meetmed", "score": "Skoor",
        "custom_tools": "VÕI kirjuta ise varustus:", "custom_measures": "VÕI kirjuta ise meede:",
        "gen": "GENEREERI PDF", "summary": "RISKIHINDAMISE SELGITUSED",
        "tools_list": ["Mootorsaag", "Käsisaag", "Ronimisvarustus", "Korvtõstuk", "Hakkur", "Vints", "Kiilud", "Piirdelint", "Rigging", "Muu"],
        "measures_list": ["Ohuala tähistamine", "IKV kandmine", "Varustuse kontroll", "Vintsimine", "Ohutu vahemaa", "Kõrvaklapid", "Sõidukite parkimine", "Vara kaitse", "Esmaabi"],
        "hazards_base": [
            ["Kukkuvad oksad", "Puuvõra hooldus", 2, 4], ["Kukkumine", "Ronimine/tõstuk", 1, 5],
            ["Vale kukkumissuund", "Tüve langetamine", 1, 5], ["Müra ja Vibratsioon", "Tervisekahjustus", 3, 2],
            ["Isikud/Autod", "Vigastusoht ohualas", 2, 3], ["Võõras vara", "Löökkahjustus", 2, 3],
            ["Putukad", "Nõelamine/puugid", 2, 3], ["Elekter", "Õhuliinid", 1, 5]
        ]
    },
    "EN": {
        "title": "SITE RISK ASSESSMENT", "employer": "Employer", "responsible": "Person in charge", 
        "address": "Site address", "owner": "Owner contact", "time": "Start time",
        "weather": "Wind (m/s)", "temp": "Weather/Temp", "county": "Select county", 
        "tree": "Tree species & condition", "env": "Paths, roads & soil", 
        "risk_tab": "RISK ASSESSMENT", "hazard": "Hazard", "desc": "Description", 
        "tools": "Equipment", "measures": "Mitigation", "score": "Score",
        "custom_tools": "OR write custom equipment:", "custom_measures": "OR write custom measure:",
        "gen": "GENERATE PDF", "summary": "RISK ASSESSMENT EXPLANATIONS",
        "tools_list": ["Chainsaw", "Handsaw", "Climbing gear", "Lift", "Chipper", "Winch", "Wedges", "Caution tape", "Rigging", "Other"],
        "measures_list": ["Area marking", "PPE use", "Gear check", "Winching", "Safety distance", "Ear protection", "Vehicle parking", "Property cover", "First aid"],
        "hazards_base": [
            ["Falling branches", "Crown maintenance", 2, 4], ["Falling", "Climbing/lift", 1, 5],
            ["Wrong direction", "Felling tree", 1, 5], ["Noise/Vibra", "Health risk", 3, 2],
            ["Bystanders/Cars", "Injury risk", 2, 3], ["Property damage", "Impact risk", 2, 3],
            ["Insects", "Stings/ticks", 2, 3], ["Electricity", "Power lines", 1, 5]
        ]
    }
}

def get_eesti_aeg():
    try:
        eesti_tz = pytz.timezone('Europe/Tallinn')
        return datetime.datetime.now(eesti_tz).strftime("%H:%M")
    except: return datetime.datetime.now().strftime("%H:%M")

def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m&wind_speed_unit=ms"
        response = requests.get(url, timeout=3)
        data = response.json()
        return round(data['current']['wind_speed_10m'], 1), f"{data['current']['temperature_2m']}C"
    except: return 0.0, "N/A"

# --- 1. UI ---
st.set_page_config(page_title="Arborisk Pro", layout="wide")
lang_choice = st.sidebar.radio("Keel / Language", ["ET", "EN"])
T = LANG[lang_choice]

st.title(f"🌳 Arborisk Pro v6.5")

st.header(f"1. {T['employer']}")
col_a, col_b = st.columns(2)
with col_b:
    maakond = st.selectbox(T['county'], list(MAAKONNAD.keys()))
    lat, lon = MAAKONNAD[maakond]
    auto_tuul, auto_ilm = get_weather(lat, lon)
    tuul = st.number_input(T['weather'], value=auto_tuul)
    ilm_tekst = st.text_input(T['temp'], value=auto_ilm)
    haigla = st.text_input("EMO", "PERH / TÜ Kliinikum")
with col_a:
    tooaandja = st.text_input(T['employer'], "Aiavana Hooldusteenused OÜ")
    vastutav = st.text_input(T['responsible'], "Ivar Peedu")
    aadress = st.text_input(T['address'], "")
    omanik_info = st.text_input(T['owner'], "")
    kellaaeg = st.text_input(T['time'], value=get_eesti_aeg())

st.divider()
st.header(f"2. {T['tree']}")
col_c, col_d = st.columns(2)
with col_c: puu_seisund = st.text_area(T['tree'])
with col_d: keskkond_info = st.text_area(T['env'])

st.divider()
st.header(f"3. {T['risk_tab']}")
tabeli_andmed = []

for i, oht in enumerate(T["hazards_base"]):
    with st.expander(f"📍 {oht[0]}", expanded=False):
        c1, c2, c3, c4, c5 = st.columns([1.5, 2, 2, 0.5, 0.5])
        with c1: kirj = st.text_input(T['desc'], value=oht[1], key=f"k{i}_{lang_choice}")
        with c2:
            v_val = st.multiselect(T['tools'], T['tools_list'], key=f"v{i}_{lang_choice}")
            v_lisa = st.text_input(T['custom_tools'], key=f"vl{i}_{lang_choice}")
            v_kokku = ", ".join(v_val) + (f" {v_lisa}" if v_lisa else "")
        with c3:
            m_val = st.multiselect(T['measures'], T['measures_list'], key=f"m{i}_{lang_choice}")
            m_lisa = st.text_input(T['custom_measures'], key=f"ml{i}_{lang_choice}")
            m_kokku = ", ".join(m_val) + (f" {m_lisa}" if m_lisa else "")
        with c4: t = st.selectbox("T", [1,2,3,4,5], index=oht[2]-1, key=f"t{i}_{lang_choice}")
        with c5: r = st.selectbox("R", [1,2,3,4,5], index=oht[3]-1, key=f"r{i}_{lang_choice}")
        sk = t * r
        st.write(f"{T['score']}: **{sk}**")
        tabeli_andmed.append([oht[0], kirj, v_kokku, m_kokku, f"{sk}"])

foto = st.file_uploader("Foto", type=['jpg', 'jpeg', 'png'])

def loe_pdf():
    pdf = FPDF()
    pdf.add_page()
    def enc(txt): return str(txt).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, enc(T['title']), ln=True, align='C')
    pdf.set_font("helvetica", '', 10)
    pdf.ln(5)
    with pdf.table(col_widths=(45, 145)) as table:
        table.row([enc(T['employer']), enc(tooaandja)])
        table.row([enc(T['responsible']), enc(vastutav)])
        table.row([enc(T['address']), enc(aadress)])
        table.row([enc(T['weather']), enc(f"{tuul} m/s, {ilm_tekst}")])
        table.row([enc(T['time']), enc(f"{datetime.date.today()} / {kellaaeg}")])
    pdf.ln(5)
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, enc(T['tree']), ln=True)
    pdf.set_font("helvetica", '', 10)
    pdf.multi_cell(0, 5, enc(puu_seisund + "\n" + keskkond_info))
    pdf.ln(5)
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, enc(T['risk_tab']), ln=True)
    pdf.set_font("helvetica", '', 6)
    with pdf.table(col_widths=(30, 30, 40, 65, 25)) as table:
        table.row([enc(T['hazard']), enc(T['desc']), enc(T['tools']), enc(T['measures']), enc(T['score'])])
        for rida in tabeli_andmed: table.row([enc(item) for item in rida])
    pdf.ln(10)
    pdf.set_font("helvetica", 'B', 9)
    pdf.cell(0, 5, enc(T['summary']), ln=True)
    pdf.set_font("helvetica", '', 7)
    pdf.cell(0, 4, enc("T (1-5) x R (1-5) = Score. 1-4: Low, 5-12: Med, 15-25: High (STOP!)"), ln=True)
    if foto:
        pdf.add_page()
        img = Image.open(foto).convert("RGB")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        pdf.image(img_byte_arr, x=15, y=25, w=180)
    return pdf.output()

if st.button(T['gen']):
    output = loe_pdf()
    st.download_button("PDF", bytes(output), f"Risk_{aadress}.pdf", "application/pdf")
