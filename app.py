import streamlit as st
from fpdf import FPDF
import datetime
import requests
from PIL import Image
import io
import pytz

# --- 1. ASUKOHAD JA ILMAANDMED ---
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

# --- 2. TÖÖINSPEKTSIOONI STANDARDITELE VASTAVAD ALUSANDMED ---
OHUD_BASE = [
    ["Kukkuvad oksad / ladvaosad", "Füüsiline trauma, löök, purustused maapinnal olijatele või varale", 3, 4],
    ["Kukkumine kõrgusest", "Ronimisvarustuse purunemine, libisemine, ankrUpunkti viga, tõstuki rike", 2, 5],
    ["Puu vale kukkumissuund", "Tüve langetamisel ootamatu suunamuutus, mädanikust tingitud murdumine", 2, 5],
    ["Mootorsae tagasilöök / sisselõige", "Rasked lõikehaavad operaatorile või abilisele", 2, 5],
    ["Elektrilöök (õhuliinid)", "Tööpinge all olevate liinide läheduses, kaarekujuline ülelöök läbi okste", 1, 5],
    ["Müra ja vibratsioon", "Pikaajaline tervisekahjustus, kuulmislangus, reko-sündroom (valged sõrmed)", 4, 2],
    ["Kolmandad isikud ja liiklus", "Kõrvaliste isikute või sõidukite sattumine ohualasse tööprotsessi ajal", 2, 4],
    ["Võõra vara kahjustamine", "Hoone katused, piirdeaiad, elektriliinid, haljastus ohualas", 3, 3],
    ["Bioloogilised ohud / putukad", "Herilaste/vaablaste rünnak puu otsas, puugid, allergiad", 3, 2]
]

TOORIISTAD = [
    "Mootorsaag (bensiin/aku)", "Käsisaag / kõrglõikur", "Arboristi ronimisvarustus (sertifitseeritud)", 
    "Korvtõstuk", "Oksahakkur", "Tõmbevints / köissüsteemid", "Suunamiskiilud / Lammutuskiilud", 
    "Ohutusrihmad ja rigging-plokid", "Piirdelint / ohumärgid", "Raadioside / peakomplektid"
]

MEETMED_BASE = [
    "Ohuala täielik tähistamine ja julgestaja määramine", 
    "Kohustusliku IKV kandmine (kiiver lõuarihmaga, saekaitsepüksid, turvajalanõud)", 
    "Ronimisvarustuse / tõstuki igapäevane eelkontroll (visuaalne)", 
    "Suunatud langetamine vintsi ja abiköitega", 
    "Ohutu vahemaa hoidmine (2x puu kõrgus)", 
    "Sidepidamine raadio teel (operaator-maamees)", 
    "Teede/tänava ajutine sulgemine / liikluskorraldus", 
    "Lähedalasuva vara kaitsmine (kaitseekraanid, rigging)", 
    "Esmaabikomplekti olemasolu ja valmidus töökohal",
    "Päästeplaani läbimängimine (ronija allatoomine < 10 minutiga)"
]

# --- 3. UI ÜLESEHITUS ---
st.set_page_config(page_title="Arborisk Pro v8.0 - Tööinspektsiooni valmidus", layout="wide")

# Logo/Pealkiri stiil
st.markdown("<h1 style='text-align: center; color: #1E4620;'>🌳 Arborisk Pro v8.0</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic;'>Ametlik arboristi objekti riskianalüüsi ja ohutuse tagamise süsteem (Vastab Töötervishoiu ja tööohutuse seadusele)</p>", unsafe_allow_html=True)

st.divider()

# Kasutame tabe puhtama UI jaoks
tab1, tab2, tab3 = st.tabs(["📋 1. Üldandmed & Meeskond", "🌲 2. Objekti & Puu Seisund", "⚡ 3. Riskide Hindamise Maatriks"])

