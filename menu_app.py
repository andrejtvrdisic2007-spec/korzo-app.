import streamlit as st
import os
import time
import requests
import re
import difflib
from st_keyup import st_keyup
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

st.set_page_config(page_title="Korzo | Digitalni Meni", page_icon="🍽️", layout="centered", initial_sidebar_state="collapsed")

# --- WOLT/GLOVO STIL (CSS) ---
st.markdown("""
<style>
    .block-container { padding: 1rem 1rem 3rem 1rem; max-width: 600px; }
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2) !important;
        margin-bottom: 15px;
        overflow: hidden;
        background-color: #1e1e1e;
    }
    
    div.stButton > button {
        border-radius: 25px;
        font-weight: 700;
        border: none;
        transition: 0.2s;
    }
    div.stButton > button:active { transform: scale(0.95); }
    
    div.stButton > button[kind="primary"] {
        background-color: #E63946;
        color: white;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; padding-bottom: 10px; }
    .stTabs [data-baseweb="tab"] { 
        border-radius: 20px; 
        padding: 8px 18px; 
        background-color: #3b3f4a !important; 
        border: 1px solid #5a5f6e; 
    }
    .stTabs [data-baseweb="tab"] p {
        color: #f0f0f0 !important;
        opacity: 1 !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #E63946 !important; 
        border: 1px solid #E63946 !important;
    }
    .stTabs [aria-selected="true"] p { 
        color: #ffffff !important; 
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BAZA MENIJA I PAMETNA PRETRAGA
# ==========================================
menu_database = {
    "Korzo doručak": {"category": "Doručak", "price": 630.00, "calories": 750, "protein": 35, "carbs": 45, "sugar": 5, "fiber": 4, "diet": "Meso", "desc": "2 jaja, sudžuk, goveđa pršuta, ajvar, sir", "image": "slike/korzo_dorucak.jpg"},
    "Kajgana": {"category": "Doručak", "price": 350.00, "calories": 300, "protein": 20, "carbs": 2, "sugar": 1, "fiber": 0, "diet": "Vegetarijansko", "desc": "Domaća kajgana", "image": "slike/kajgana.jpg"},
    "Kačamak": {"category": "Doručak", "price": 300.00, "calories": 400, "protein": 8, "carbs": 55, "sugar": 2, "fiber": 3, "diet": "Vegetarijansko", "desc": "Tradicionalni domaći kačamak", "image": "slike/kacamak.jpg"},
    "Juneća čorba 350g": {"category": "Toplo predjelo", "price": 480.00, "calories": 250, "protein": 18, "carbs": 15, "sugar": 3, "fiber": 2, "diet": "Meso", "desc": "Domaća topla juneća čorba", "image": "slike/juneca_corba.jpg"},
    "Juneće ćufte 350g": {"category": "Roštilj", "price": 990.00, "calories": 650, "protein": 45, "carbs": 10, "sugar": 2, "fiber": 1, "diet": "Meso", "desc": "Sočne juneće ćufte sa roštilja", "image": "slike/junece_cufte.jpg"},
    "Juneći ćevapi 350g": {"category": "Roštilj", "price": 960.00, "calories": 700, "protein": 50, "carbs": 5, "sugar": 1, "fiber": 0, "diet": "Meso", "desc": "Pravi domaći juneći ćevapi", "image": "slike/juneci_cevapi.jpg"},
    "Bagrem piletina 350g": {"category": "Roštilj", "price": 900.00, "calories": 500, "protein": 60, "carbs": 8, "sugar": 2, "fiber": 1, "diet": "Meso", "desc": "Specijalitet kuće od piletine", "image": "slike/bagrem_piletina.jpg"},
    "Goveđa pršuta 100g": {"category": "Hladno predjelo", "price": 900.00, "calories": 250, "protein": 30, "carbs": 0, "sugar": 0, "fiber": 0, "diet": "Meso", "desc": "Kvalitetna domaća goveđa pršuta", "image": "slike/govedja_prsuta.jpg"},
    "Sušeni sudžuk 100g": {"category": "Hladno predjelo", "price": 480.00, "calories": 400, "protein": 20, "carbs": 2, "sugar": 0, "fiber": 0, "diet": "Meso", "desc": "Domaći sušeni sudžuk", "image": "slike/suseni_sudzuk.jpg"},
    "Sir 100g": {"category": "Hladno predjelo", "price": 340.00, "calories": 350, "protein": 20, "carbs": 3, "sugar": 3, "fiber": 0, "diet": "Vegetarijansko", "desc": "Domaći beli sir", "image": "slike/sir.jpg"},
    "Mađarski juneći gulaš 450g": {"category": "Glavno jelo", "price": 1020.00, "calories": 600, "protein": 40, "carbs": 30, "sugar": 6, "fiber": 4, "diet": "Meso", "desc": "Bogati mađarski gulaš od junetine", "image": "slike/madjarski_gulas.jpg"},
    "Ćufte u pireu 350g": {"category": "Glavno jelo", "price": 660.00, "calories": 550, "protein": 30, "carbs": 45, "sugar": 4, "fiber": 3, "diet": "Meso", "desc": "Domaće ćufte u kremastom pireu", "image": "slike/cufte_u_pireu.jpg"},
    "Prebranac sa sudžukom 400g": {"category": "Glavno jelo", "price": 760.00, "calories": 650, "protein": 30, "carbs": 50, "sugar": 5, "fiber": 12, "diet": "Meso", "desc": "Zapečeni pasulj sa sudžukom", "image": "slike/prebranac_sudzuk.jpg"},
    "Prebranac 300g": {"category": "Glavno jelo", "price": 590.00, "calories": 400, "protein": 18, "carbs": 55, "sugar": 4, "fiber": 14, "diet": "Posno", "desc": "Tradicionalni posni prebranac", "image": "slike/prebranac.jpg"},
    "Šopska salata 350g": {"category": "Salate", "price": 460.00, "calories": 200, "protein": 8, "carbs": 12, "sugar": 6, "fiber": 4, "diet": "Vegetarijansko", "desc": "Paradajz, krastavac, luk, paprika, sir", "image": "slike/sopska_salata.jpg"},
    "Srpska salata 300g": {"category": "Salate", "price": 410.00, "calories": 100, "protein": 3, "carbs": 15, "sugar": 8, "fiber": 5, "diet": "Posno", "desc": "Paradajz, krastavac, luk, ljuta paprika", "image": "slike/srpska_salata.jpg"},
    "Kupus salata 300g": {"category": "Salate", "price": 330.00, "calories": 80, "protein": 2, "carbs": 10, "sugar": 5, "fiber": 4, "diet": "Posno", "desc": "Sveža kupus salata", "image": "slike/kupus_salata.jpg"},
    "Ljuta paprika u ulju 1 komad": {"category": "Salate", "price": 150.00, "calories": 50, "protein": 0, "carbs": 3, "sugar": 1, "fiber": 1, "diet": "Posno", "desc": "Pečena ljuta paprika", "image": "slike/ljuta_paprika.jpg"},
    "Lepinja 1 komad": {"category": "Dodaci", "price": 120.00, "calories": 250, "protein": 7, "carbs": 50, "sugar": 2, "fiber": 2, "diet": "Posno", "desc": "Sveža domaća lepinja", "image": "slike/lepinja.jpg"},
    "Pomfrit 150g": {"category": "Dodaci", "price": 300.00, "calories": 450, "protein": 4, "carbs": 60, "sugar": 1, "fiber": 5, "diet": "Posno", "desc": "Hrskavi prženi krompirići", "image": "slike/pomfrit.jpg"},
    "Kugla kajmaka 1 komad": {"category": "Dodaci", "price": 180.00, "calories": 200, "protein": 2, "carbs": 2, "sugar": 1, "fiber": 0, "diet": "Vegetarijansko", "desc": "Domaći zreli kajmak", "image": "slike/kugla_kajmaka.jpg"}
}

def ukloni_kvacice(tekst):
    tekst = tekst.lower()
    zamene = {'ć': 'c', 'č': 'c', 'š': 's', 'ž': 'z', 'đ': 'dj'}
    for sr, lat in zamene.items():
        tekst = tekst.replace(sr, lat)
    return tekst

def proveri_poklapanje(upit, naziv_jela):
    upit_norm = ukloni_kvacice(upit).strip()
    naziv_norm = ukloni_kvacice(naziv_jela)
    if not upit_norm: return True
    if upit_norm in naziv_norm: return True
    if len(upit_norm) >= 3:
        reci_iz_naziva = naziv_norm.split()
        for rec in reci_iz_naziva:
            slicnost = difflib.SequenceMatcher(None, upit_norm, rec).ratio()
            if slicnost >= 0.7:  
                return True
    return False

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
        "trazi_racun": podaci.get("trazi_racun", False),
        "konobar_stize": podaci.get("konobar_stize", False)
    }
    if len(provera.data) > 0: supabase.table("porudzbine").update(nova_data).eq("sto", sto).execute()
    else: supabase.table("porudzbine").insert(nova_data).execute()

def obrisi_sto(sto):
    supabase.table("porudzbine").delete().eq("sto", sto).execute()

def prikazi_sliku(putanja):
    return putanja if os.path.exists(putanja) else "https://via.placeholder.com/600x350.png?text=Korzo"

# ==========================================
# 3. KONTROLNI PANEL ZA KONOBARA (LOGIN + MAPA)
# ==========================================
def prikazi_konobara():
    st.markdown("<h1 style='text-align: center; color: #E63946;'>👨‍🍳 Kontrolni Panel - Korzo</h1>", unsafe_allow_html=True)
    
    # Tabovi: Mapa, Lista narudžbi, Statistika
    tab_mapa, tab_stolovi, tab_statistika = st.tabs(["🗺️ Mapa Sale", "🍽️ Lista Narudžbi", "📊 Dnevni Pazar"])
    baza = ucitaj_iz_baze()
    aktivni_stolovi = {k: v for k, v in baza.items() if k != "admin_statistika"}
    zvoni_alarm = False
    
    # TAB 1: VIZUALNA MAPA STOLOVA
    with tab_mapa:
        st.markdown("### Trenutno stanje u sali")
        st.caption("🟢 Slobodno | 🔵 Zauzeto (Jedu) | 🚨 Hitna usluga")
        
        # Definiramo stolove u sali (npr. 6 stolova)
        svi_stolovi = ["1", "2", "3", "4", "5", "6"]
        cols = st.columns(3)
        
        for i, sto_id in enumerate(svi_stolovi):
            with cols[i % 3]:
                podaci_stola = aktivni_stolovi.get(sto_id)
                
                if not podaci_stola:
                    boja = "#2b9348" # Zelena
                    st.markdown(f"<div style='background-color:{boja}; padding:15px; border-radius:15px; text-align:center; color:white; margin-bottom:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'><h2>🟢 {sto_id}</h2><b>Slobodan</b></div>", unsafe_allow_html=True)
                elif podaci_stola.get('zove_konobara') or podaci_stola.get('trazi_racun'):
                    boja = "#d90429" # Crvena
                    razlog = "Račun!" if podaci_stola.get('trazi_racun') else "Konobar!"
                    st.markdown(f"<div style='background-color:{boja}; padding:15px; border-radius:15px; text-align:center; color:white; margin-bottom:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'><h2>🚨 {sto_id}</h2><b>{razlog}</b></div>", unsafe_allow_html=True)
                else:
                    boja = "#0077b6" # Plava
                    st.markdown(f"<div style='background-color:{boja}; padding:15px; border-radius:15px; text-align:center; color:white; margin-bottom:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'><h2>🔵 {sto_id}</h2><b>Zauzet</b></div>", unsafe_allow_html=True)

    # TAB 2: DETALJI NARUDŽBI
    with tab_stolovi:
        if not aktivni_stolovi: 
            st.success("✨ Trenutno nema aktivnih narudžbi.")
        else:
            cols = st.columns(3)
            i = 0
            for sto, podaci in aktivni_stolovi.items():
                with cols[i % 3]:
                    if (podaci.get('zove_konobara') or podaci.get('trazi_racun')) and not podaci.get('konobar_stize'):
                        zvoni_alarm = True
                    
                    with st.container(border=True):
                        st.markdown(f"<h3 style='text-align: center;'>📍 Sto {sto}</h3>", unsafe_allow_html=True)
                        
                        if podaci.get('zove_konobara') or podaci.get('trazi_racun'):
                            razlog = "💳 TRAŽI RAČUN" if podaci.get('trazi_racun') else "🚨 ZOVE VAS"
                            if podaci.get('konobar_stize'):
                                st.success("🏃‍♂️ Krenuli ste ka stolu.")
                            else:
                                st.error(f"**{razlog}**")
                                if st.button("✅ Prihvati poziv", key=f"prihvati_{sto}", use_container_width=True):
                                    podaci["konobar_stize"] = True
                                    snimi_u_bazu(sto, podaci)
                                    st.rerun()
                        else:
                            st.info("🍽️ Aktivna narudžba")
                        
                        ukupno = 0
                        for jelo, kolicina in podaci.get("stavke", {}).items():
                            if jelo in menu_database:
                                ukupno += menu_database[jelo]["price"] * kolicina
                                st.write(f"▪️ **{kolicina}x** {jelo}")
                        
                        st.divider()
                        st.metric("Za naplatu:", f"{ukupno:.2f} RSD")
                        
                        if st.button("💰 Naplati i Zatvori", key=f"del_{sto}", type="primary", use_container_width=True):
                            stat_podaci = baza.get("admin_statistika", {"sto": "admin_statistika", "stavke": {}})
                            stat_podaci["stavke"]["_ukupno_zarada"] = stat_podaci.get("stavke", {}).get("_ukupno_zarada", 0) + ukupno
                            for j, q in podaci.get("stavke", {}).items():
                                stat_podaci["stavke"][j] = stat_podaci["stavke"].get(j, 0) + q
                            snimi_u_bazu("admin_statistika", stat_podaci)
                            obrisi_sto(sto)
                            st.rerun()
                i += 1

    # TAB 3: DNEVNI PAZAR
    with tab_statistika:
        stat_podaci = baza.get("admin_statistika", {"stavke": {}})
        ukupno_zarada = stat_podaci.get("stavke", {}).get("_ukupno_zarada", 0)
        
        st.markdown(f"### 💰 Ukupan pazar danas: **{ukupno_zarada:.2f} RSD**")
        st.divider()
        st.markdown("#### 🏆 Prodana jela i pića:")
        
        prodato = {k: v for k, v in stat_podaci.get("stavke", {}).items() if k != "_ukupno_zarada"}
        prodato_sortirano = sorted(prodato.items(), key=lambda x: x[1], reverse=True)
        
        if not prodato_sortirano:
            st.info("Još uvijek nema naplaćenih jela.")
        else:
            for jelo, kolicina in prodato_sortirano:
                st.write(f"✔️ **{kolicina}x** {jelo}")
        
        st.write("")
        if st.button("🗑️ Zatvori smjenu (Resetiraj pazar)", type="primary"):
            obrisi_sto("admin_statistika")
            st.success("Pazar je uspješno resetiran!")
            time.sleep(1)
            st.rerun()

    # ZVUČNI ALARM
    if zvoni_alarm:
        st.components.v1.html(
            '''<audio autoplay loop><source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg"></audio>''',
            height=0, width=0
        )
            
    time.sleep(10)
    st.rerun()

# ==========================================
# 4. STRANICA ZA GOSTA
# ==========================================
def prikazi_gosta(sto):
    if "ekran" not in st.session_state:
        st.session_state.ekran = "meni"
    
    baza = ucitaj_iz_baze()
    moj_sto = baza.get(sto, {"stavke": {}, "zove_konobara": False, "trazi_racun": False, "konobar_stize": False})

    if "ai_toast" in st.session_state and st.session_state.ai_toast:
        st.toast(st.session_state.ai_toast, icon="🛒")
        st.session_state.ai_toast = "" 

    if st.session_state.ekran == "meni":
        broj_stavki = sum(moj_sto.get("stavke", {}).values())
        
        st.markdown(f"<h1 style='text-align: center; margin-bottom: 0px;'>🍽️ Korzo</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: gray;'>Sto {sto} • Uživajte u hrani</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🛒 Korpa ({broj_stavki})", type="primary", use_container_width=True):
                st.session_state.ekran = "korpa"
                st.rerun()
        with col2:
            if moj_sto["zove_konobara"] or moj_sto["trazi_racun"]:
                if moj_sto.get("konobar_stize"):
                    st.button("🏃‍♂️ Konobar stiže!", disabled=True, use_container_width=True)
                else:
                    if st.button("❌ Otkaži poziv", type="secondary", use_container_width=True):
                        moj_sto["zove_konobara"] = False
                        moj_sto["trazi_racun"] = False
                        snimi_u_bazu(sto, moj_sto)
                        st.rerun()
            else:
                if st.button("🙋‍♂️ Konobar", use_container_width=True):
                    moj_sto["zove_konobara"] = True
                    moj_sto["konobar_stize"] = False
                    snimi_u_bazu(sto, moj_sto)
                    st.toast("Konobar je pozvan!", icon="🔔")
                    st.rerun()

        st.write("") 
        
        with st.expander("🔍 Filteri i pretraga (tipkaj slobodno)"):
            search_tekst = st_keyup("Što vam se jede danas?", placeholder="npr. 'prebranac', 'cevapi', 'gulas'...", debounce=300)
            if not search_tekst: search_tekst = ""
            
            c_cena, c_ishrana = st.columns(2)
            with c_cena: max_cena = st.slider("Maks. cijena (RSD)", 100, 2000, 2000, step=50)
            with c_ishrana: odabrana_ishrana = st.multiselect("Vrsta prehrane", ["Meso", "Vegetarijansko", "Posno"])
        
        filtriran_meni = {}
        for ime, info in menu_database.items():
            if not proveri_poklapanje(search_tekst, ime): continue
            if info["price"] > max_cena: continue
            if odabrana_ishrana and info["diet"] not in odabrana_ishrana: continue
            filtriran_meni[ime] = info

        if not filtriran_meni:
            st.warning("Nijedno jelo ne odgovara unosu. Jeste li mislili na nešto drugo?")
        else:
            kategorije = sorted(list(set([info["category"] for info in filtriran_meni.values()])))
            tabs = st.tabs(kategorije)

            for i, tab in enumerate(tabs):
                with tab:
                    kat = kategorije[i]
                    jela = {k: v for k, v in filtriran_meni.items() if v["category"] == kat}
                    
                    for jelo, info in jela.items():
                        with st.container(border=True):
                            st.image(prikazi_sliku(info["image"]), use_container_width=True)
                            st.markdown(f"<h3 style='margin-bottom: 0;'>{jelo}</h3>", unsafe_allow_html=True)
                            
                            boja_dijete = "green" if info["diet"] == "Vegetarijansko" else "blue" if info["diet"] == "Posno" else "gray"
                            st.markdown(f"<span style='background-color: {boja_dijete}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;'>{info['diet']}</span>", unsafe_allow_html=True)
                            
                            st.markdown(f"<p style='color: gray; font-size: 14px; margin-top: 5px;'>{info['desc']}</p>", unsafe_allow_html=True)
                            
                            col_cena, col_dugme = st.columns([1, 1])
                            with col_cena: st.markdown(f"<h4 style='color: #E63946; margin-top: 5px;'>{info['price']:.2f} RSD</h4>", unsafe_allow_html=True)
                            with col_dugme:
                                if st.button("➕ Dodaj", key=f"add_{jelo}", use_container_width=True):
                                    moj_sto["stavke"][jelo] = moj_sto["stavke"].get(jelo, 0) + 1
                                    snimi_u_bazu(sto, moj_sto)
                                    st.toast(f"Dodano: {jelo}", icon="✅")
                                    st.rerun()
                            
                            with st.expander("Nutritivne vrijednosti"):
                                st.caption(f"🔥 {info['calories']} kcal | 🥩 {info['protein']}g proteina | 🍞 {info['carbs']}g uglj. hidrata | 🍬 {info['sugar']}g šećera | 🌾 {info['fiber']}g vlakana")

        # AI CHATBOT
        st.divider()
        st.markdown("### 🤖 AI Asistent")
        st.caption("Pitajte me za preporuku ili naručite hranu preko mene!")
        
        if "chat_history" not in st.session_state: st.session_state.chat_history = []
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]): st.markdown(message["content"])

        upit = st.chat_input("Napiši poruku...")
        if upit:
            st.session_state.chat_history.append({"role": "user", "content": upit})
            with st.chat_message("user"): st.markdown(upit)
                
            with st.chat_message("assistant"):
                try:
                    get_models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_KEY}"
                    models_response = requests.get(get_models_url)
                    
                    if models_response.status_code == 200:
                        radni_model = None
                        for m in models_response.json().get('models', []):
                            if 'generateContent' in m.get('supportedGenerationMethods', []):
                                radni_model = m['name']
                                break
                        
                        if radni_model:
                            api_contents = [{"role": "user" if msg["role"] == "user" else "model", "parts": [{"text": msg["content"]}]} for msg in st.session_state.chat_history]
                            url = f"https://generativelanguage.googleapis.com/v1beta/{radni_model}:generateContent?key={GEMINI_KEY}"
                            
                            sistemska_instrukcija = f"""Ti si konobar u Korzou. Meni: {list(menu_database.keys())}.
                            Ako gost traži naručivanje, MORAŠ koristiti točne nazive u formatu [DODAJ: Ime jela gramaža].
                            Primjer: [DODAJ: Bagrem piletina 350g]. Uvijek napiši i tekst potvrde."""

                            payload = {"systemInstruction": {"parts": [{"text": sistemska_instrukcija}]}, "contents": api_contents}
                            ai_response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
                            
                            if ai_response.status_code == 200:
                                odgovor = ai_response.json()['candidates'][0]['content']['parts'][0]['text']
                                komande_dodaj = re.findall(r'\[DODAJ:\s*(.*?)\]', odgovor)
                                dodato = False
                                for jelo_dodaj in komande_dodaj:
                                    jelo_dodaj = jelo_dodaj.strip()
                                    if jelo_dodaj in menu_database:
                                        moj_sto["stavke"][jelo_dodaj] = moj_sto["stavke"].get(jelo_dodaj, 0) + 1
                                        dodato = True
                                
                                cist_odgovor = re.sub(r'\[DODAJ:\s*.*?\]', '', odgovor).strip()
                                if not cist_odgovor: cist_odgovor = "Ubačeno u korpu! 🛒"
                                st.session_state.chat_history.append({"role": "assistant", "content": cist_odgovor})
                                
                                if dodato:
                                    snimi_u_bazu(sto, moj_sto)
                                    st.session_state.ai_toast = "AI je dodao jelo u korpu!"
                                    st.rerun()
                                else:
                                    st.markdown(cist_odgovor)
                            else: st.error("Greška API-ja.")
                    else: st.error("AI sistem nije dostupan.")
                except Exception as e: st.error(f"Greška: {e}")

    # ---------------------------------------------------------
    # EKRAN 2: KORPA
    # ---------------------------------------------------------
    elif st.session_state.ekran == "korpa":
        if st.button("⬅️ Nazad na meni"):
            st.session_state.ekran = "meni"
            st.rerun()
            
        st.markdown("<h2 style='text-align: center;'>🛒 Tvoja Korpa</h2>", unsafe_allow_html=True)
        st.divider()
        
        ukupno = 0
        stavke_korpa = moj_sto.get("stavke", {})
        
        if not stavke_korpa:
            st.info("Korpa je trenutno prazna. Vratite se na meni da dodate jela!")
        else:
            for jelo, qty in list(stavke_korpa.items()):
                if jelo in menu_database:
                    cena = menu_database[jelo]["price"] * qty
                    ukupno += cena
                    
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([1, 4, 1])
                        with c1: st.markdown(f"**{qty}x**")
                        with c2: st.markdown(f"**{jelo}**<br><span style='color:gray;'>{cena:.2f} RSD</span>", unsafe_allow_html=True)
                        with c3:
                            if st.button("🗑️", key=f"del_{jelo}"):
                                if moj_sto["stavke"][jelo] > 1: moj_sto["stavke"][jelo] -= 1
                                else: del moj_sto["stavke"][jelo]
                                snimi_u_bazu(sto, moj_sto)
                                st.rerun()
            
            st.divider()
            st.markdown(f"<h3 style='text-align: right;'>Ukupno: <span style='color:#E63946;'>{ukupno:.2f} RSD</span></h3>", unsafe_allow_html=True)
            
            st.write("")
            if st.button("🧾 ZATRAŽI RAČUN I PLATI", type="primary", use_container_width=True):
                moj_sto["trazi_racun"] = True
                moj_sto["konobar_stize"] = False
                snimi_u_bazu(sto, moj_sto)
                st.success("Konobar stiže s računom za Vaš stol!")
                time.sleep(2)
                st.session_state.ekran = "meni"
                st.rerun()

# ==========================================
# 5. GLAVNI RUTER (S LOGINOM)
# ==========================================
params = st.query_params

if "konobar" in params: 
    # LOGIN ZA KONOBARE
    if not st.session_state.get("ulogovan", False):
        st.markdown("<h2 style='text-align: center; margin-top:50px;'>🔒 Pristup za osoblje</h2>", unsafe_allow_html=True)
        with st.container(border=True):
            st.write("Unesite sigurnosni PIN kod da biste pristupili kontroli sale.")
            pin = st.text_input("PIN kod:", type="password")
            if st.button("Prijavi se", type="primary", use_container_width=True):
                if pin == "1234":
                    st.session_state.ulogovan = True
                    st.rerun()
                else:
                    st.error("❌ Pogrešan PIN! Pokušajte ponovo.")
    else:
        prikazi_konobara()
        
elif "sto" in params: 
    prikazi_gosta(params["sto"])
else:
    st.markdown("<h2 style='text-align: center;'>Dobrodošli u Korzo 🍽️</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### 📱 Za Goste")
            if st.button("Uđi kao Sto 1", use_container_width=True):
                st.query_params["sto"] = "1"
                st.rerun()
            if st.button("Uđi kao Sto 2", use_container_width=True):
                st.query_params["sto"] = "2"
                st.rerun()
    with col2:
        with st.container(border=True):
            st.markdown("### 👨‍🍳 Za Osoblje")
            if st.button("Otvori Kontrolni Panel", type="primary", use_container_width=True):
                st.query_params["konobar"] = "true"
                st.rerun()
