import streamlit as st
import os
import time
import requests
import re
import difflib
from st_keyup import st_keyup
from supabase import create_client, Client

# ==========================================
# 1. СИГУРНО ПОДЕШАВАЊЕ
# ==========================================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ ГРЕШКА: GEMINI_API_KEY није подешен у Streamlit Secrets!")
    st.stop()

GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
SUPABASE_URL = "https://mszsrorxwmkopoyvsbpw.supabase.co"
SUPABASE_KEY = "sb_publishable_mYfAEgWeQqUcjTIKqORx5w_A4hSqIc_"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Корзо | Дигитални Мени", page_icon="🍽️", layout="centered", initial_sidebar_state="collapsed")

# --- WOLT/GLOVO СТИЛ (CSS) ---
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
# 2. БАЗА МЕНИЈА И ПАМЕТНА ПРЕТРАГА
# ==========================================
menu_database = {
    "Korzo doručak": {"category": "Doručak", "price": 630.00, "calories": 750, "protein": 35, "carbs": 45, "sugar": 5, "fiber": 4, "diet": "Meso", "desc": "2 jaja, sudžuk, goveđa pršuta, ajvar, sir", "image": "slike/korzo_dorucak.jpg"},
    "Kajgana": {"category": "Doručak", "price": 350.00, "calories": 300, "protein": 20, "carbs": 2, "sugar": 1, "fiber": 0, "diet": "Vegetarijansko", "desc": "Domaća kajgana", "image": "slike/kajgana.jpg"},
    "Kačamak": {"category": "Doručak", "price": 300.00, "calories": 400, "protein": 8, "carbs": 55, "sugar": 2, "fiber": 3, "diet": "Vegetarijansko", "desc": "Tradicionalni domaći kačamak", "image": "slike/kacamak.jpg"},
    "Juneća čorba 350g": {"category": "Toplo predjelo", "price": 480.00, "calories": 250, "protein": 18, "carbs": 15, "sugar": 3, "fiber": 2, "diet": "Meso", "desc": "Domaća topla juneća čorba", "image": "slike/juneca_corba.jpg"},
    "Juneће ćufte 350g": {"category": "Roštilj", "price": 990.00, "calories": 650, "protein": 45, "carbs": 10, "sugar": 2, "fiber": 1, "diet": "Meso", "desc": "Sočne juneće ćufte sa roštilja", "image": "slike/junece_cufte.jpg"},
    "Juneći ćevapi 350g": {"category": "Roštilj", "price": 960.00, "calories": 700, "protein": 50, "carbs": 5, "sugar": 1, "fiber": 0, "diet": "Meso", "desc": "Pravi domaći juneћи ćevapi", "image": "slike/juneci_cevapi.jpg"},
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

# --- ФУНКЦИЈЕ ЗА БАЗУ ---
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
# 3. КОНТРОЛНИ ПАНЕЛ ЗА КОНОБАРА (ЛОГИН + МАПА)
# ==========================================
def prikazi_konobara():
    st.markdown("<h1 style='text-align: center; color: #E63946;'>👨‍🍳 Контролни Панел - Корзо</h1>", unsafe_allow_html=True)
    
    # Табови: Мапа, Листа поруџбина, Статистика
    tab_mapa, tab_stolovi, tab_statistika = st.tabs(["🗺️ Мапа Сале", "🍽️ Листа Поруџбина", "📊 Дневни Пазар"])
    baza = ucitaj_iz_baze()
    aktivni_stolovi = {k: v for k, v in baza.items() if k != "admin_statistika"}
    zvoni_alarm = False
    
    # ТАБ 1: ВИЗУЕЛНА МАПА СТОЛОВА
    with tab_mapa:
        st.markdown("### Тренутно стање у сали")
        st.caption("🟢 Слободно | 🔵 Заузето (Једу) | 🚨 Хитна услуга")
        
        # Дефинишемо столове у сали (нпр. 6 столова за сада)
        svi_stolovi = ["1", "2", "3", "4", "5", "6"]
        cols = st.columns(3)
        
        for i, sto_id in enumerate(svi_stolovi):
            with cols[i % 3]:
                podaci_stola = aktivni_stolovi.get(sto_id)
                
                if not podaci_stola:
                    # Сто је слободан
                    boja = "#2b9348" # Зелена
                    st.markdown(f"<div style='background-color:{boja}; padding:15px; border-radius:15px; text-align:center; color:white; margin-bottom:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'><h2>🟢 {sto_id}</h2><b>Слободан</b></div>", unsafe_allow_html=True)
                elif podaci_stola.get('zove_konobara') or podaci_stola.get('trazi_racun'):
                    # Сто тражи услугу
                    boja = "#d90429" # Црвена
                    razlog = "Рачун!" if podaci_stola.get('trazi_racun') else "Конобар!"
                    st.markdown(f"<div style='background-color:{boja}; padding:15px; border-radius:15px; text-align:center; color:white; margin-bottom:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'><h2>🚨 {sto_id}</h2><b>{razlog}</b></div>", unsafe_allow_html=True)
                else:
                    # Сто је заузет (само поруџбина)
                    boja = "#0077b6" # Плава
                    st.markdown(f"<div style='background-color:{boja}; padding:15px; border-radius:15px; text-align:center; color:white; margin-bottom:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'><h2>🔵 {sto_id}</h2><b>Заузет</b></div>", unsafe_allow_html=True)

    # ТАБ 2: ДЕТАЉИ ПОРУЏБИНА
    with tab_stolovi:
        if not aktivni_stolovi: 
            st.success("✨ Тренутно нема активних поруџбина.")
        else:
            cols = st.columns(3)
            i = 0
            for sto, podaci in aktivni_stolovi.items():
                with cols[i % 3]:
                    # Провера да ли треба аларм
                    if (podaci.get('zove_konobara') or podaci.get('trazi_racun')) and not podaci.get('konobar_stize'):
                        zvoni_alarm = True
                    
                    with st.container(border=True):
                        st.markdown(f"<h3 style='text-align: center;'>📍 Сто {sto}</h3>", unsafe_allow_html=True)
                        
                        if podaci.get('zove_konobara') or podaci.get('trazi_racun'):
                            razlog = "💳 ТРАЖИ РАЧУН" if podaci.get('trazi_racun') else "🚨 ЗОВЕ ВАС"
                            if podaci.get('konobar_stize'):
                                st.success("🏃‍♂️ Кренули сте ка столу.")
                            else:
                                st.error(f"**{razlog}**")
                                if st.button("✅ Прихвати позив", key=f"prihvati_{sto}", width='stretch'):
                                    podaci["konobar_stize"] = True
                                    snimi_u_bazu(sto, podaci)
                                    st.rerun()
                        else:
                            st.info("🍽️ Активна поруџбина")
                        
                        ukupno = 0
                        for jelo, kolicina in podaci.get("stavke", {}).items():
                            if jelo in menu_database:
                                ukupno += menu_database[jelo]["price"] * kolicina
                                st.write(f"▪️ **{kolicina}x** {jelo}")
                        
                        st.divider()
                        st.metric("За наплату:", f"{ukupno:.2f} RSD")
                        
                        if st.button("💰 Наплати и Затвори", key=f"del_{sto}", type="primary", width='stretch'):
                            stat_podaci = baza.get("admin_statistika", {"sto": "admin_statistika", "stavke": {}})
                            stat_podaci["stavke"]["_ukupno_zarada"] = stat_podaci.get("stavke", {}).get("_ukupno_zarada", 0) + ukupno
                            for j, q in podaci.get("stavke", {}).items():
                                stat_podaci["stavke"][j] = stat_podaci["stavke"].get(j, 0) + q
                            snimi_u_bazu("admin_statistika", stat_podaci)
                            obrisi_sto(sto)
                            st.rerun()
                i += 1

    # ТАБ 3: ДНЕВНИ ПАЗАР
    with tab_statistika:
        stat_podaci = baza.get("admin_statistika", {"stavke": {}})
        ukupno_zarada = stat_podaci.get("stavke", {}).get("_ukupno_zarada", 0)
        
        st.markdown(f"### 💰 Укупан пазар данас: **{ukupno_zarada:.2f} RSD**")
        st.divider()
        st.markdown("#### 🏆 Продата јела и пића:")
        
        prodato = {k: v for k, v in stat_podaci.get("stavke", {}).items() if k != "_ukupno_zarada"}
        prodato_sortirano = sorted(prodato.items(), key=lambda x: x[1], reverse=True)
        
        if not prodato_sortirano:
            st.info("Још увек нема наплаћених јела.")
        else:
            for jelo, kolicina in prodato_sortirano:
                st.write(f"✔️ **{kolicina}x** {jelo}")
        
        st.write("")
        if st.button("🗑️ Затвори смену (Ресетуј пазар)", type="primary"):
            obrisi_sto("admin_statistika")
            st.success("Пазар је успешно ресетован!")
            time.sleep(1)
            st.rerun()

    # ЗВУЧНИ АЛАРМ
    if zvoni_alarm:
        st.components.v1.html(
            '''<audio autoplay loop><source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg"></audio>''',
            height=0, width=0
        )
            
    time.sleep(10)
    st.rerun()

# ==========================================
# 4. СТРАНИЦА ЗА ГОСТА
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
        
        st.markdown(f"<h1 style='text-align: center; margin-bottom: 0px;'>🍽️ Корзо</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: gray;'>Сто {sto} • Уживајте у храни</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🛒 Корпа ({broj_stavki})", type="primary", width='stretch'):
                st.session_state.ekran = "korpa"
                st.rerun()
        with col2:
            if moj_sto["zove_konobara"] or moj_sto["trazi_racun"]:
                if moj_sto.get("konobar_stize"):
                    st.button("🏃‍♂️ Конобар стиже!", disabled=True, width='stretch')
                else:
                    if st.button("❌ Откажи позив", type="secondary", width='stretch'):
                        moj_sto["zove_konobara"] = False
                        moj_sto["trazi_racun"] = False
                        snimi_u_bazu(sto, moj_sto)
                        st.rerun()
            else:
                if st.button("🙋‍♂️ Конобар", width='stretch'):
                    moj_sto["zove_konobara"] = True
                    moj_sto["konobar_stize"] = False
                    snimi_u_bazu(sto, moj_sto)
                    st.toast("Конобар је позван!", icon="🔔")
                    st.rerun()

        st.write("") 
        
        with st.expander("🔍 Филтери и претрага (куцај слободно)"):
            search_tekst = st_keyup("Шта вам се једе данас?", placeholder="нпр. 'prebranac', 'cevapi', 'gulas'...", debounce=300)
            if not search_tekst: search_tekst = ""
            
            c_cena, c_ishrana = st.columns(2)
            with c_cena: max_cena = st.slider("Макс. цена (RSD)", 100, 2000, 2000, step=50)
            with c_ishrana: odabrana_ishrana = st.multiselect("Врста исхране", ["Meso", "Vegetarijansko", "Posno"])
        
        filtriran_meni = {}
        for ime, info in menu_database.items():
            if not proveri_poklapanje(search_tekst, ime): continue
            if info["price"] > max_cena: continue
            if odabrana_ishrana and info["diet"] not in odabrana_ishrana: continue
            filtriran_meni[ime] = info

        if not filtriran_meni:
            st.warning("Ниједно јело не одговара уносу. Да ли сте мислили на нешто друго?")
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
                                if st.button("➕ Додај", key=f"add_{jelo}", width='stretch'):
                                    moj_sto["stavke"][jelo] = moj_sto["stavke"].get(jelo, 0) + 1
                                    snimi_u_bazu(sto, moj_sto)
                                    st.toast(f"Додато: {jelo}", icon="✅")
                                    st.rerun()
                            
                            with st.expander("Нутритивне вредности"):
                                st.caption(f"🔥 {info['calories']} kcal | 🥩 {info['protein']}g протеина | 🍞 {info['carbs']}g угљ. хидрата | 🍬 {info['sugar']}g шећера | 🌾 {info['fiber']}g влакана")

        # АИ ЧАТБОТ
        st.divider()
        st.markdown("### 🤖 АИ Асистент")
        st.caption("Питајте ме за препоруку или наручите храну преко мене!")
        
        if "chat_history" not in st.session_state: st.session_state.chat_history = []
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]): st.markdown(message["content"])

        upit = st.chat_input("Напиши поруку...")
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
                            
                            sistemska_instrukcija = f"""Ти си конобар у Корзоу. Мени: {list(menu_database.keys())}.
                            Ако гост тражи наручивање, МОРАШ користити тачне називе у формату [DODAJ: Име јела грамажа].
                            Пример: [DODAJ: Bagrem piletina 350g]. Увек напиши и текст потврде."""

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
                                if not cist_odgovor: cist_odgovor = "Убачено у корпу! 🛒"
                                st.session_state.chat_history.append({"role": "assistant", "content": cist_odgovor})
                                
                                if dodato:
                                    snimi_u_bazu(sto, moj_sto)
                                    st.session_state.ai_toast = "АИ је додао јело у корпу!"
                                    st.rerun()
                                else:
                                    st.markdown(cist_odgovor)
                            else: st.error("Грешка АПИ-ја.")
                    else: st.error("АИ систем није доступан.")
                except Exception as e: st.error(f"Грешка: {e}")

    # ---------------------------------------------------------
    # ЕКРАН 2: КОРПА
    # ---------------------------------------------------------
    elif st.session_state.ekran == "korpa":
        if st.button("⬅️ Назад на мени"):
            st.session_state.ekran = "meni"
            st.rerun()
            
        st.markdown("<h2 style='text-align: center;'>🛒 Твоја Корпа</h2>", unsafe_allow_html=True)
        st.divider()
        
        ukupno = 0
        stavke_korpa = moj_sto.get("stavke", {})
        
        if not stavke_korpa:
            st.info("Корпа је тренутно празна. Вратите се на мени да додате јела!")
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
            st.markdown(f"<h3 style='text-align: right;'>Укупно: <span style='color:#E63946;'>{ukupno:.2f} RSD</span></h3>", unsafe_allow_html=True)
            
            st.write("")
            if st.button("🧾 ЗАТРАЖИ РАЧУН И ПЛАТИ", type="primary", width='stretch'):
                moj_sto["trazi_racun"] = True
                moj_sto["konobar_stize"] = False
                snimi_u_bazu(sto, moj_sto)
                st.success("Конобар стиже са рачуном за Ваш сто!")
                time.sleep(2)
                st.session_state.ekran = "meni"
                st.rerun()

