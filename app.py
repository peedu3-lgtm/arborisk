# --- RISKIDE HINDAMISE OSA (Asenda see tsükkel oma koodis) ---

for i, oht in enumerate(ohud_base):
    with st.expander(f"📍 {oht[0]}", expanded=False):
        col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 0.6, 0.6])
        
        with col1:
            kirj = st.text_input("Ohu kirjeldus", value=oht[1], key=f"k{i}")
        
        with col2:
            # MITME VALIKUGA TÖÖVAHENDID
            vahendid_valitud = st.multiselect(
                "Töövahendid", 
                options=toovahendid_valik, 
                default=[oht[2]] if oht[2] in toovahendid_valik else [],
                key=f"v{i}"
            )
            # Võimalus lisada käsitsi, kui midagi on puudu
            vahend_lisa = st.text_input("Lisa muu vahend (vabatahtlik)", key=f"vcl{i}")
            
            # Ühendame valikud üheks stringiks PDF-i jaoks
            koik_vahendid = ", ".join(vahendid_valitud)
            if vahend_lisa:
                koik_vahendid += f", {vahend_lisa}" if koik_vahendid else vahend_lisa

        with col3:
            # MITME VALIKUGA MEETMED
            meetmed_valitud = st.multiselect(
                "Ennetusmeetmed", 
                options=meetmed_valik, 
                default=[oht[3]] if oht[3] in meetmed_valik else [],
                key=f"m{i}"
            )
            meede_lisa = st.text_input("Lisa muu meede (vabatahtlik)", key=f"mcl{i}")
            
            koik_meetmed = ", ".join(meetmed_valitud)
            if meede_lisa:
                koik_meetmed += f", {meede_lisa}" if koik_meetmed else meede_lisa
            
        with col4: 
            t = st.selectbox("T", t_r_valikud, index=t_r_valikud.index(oht[4]), key=f"t{i}")
        with col5: 
            r = st.selectbox("R", t_r_valikud, index=t_r_valikud.index(oht[5]), key=f"r{i}")
        
        skoor = t * r
        tase = "MADAL" if skoor <= 4 else "KESKMINE" if skoor <= 12 else "KÕRGE"
        
        # Lisame andmed tabelisse (kasutades koik_vahendid ja koik_meetmed stringe)
        tabeli_andmed.append([oht[0], kirj, koik_vahendid, koik_meetmed, f"{t}x{r}={skoor} ({tase})"])
