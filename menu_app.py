import streamlit as st
import os
import time
import requests
import re  # Dodato za AI naručivanje
from supabase import create_client, Client

# ==========================================
# 1. SIGURNO PODEŠAVANJE
# ==========================================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ GREŠKA: GEMINI_API_KEY nije podešen u Streamlit Secrets!")
    st.stop()

GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
SUPABASE_URL = "https://mszsrorxwmkopoyvsbpw.supabase.co"
SUPABASE_KEY = "sb_publishable_mYfAEgWeQqUcjTIKqORx5w_A4hSqIc_"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Podešavanje izgleda stranice
st.set_page_config(page_title="Korzo | Digitalni Meni", page_icon="🍽️", layout="wide", initial_sidebar_state="collapsed")

# --- MINIMALISTIČKI MOBILNI DIZAJN (CSS) ---
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    div.stButton > button { border-radius: 10px; font-weight: bold; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Skrivanje starog sidebara potpuno */
    [data-testid="collapsedControl"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BAZA MENIJA (Sa nutritivnim vrednostima)
# ==========================================
menu_database = {
    "Korzo doručak": {"category": "Doručak", "price": 630.00, "calories": 750, "protein": 35, "carbs": 45, "sugar": 5, "fiber": 4, "desc": "2 jaja, sudžuk, goveđa pršuta, ajvar, sir", "image": "slike/korzo_dorucak.jpg"},
    "Kajgana": {"category": "Doručak", "price": 350.00, "calories": 300, "protein": 20, "carbs": 2, "sugar": 1, "fiber": 0, "desc": "Domaća kajgana", "image": "slike/kajgana.jpg"},
    "Kačamak": {"category": "Doručak", "price": 300.00, "calories": 400, "protein": 8, "carbs": 55, "sugar": 2, "fiber": 3, "desc": "Tradicionalni domaći kačamak", "image": "slike/kacamak.jpg"},
    "Juneća čorba 350g": {"category": "Toplo predjelo", "price": 480.00, "calories": 250, "protein": 18, "carbs": 15, "sugar": 3, "fiber": 2, "desc": "Domaća topla juneća čorba", "image": "slike/juneca_corba.jpg"},
    "Juneće ćufte 350g": {"category": "Roštilj", "price": 990.00, "calories": 650, "protein": 45, "carbs": 10, "sugar": 2, "fiber": 1, "desc": "Sočne juneće ćufte sa roštilja", "image": "slike/junece_cufte.jpg"},
    "Juneći ćevapi 350g": {"category": "Roštilj", "price": 960.00, "calories": 700, "protein": 50, "carbs": 5, "sugar": 1, "fiber": 0, "desc": "Pravi domaći juneći ćevapi", "image": "slike/juneci_cevapi.jpg"},
    "Bagrem piletina 350g": {"category": "Roštilj", "price": 900.00, "calories": 500, "protein": 60, "carbs": 8, "sugar": 2, "fiber": 1, "desc": "Specijalitet kuće od piletine", "image": "slike/bagrem_piletina.jpg"},
    "Goveđa pršuta 100g": {"category": "Hladno predjelo", "price": 900.00, "calories": 250, "protein": 30, "carbs": 0, "sugar": 0, "fiber": 0, "desc": "Kvalitetna domaća goveđa pršuta", "image": "slike/govedja_prsuta.jpg"},
    "Sušeni sudžuk 100g": {"category": "Hladno predjelo", "price": 480.00, "calories": 400, "protein": 20, "carbs": 2, "sugar": 0, "fiber": 0, "desc": "Domaći sušeni sudžuk", "image": "slike/suseni_sudzuk.jpg"},
    "Sir 100g": {"category": "Hladno predjelo", "price": 340.00, "calories": 350, "protein": 20, "carbs": 3, "sugar": 3, "fiber": 0, "desc": "Domaći beli sir", "image": "slike/sir.jpg"},
    "Mađarski juneći gulaš 450g": {"category": "Glavno jelo", "price": 1020.00, "calories": 600, "protein": 40, "carbs": 30, "sugar": 6, "fiber": 4, "desc": "Bogati mađarski gulaš od junetine", "image": "slike/madjarski_gulas.jpg"},
    "Ćufte u pireu 350g": {"category": "Glavno jelo", "price": 660.00, "calories": 550, "protein": 30, "carbs": 45, "sugar": 4, "fiber": 3, "desc": "Domaće ćufte u kremastom pireu", "image": "slike/cufte_u_pireu.jpg"},
    "Prebranac sa sudžukom 400g": {"category": "Glavno jelo", "price": 760.00, "calories": 650, "protein": 30, "carbs": 50, "sugar": 5, "fiber": 12, "desc": "Zapečeni pasulj sa sudžukom", "image": "slike/prebranac_sudzuk.jpg"},
    "Prebranac 300g": {"category": "Glavno jelo", "price": 590.00, "calories": 400, "protein": 18, "carbs": 55, "sugar": 4, "fiber": 14, "desc": "Tradicionalni posni prebranac", "image": "slike/prebranac.jpg"},
    "Šopska salata 350g": {"category": "Salate", "price": 460.00, "calories": 200, "protein": 8, "carbs": 12, "sugar": 6, "fiber": 4, "desc": "Paradajz, krastavac, luk, paprika, sir", "image": "slike/sopska_salata.jpg"},
    "Srpska salata 300g": {"category": "Salate", "price": 410.00, "calories": 100, "protein": 3, "carbs": 15, "sugar": 8, "fiber": 5, "desc": "Paradajz, krastavac, luk, ljuta paprika", "image": "slike/srpska_salata.jpg"},
    "Kupus salata 300g": {"category": "Salate", "price": 330.00, "calories": 80, "protein": 2, "carbs": 10, "sugar": 5, "fiber": 4, "desc": "Sveža kupus salata", "image": "slike/kupus_salata.jpg"},
    "Ljuta paprika u ulju 1 komad": {"category": "Salate", "price": 150.00, "calories": 50, "protein": 0, "carbs": 3, "sugar": 1, "fiber": 1, "desc": "Pečena ljuta paprika", "image": "slike/ljuta_paprika.jpg"},
    "Lepinja 1 komad": {"category": "Dodaci", "price": 120.00, "calories": 250, "protein": 7, "carbs": 50, "sugar": 2, "fiber": 2, "desc": "Sveža domaća lepinja", "image": "slike/lepinja.jpg"},
    "Pomfrit 150g": {"category": "Dodaci", "price": 300.00, "calories": 450, "protein": 4, "carbs": 60, "sugar": 1, "fiber": 5, "desc": "Hrskavi prženi krompirići", "image": "slike/pomfrit.jpg"},
    "Kugla kajmaka 1 komad": {"category": "Dodaci", "price": 180.00, "calories": 200, "protein": 2, "carbs": 2, "sugar": 1, "fiber": 0, "desc": "Domaći zreli kajmak", "image": "slike/kugla_kajmaka.jpg"}
}

# --- FUNKCIJE ZA BAZU ---
def ucitaj_iz_baze():
    try:
        res = supabase.table("porudzbine").select("*").execute()
        return {item['sto']: item for item in res.data}
    except: return {}

def snimi_u_bazu(sto, podaci):
    provera = supabase.table("porudzbine").select("*").eq("sto", sto).execute()
    nova_data = {
        "sto": sto, 
        "stavke": podaci.get("stavke", {}), 
        "zove_konobara": podaci.get("zove_konobara", False),
        "trazi_racun": podaci.get("trazi_racun", False)
    }
    if len(provera.data) > 0: supabase.table("porudzbine").update(nova_data).eq("sto", sto).execute()
    else: supabase.table("porudzbine").insert(nova_data).execute()

def obrisi_sto(sto):
    supabase.table("porudzbine").delete().eq("sto", sto).execute()

def prikazi_sliku(putanja):
    return putanja if os.path.exists(putanja) else "https://via.placeholder.com/600x400.png?text=Korzo+Restoran"

# ==========================================
# 3. PANEL ZA KONOBARA
# ==========================================
def prikazi_konobara():
    st.markdown("<h1 style='text-align: center; color: #E63946;'>👨‍🍳 Kontrolni Panel - Korzo</h1>", unsafe_allow_html=True)
    st.info("🔄 Ekran se automatski osvežava svakih 10 sekundi.")
    st.divider()
    
    baza = ucitaj_iz_baze()
    if not baza: 
        st.success("✨ Trenutno nema aktivnih narudžbi. Restoran je miran!")
    else:
        cols = st.columns(3)
        for i, (sto, podaci) in enumerate(baza.items()):
            with cols[i % 3]:
                if podaci.get('zove_konobara'):
                    st.error(f"🚨 STO {sto} VAS ZOVE!")
                elif podaci.get('trazi_racun'):
                    st.warning(f"💳 STO {sto} TRAŽI RAČUN!")
                else:
                    st.info(f"📍 Sto {sto} - Aktivna narudžba")
                
                with st.container(border=True):
                    ukupno = 0
                    st.markdown("### Poručeno:")
                    for jelo, kolicina in podaci.get("stavke", {}).items():
                        if jelo in menu_database:
                            ukupno += menu_database[jelo]["price"] * kolicina
                            st.write(f"🍽️ **{kolicina}x** {jelo}")
                    
                    st.divider()
                    st.metric("Za naplatu:", f"{ukupno:.2f} RSD")
                    
                    if st.button("✅ Zatvori sto (Naplaćeno)", key=f"del_{sto}", use_container_width=True):
                        obrisi_sto(sto)
                        st.rerun()
    time.sleep(10)
    st.rerun()

# ==========================================
# 4. STRANICA ZA GOSTA
# ==========================================
def prikazi_gosta(sto):
    baza = ucitaj_iz_baze()
    moj_sto = baza.get(sto, {"stavke": {}, "zove_konobara": False, "trazi_racun": False})

    # --- NOVI POPOVER (ZAMENJUJE SIDEBAR) ---
    st.markdown(f"<h3 style='text-align: center; color: gray;'>📍 Vaš Sto: {sto}</h3>", unsafe_allow_html=True)
    
    with st.popover("🛒 OTVORI KORPU I OPCIJE", use_container_width=True):
        st.markdown("### 🛒 Vaša Korpa")
        ukupno = 0
        stavke_korpa = moj_sto.get("stavke", {})
        
        if not stavke_korpa:
            st.info("Vaša korpa je prazna.")
        else:
            # Lista stavki sa dugmetom za brisanje
            for jelo, qty in list(stavke_korpa.items()):
                if jelo in menu_database:
                    cena_stavke = menu_database[jelo]["price"] * qty
                    ukupno += cena_stavke
                    
                    col_tekst, col_brisi = st.columns([4, 1])
                    with col_tekst:
                        st.markdown(f"**{qty}x** {jelo} (*{cena_stavke:.2f} RSD*)")
                    with col_brisi:
                        # Brisanje stavki iz korpe
                        if st.button("🗑️", key=f"brisi_{jelo}"):
                            if moj_sto["stavke"][jelo] > 1:
                                moj_sto["stavke"][jelo] -= 1
                            else:
                                del moj_sto["stavke"][jelo]
                            snimi_u_bazu(sto, moj_sto)
                            st.rerun()
            
            st.divider()
            st.metric("Ukupno za plaćanje:", f"{ukupno:.2f} RSD")
            
            if st.button("🧾 ZATRAŽI RAČUN", use_container_width=True):
                moj_sto["trazi_racun"] = True
                snimi_u_bazu(sto, moj_sto)
                st.warning("Konobar dolazi sa Vašim računom!")

        st.divider()
        st.markdown("### 👨‍🍳 Usluga")
        # Logika za poziv konobara
        if moj_sto["zove_konobara"]:
            if st.button("❌ OTKAŽI POZIV", type="secondary", use_container_width=True):
                moj_sto["zove_konobara"] = False
                snimi_u_bazu(sto, moj_sto)
                st.rerun()
            st.warning("Konobar je pozvan i stiže uskoro.")
        else:
            if st.button("🙋‍♂️ POZOVI KONOBARA", type="primary", use_container_width=True):
                moj_sto["zove_konobara"] = True
                snimi_u_bazu(sto, moj_sto)
                st.success("Osoblje je obavešteno!")

    # --- GLAVNI PRIKAZ MENIJA ---
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>🍽️ Dobrodošli u Korzo</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>Izaberite kategoriju i uživajte u našoj hrani.</p>", unsafe_allow_html=True)

    kategorije = sorted(list(set([info["category"] for info in menu_database.values()])))
    tabs = st.tabs(kategorije)

    for i, tab in enumerate(tabs):
        with tab:
            kat = kategorije[i]
            jela = {k: v for k, v in menu_database.items() if v["category"] == kat}
            cols = st.columns(2)
            for j, (ime, info) in enumerate(jela.items()):
                with cols[j % 2]:
                    with st.container(border=True):
                        st.image(prikazi_sliku(info["image"]), width='stretch')
                        st.markdown(f"#### {ime}")
                        st.markdown(f"<h5 style='color: #E63946; margin-top: -10px;'>{info['price']:.2f} RSD</h5>", unsafe_allow_html=True)
                        st.caption(info['desc'])
                        
                        with st.expander("ℹ️ Nutritivne vrednosti"):
                            st.write(f"🔥 **Kalorije:** {info['calories']} kcal")
                            st.write(f"🥩 **Proteini:** {info['protein']} g")
                            st.write(f"🍞 **Uglj. hidrati:** {info['carbs']} g")
                            st.write(f"🍬 **Šećeri:** {info['sugar']} g")
                            st.write(f"🌾 **Vlakna:** {info['fiber']} g")

                        if st.button(f"➕ Dodaj", key=f"add_{ime}", use_container_width=True):
                            moj_sto["stavke"][ime] = moj_sto["stavke"].get(ime, 0) + 1
                            snimi_u_bazu(sto, moj_sto)
                            st.rerun()

    # --- PAMETNI AI CHATBOT (SA MEMORIJOM I NARUČIVANJEM) ---
    st.divider()
    st.markdown("### 🤖 Pitajte našeg AI konobara!")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    upit = st.chat_input("Pitaj me nešto o meniju ili naruči jelo...")
    
    if upit:
        st.session_state.chat_history.append({"role": "user", "content": upit})
        with st.chat_message("user"):
            st.markdown(upit)
            
        with st.chat_message("assistant"):
            try:
                # Pronalazak modela
                get_models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_KEY}"
                models_response = requests.get(get_models_url)
                
                if models_response.status_code == 200:
                    models_data = models_response.json()
                    radni_model = None
                    for m in models_data.get('models', []):
                        if 'generateContent' in m.get('supportedGenerationMethods', []):
                            radni_model = m['name']
                            break
                    
                    if radni_model:
                        api_contents = []
                        for msg in st.session_state.chat_history:
                            role = "user" if msg["role"] == "user" else "model"
                            api_contents.append({"role": role, "parts": [{"text": msg["content"]}]})
                            
                        url = f"https://generativelanguage.googleapis.com/v1beta/{radni_model}:generateContent?key={GEMINI_KEY}"
                        
                        # INSTRUKCIJE ZA AI DA NARUČUJE
                        sistemska_instrukcija = f"""Ti si konobar u restoranu Korzo. Meni je: {list(menu_database.keys())}. 
                        Odgovaraj prirodno i na našem jeziku. 
                        VAŽNO: Ako gost traži da naruči neko jelo sa menija, obavezno na kraju svog odgovora ubaci tajnu komandu u formatu [DODAJ: Ime Jela]. 
                        Na primer, ako gost kaže 'Dodaj mi Kajganu i Pomfrit 150g', ti reci 'Sa zadovoljstvom, dodao sam u korpu! [DODAJ: Kajgana] [DODAJ: Pomfrit 150g]'."""

                        payload = {
                            "systemInstruction": {"parts": [{"text": sistemska_instrukcija}]},
                            "contents": api_contents
                        }
                        
                        ai_response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
                        
                        if ai_response.status_code == 200:
                            odgovor = ai_response.json()['candidates'][0]['content']['parts'][0]['text']
                            
                            # MAGIJA: Logika za automatsko dodavanje iz AI komandi
                            komande_dodaj = re.findall(r'\[DODAJ:\s*(.*?)\]', odgovor)
                            dodato = False
                            for jelo in komande_dodaj:
                                jelo = jelo.strip()
                                if jelo in menu_database:
                                    moj_sto["stavke"][jelo] = moj_sto["stavke"].get(jelo, 0) + 1
                                    dodato = True
                            
                            if dodato:
                                snimi_u_bazu(sto, moj_sto)
                                st.success("✨ AI asistent je automatski dodao stavke u vašu korpu!")
                            
                            # Čistimo tajne komande da ih gost ne vidi
                            cist_odgovor = re.sub(r'\[DODAJ:\s*.*?\]', '', odgovor).strip()
                            
                            st.markdown(cist_odgovor)
                            st.session_state.chat_history.append({"role": "assistant", "content": cist_odgovor})
                        else:
                            st.error("Desila se greška prilikom odgovora AI sistema.")
                else:
                    st.error("AI sistem trenutno nije dostupan.")
            except Exception as e:
                st.error("Došlo je do greške pri povezivanju.")

# ==========================================
# 5. GLAVNI RUTER
# ==========================================
params = st.query_params
if "konobar" in params: 
    prikazi_konobara()
elif "sto" in params: 
    prikazi_gosta(params["sto"])
else:
    st.markdown("<h2 style='text-align: center;'>Dobrodošli u Korzo 🍽️</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### 📱 Za Goste")
            st.write("Skenirajte QR kod na stolu ili uđite ovde za test.")
            if st.button("Uđi kao Sto 1", use_container_width=True):
                st.query_params["sto"] = "1"
                st.rerun()
                
    with col2:
        with st.container(border=True):
            st.markdown("### 👨‍🍳 Za Osoblje")
            st.write("Pristup kontrolnom panelu za praćenje narudžbi.")
            if st.button("Otvori Kontrolni Panel", type="primary", use_container_width=True):
                st.query_params["konobar"] = "true"
                st.rerun()