# ==========================================
# 5. ГЛАВНИ РУТЕР (СА ЛОГИНОМ)
# ==========================================
params = st.query_params

if "konobar" in params: 
    # ЛОГИН ЗА КОНОБАРЕ
    if not st.session_state.get("ulogovan", False):
        st.markdown("<h2 style='text-align: center; margin-top:50px;'>🔒 Приступ за особље</h2>", unsafe_allow_html=True)
        with st.container(border=True):
            st.write("Унесите сигурносни ПИН код да бисте приступили контроли сале.")
            pin = st.text_input("ПИН код:", type="password")
            if st.button("Пријави се", type="primary", width='stretch'):
                if pin == "1234":
                    st.session_state.ulogovan = True
                    st.rerun()
                else:
                    st.error("❌ Погрешан ПИН! Покушајте поново.")
    else:
        prikazi_konobara()
        
elif "sto" in params: 
    prikazi_gosta(params["sto"])
else:
    st.markdown("<h2 style='text-align: center;'>Добродошли у Корзо 🍽️</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### 📱 За Госте")
            if st.button("Уђи као Сто 1", width='stretch'):
                st.query_params["sto"] = "1"
                st.rerun()
            if st.button("Уђи као Сто 2", width='stretch'):
                st.query_params["sto"] = "2"
                st.rerun()
    with col2:
        with st.container(border=True):
            st.markdown("### 👨‍🍳 За Особље")
            if st.button("Отвори Контролни Панел", type="primary", width='stretch'):
                st.query_params["konobar"] = "true"
                st.rerun()