with tab1:
    st.subheader("Ettevõtte ja töökeskkonna üldandmed")
    col1, col2 = st.columns(2)

    with col1:
        tooaandja = st.text_input("Tööandja (Ettevõtte nimi)", "Framiter OÜ")
        vastutav = st.text_input("Vastutav isik / Tööjuht (Nimi ja tel)", value="") 
        tootajad = st.text_area("Töögrupi koosseis (Kõik objektil viibivad töötajad)", placeholder="1. Jaan Tamm (Arborist)
2. Peeter Kask (Abitööline / Maamees)")
        aadress = st.text_input("Objekti täpne aadress", placeholder="Männi tee 4, Tallinn")
        kellaaeg = st.text_input("Töö algusaeg objektil", value=get_eesti_aeg())

    with col2:
        valitud_maakond = st.selectbox("Vali teostamise maakond (Ilmateate jaoks)", list(MAAKONNAD.keys()))
        lat, lon = MAAKONNAD[valitud_maakond]
        auto_tuul, auto_temp = get_weather(lat, lon)
        
        tuul = st.number_input("Mõõdetud tuule kiirus kohapeal (m/s)", value=auto_tuul, step=0.1)
        if tuul >= 12.0:
            st.error("⚠️ HOIATUS: Tuule kiirus on üle 12 m/s! Kõrgustööd ja puude langetamine on eluohtlik ning Tööinspektsiooni reeglite järgi üldjuhul keelatud.")
        elif tuul >= 8.0:
            st.warning("⚠️ TÄHELEPANU: Tuul on tugev. Tõstukiga töötamisel ja suurtel kõrgustel tegutsedes rakendada kõrgendatud tähelepanu.")

        ilm_tekst = st.text_input("Ilmastiku kirjeldus / Temperatuur", value=auto_temp)
        haigla = st.text_input("Lähim EMO / Esmaabipunkt (Aadress/Telefon)", placeholder="Põhja-Eesti Regionaalhaigla EMO, J. Sütiste tee 19")
        esmaabi_andja = st.text_input("Sertifitseeritud esmaabiandja kohapeal", placeholder="Jaan Tamm (Kehtiv sertifikaat kuni 2027)")

with tab2:
    st.subheader("Puu dendroloogilised andmed ja töökeskkonna eripärad")
    col3, col4 = st.columns(2)
    
    with col3:
        puu_liik = st.text_input("Puu liik (nt. Harilik tamm, Vananenud saar)", "")
        puu_korgus = st.number_input("Puu prognoositav kõrgus (m)", min_value=1, value=20)
        puu_seisund = st.text_area("Puu tervislik seisund ja defektid (Tööinspektsioonile oluline!)", 
                                   placeholder="Seenhaigused, tüvemädanik, pikilõhed, ohtlik kalle hoone poole, kuivanud suurvõra osad.")
    
    with col4:
        # Ohuala arvutamine ametliku valemi järgi (tavaliselt vähemalt 2x puu kõrgus)
        ohuala = puu_korgus * 2
        st.metric("Nõutav ohuala raadius (m)", f"{ohuala} m", help="Tööinspektsiooni standard: Ohuala raadius peab olema vähemalt kahekordne puu kõrgus.")
        
        keskkond = st.text_area("Ümbritsev keskkond ja infrastruktuur", 
                                placeholder="Läheduses asuvad õhuliinid (10kV), sõidutee, eramu katus 5m kaugusel, jalakäijate kergliiklustee.")
        paaste_info = st.text_input("Ligipääs päästetehnikale ja logistika", placeholder="Väravad avatud, ligipääs tagatud korvtõstukile ja kiirabile.")
        
    st.subheader("🚨 ARBORISTI PÄÄSTEPLAAN (Tööinspektsiooni kohustuslik nõue!)")
    paasteplaan = st.text_area(
        "Kirjelda päästeplaani juhuks, kui ronija kaotab teadvuse või jääb puu otsa kinni (Suspension Trauma vältimiseks):",
        value="Kohapeal on teine sertifitseeritud ronimisvarustusega arborist/tööjuht, kes on valmis koheseks päästeronimiseks. Maapinnal on valmis seatud päästeköis. Päästeaeg maapinnale toomiseks on alla 10 minuti. Vajadusel kaasatakse koheselt Päästeamet (112)."
    )

with tab3:
    st.subheader("Riskide hindamine (Tõenäosus × Tagajärg)")
    st.info("Hinda iga ohuteguri tõenäosust (1-5) ja tagajärje raskust (1-5). Süsteem arvutab riskitaseme automaatselt.")
    
    tabeli_andmed = []
    
    # Isikukaitsevahendite (IKV) valik
    st.markdown("#### **Nõutavad isikukaitsevahendid (IKV) antud objektil:**")
    ikv_col1, ikv_col2, ikv_col3 = st.columns(3)
    with ikv_col1:
        ikv_kiiver = st.checkbox("Arboristi kiiver lõuarihmaga (EN 12492)", value=True)
        ikv_kuulmine = st.checkbox("Kuulmiskaitsevahendid (kõrvaklapid)", value=True)
    with ikv_col2:
        ikv_saed = st.checkbox("Saekaitsepüksid (Klass 1 või 2)", value=True)
        ikv_jalanoud = st.checkbox("Saekaitsega turvajalanõud", value=True)
    with ikv_col3:
        ikv_rakmed = st.checkbox("Kukkumiskaitserakmed ja julgestus (EN 358/361)", value=True)
        ikv_nagu = st.checkbox("Näokaitse / kaitseprillid", value=True)
        
    ikv_list = []
    if ikv_kiiver: ikv_list.append("Arboristi kiiver (EN 12492)")
    if ikv_kuulmine: ikv_list.append("Kuulmiskaitse")
    if ikv_saed: ikv_list.append("Saekaitsepüksid")
    if ikv_jalanoud: ikv_list.append("Turvajalanõud")
    if ikv_rakmed: ikv_list.append("Kukkumisrakmed")
    if ikv_nagu: ikv_list.append("Näokaitse")
    ikv_kokkuvõte = ", ".join(ikv_list)

    st.markdown("---")
    st.markdown("#### **Ohutegurite kaardistamine:**")

    for i, oht in enumerate(OHUD_BASE):
        with st.expander(f"📍 Ohutegur: {oht[0]}", expanded=True if i<3 else False):
            c1, c2, c3, c4, c5 = st.columns([1.5, 2, 2, 0.6, 0.6])
            with c1: 
                kirj = st.text_input("Spetsiifiline oht / tagajärg", value=oht[1], key=f"k_{i}")
            with c2:
                v_val = st.multiselect("Kasutatavad töövahendid", TOORIISTAD, default=[TOORIISTAD[0], TOORIISTAD[8]] if i==0 else [TOORIISTAD[0]], key=f"v_{i}")
                v_lisa = st.text_input("Muu spetsiifiline varustus:", key=f"vl_{i}")
                v_kokku = ", ".join(v_val) + (f" {v_lisa}" if v_lisa else "")
            with c3:
                m_val = st.multiselect("Rakendatavad ohutusmeetmed", MEETMED_BASE, default=[MEETMED_BASE[0], MEETMED_BASE[1], MEETMED_BASE[4]] if i==0 else [MEETMED_BASE[1]], key=f"m_{i}")
                m_lisa = st.text_input("Muu spetsiifiline meede:", key=f"ml_{i}")
                m_kokku = ", ".join(m_val) + (f" {m_lisa}" if m_lisa else "")
            with c4: 
                t = st.selectbox("Tõenäosus (1-5)", [1,2,3,4,5], index=oht[2]-1, key=f"t_{i}", help="1-Harv, 5-Pidev/Kindel")
            with c5: 
                r = st.selectbox("Tagajärg (1-5)", [1,2,3,4,5], index=oht[3]-1, key=f"r_{i}", help="1-Tühine, 5-Surmav/Katastroofiline")
            
            skoor = t * r
            
            # Riskitaseme määramine värviga
            if skoor <= 4:
                status_color = "green"
                status_text = "MADAL"
            elif skoor <= 12:
                status_color = "orange"
                status_text = "KESKMINE"
            else:
                status_color = "red"
                status_text = "KÕRGE (TÖÖ KEELATUD)"
                
            st.markdown(f"Riskiskoor: <span style='color:{status_color}; font-weight:bold;'>{skoor} ({status_text})</span>", unsafe_allow_html=True)
            tabeli_andmed.append([oht[0], kirj, v_kokku, m_kokku, f"{skoor} ({status_text})"])

    st.markdown("---")
    foto = st.file_uploader("Lisa foto või asendiplaan objektist (PDF-i lisamiseks)", type=['jpg', 'jpeg', 'png'])

# --- 4. FINISH JA PDF GENEREERIMINE ---
def genereeri_ametlik_pdf():
    # Loome PDF klassi laienduse, et käsitleda täpitähti ISO-8859-1 abil (Latin-1)
    # Standard Helvetica toetab Ä, Ö, Ü, Õ kui kodeerida õigesti.
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    def enc(txt):
        if not txt:
            return ""
        # Asendame š ja ž süsteemi ühilduvuse tagamiseks, kuna standardne latin-1 neid ei sisalda
        txt = str(txt).replace("š", "s").replace("Š", "S").replace("ž", "z").replace("Ž", "Z")
        return txt.encode('iso-8859-1', 'replace').decode('iso-8859-1')

    # --- Päis ---
    pdf.set_fill_color(30, 70, 32) # Tumesinine/roheline toon
    pdf.rect(0, 0, 210, 35, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 8, enc("TÖÖKOHA RISKIANALÜÜS: ARBORISTITÖÖD"), ln=True, align='C')
    pdf.set_font("helvetica", 'I', 10)
    pdf.cell(0, 5, enc("Vastab Tööinspektsiooni ja Töötervishoiu ja tööohutuse seaduse (TTOS) nõuetele"), ln=True, align='C')
    pdf.ln(12)
    
    pdf.set_text_color(0, 0, 0)
    
    # --- 1. Üldandmed ---
    pdf.set_font("helvetica", 'B', 12)
    pdf.set_fill_color(240, 245, 240)
    pdf.cell(0, 8, enc(" 1. ETTEVÕTTE JA OBJEKTI ÜLDANDMED"), fill=True, ln=True)
    pdf.ln(2)
    
    pdf.set_font("helvetica", '', 10)
    with pdf.table(col_widths=(60, 130), line_height=7) as table:
        table.row([enc("Tööandja / Ettevõte"), enc(tooaandja)])
        table.row([enc("Vastutav isik / Tööjuht"), enc(vastutav)])
        table.row([enc("Töögrupi koosseis"), enc(tootajad)])
        table.row([enc("Objekti täpne aadress"), enc(aadress)])
        table.row([enc("Kuupäev ja kellaaeg"), enc(f"{datetime.date.today().strftime('%d.%m.%Y')} / {kellaaeg}")])
        table.row([enc("Ilmastikutingimused kohapeal"), enc(f"{ilm_tekst} | Tuul: {tuul} m/s")])
        table.row([enc("Lähim EMO punkt"), enc(haigla)])
        table.row([enc("Sertifitseeritud esmaabiandja"), enc(esmaabi_andja)])
        table.row([enc("Valitud Isikukaitsevahendid (IKV)"), enc(ikv_kokkuvõte)])

    pdf.ln(6)
    
    # --- 2. Puu ja keskkonna seisund ---
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 8, enc(" 2. PUU DENDROLOOGILISED ANDMED JA KESKKOND"), fill=True, ln=True)
    pdf.ln(2)
    
    pdf.set_font("helvetica", '', 10)
    with pdf.table(col_widths=(60, 130), line_height=7) as table:
        table.row([enc("Puu liik"), enc(puu_liik)])
        table.row([enc("Puu kõrgus / Arvutuslik ohuala"), enc(f"{puu_korgus} m / Raadius: {ohuala} m (2x kõrgus)")])
        table.row([enc("Tervislik seisund ja defektid"), enc(puu_seisund)])
        table.row([enc("Ümbritsev keskkond"), enc(keskkond)])
        table.row([enc("Ligipääs päästetehnikale"), enc(paaste_info)])

    pdf.ln(6)
    
    # --- Päästeplaan ---
    pdf.set_font("helvetica", 'B', 11)
    pdf.set_text_color(180, 0, 0)
    pdf.cell(0, 6, enc("KOHUSTUSLIK ARBORISTI PÄÄSTEPLAAN KÕRGUSTELT PÄÄSTMISEKS:"), ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", 'I', 10)
    pdf.multi_cell(0, 6, enc(paasteplaan), border=1)
    
    pdf.ln(6)
    
    # --- 3. Riskide tabel ---
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 8, enc(" 3. RISKIDE HINDAMISE JA SAKSEERIMISE MAATRIKS"), fill=True, ln=True)
    pdf.ln(2)
    
    pdf.set_font("helvetica", '', 8)
    with pdf.table(col_widths=(35, 40, 40, 55, 20), line_height=6) as table:
        table.row([enc("Ohutegur"), enc("Spetsiifiline oht"), enc("Töövahendid"), enc("Kaitsemeetmed"), enc("Riskitase")])
        for rida in tabeli_andmed:
            table.row([enc(item) for item in rida])

    # Selgitused ja kinnitused
    pdf.ln(8)
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 5, enc("Klassifikatsioon: Skoor 1-4 Madal | Skoor 5-12 Keskmine | Skoor 15-25 KÕRGE (Töö alustamine keelatud!)"), ln=True)
    pdf.set_font("helvetica", '', 10)
    pdf.ln(8)
    
    pdf.multi_cell(0, 6, enc("Kinnitan oma allkirjaga, et olen tutvunud antud objekti riskianalüüsiga, läbinud ohutusalase instrueerimise ning kohustun täitma kõiki dokumenteeritud ohutusmeetmeid ja kandma ettenähtud isikukaitsevahendeid."))
    pdf.ln(12)
    
    pdf.cell(95, 10, enc("Tööjuhi / Koostaja allkiri: ......................................."), 0, 0)
    pdf.cell(95, 10, enc("Kuupäev: ......................................."), 0, 1)
    pdf.ln(5)
    pdf.cell(95, 10, enc("Töötaja 1 allkiri: ......................................."), 0, 0)
    pdf.cell(95, 10, enc("Töötaja 2 allkiri: ......................................."), 0, 1)

    if foto:
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 8, enc("OBJEKTI FOTO JA ASENDIPLAAN"), ln=True, align='C')
        pdf.ln(5)
        img = Image.open(foto).convert("RGB")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        pdf.image(img_byte_arr, x=15, y=30, w=180)

    return pdf.output()

st.sidebar.markdown("### Rapordi seaded")
if st.button("🚀 GENEREERI TÖÖINSPEKTSIOONILE VASTAV LÕPLIK PDF"):
    if not vastutav or not aadress or not puu_liik:
        st.error("❌ Palun täida enne PDF-i genereerimist kohustuslikud väljad: Vastutav isik, Aadress ja Puu liik!")
    else:
        output = genereeri_ametlik_pdf()
        st.success("✅ Ametlik riskianalüüsi raport on valmis genereeritud!")
        st.download_button(
            label="📥 LAADI ALLA AMETLIK PDF RAPORT", 
            data=bytes(output), 
            file_name=f"Arborist_Riskianalyys_{aadress.replace(' ', '_')}.pdf", 
            mime="application/pdf"
        )
