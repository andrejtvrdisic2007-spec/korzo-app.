import streamlit as st
import os
import time
import requests
import re
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
    /* Ресетовање маргина за мобилни изглед */
    .block-container { padding: 1rem 1rem 3rem 1rem; max-width: 600px; }
    
    /* Скривање Streamlit вишкова */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* Модерне картице за јела (Wolt стил) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.08) !important;
        margin-bottom: 15px;
        overflow: hidden;
        background-color: white;
    }
    
    /* Дугмићи са заобљеним ивицама */
    div.stButton > button {
        border-radius: 25px;
        font-weight: 700;
        border: none;
        box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
        transition: 0.2s;
    }
    div.stButton > button:active { transform: scale(0.95); }
    
    /* Примарно дугме (нпр. црвена Корзо боја) */
    div.stButton > button[kind="primary"] {
        background-color: #E63946;
        color: white;
    }
    
    /* Дизајн Категорија (Табова) да изгледају као "пилуле" */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; padding-bottom: 5px; }
    .stTabs [data-baseweb="tab"] { 
        border-radius: 20px; 
        padding: 8px 16px; 
        background-color: #f0f2f6; 
        border: none; 
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #2b2d42; 
        color: white; 
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. МЕНИ БАЗА
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
    return putanja if os.path.exists(putanja) else "https://via.placeholder.com/600x350.png?text=Корзо"

# ==========================================
# 3. ПАНЕЛ ЗА КОНОБАРА
# ==========================================
def prikazi_konobara():
    st.markdown("<h1 style='text-align: center; color: #E63946;'>👨‍🍳 Контролни Панел - Корзо</h1>", unsafe_allow_html=True)
    st.info("🔄 Екран се аутоматски освежава сваких 10 секунди.")
    st.divider()
    
    baza = ucitaj_iz_baze()
    if not baza: 
        st.success("✨ Тренутно нема активних поруџбина.")
    else:
        cols = st.columns(3)
        for i, (sto, podaci) in enumerate(baza.items()):
            with cols[i % 3]:
                if podaci.get('zove_konobara'):
                    st.error(f"🚨 СТО {sto} ЗОВЕ!")
                elif podaci.get('trazi_racun'):
                    st.warning(f"💳 СТО {sto} РАЧУН!")
                else:
                    st.info(f"📍 Сто {sto} - Активно")
                
                with st.container(border=True):
                    ukupno = 0
                    for jelo, kolicina in podaci.get("stavke", {}).items():
                        if jelo in menu_database:
                            ukupno += menu_database[jelo]["price"] * kolicina
                            st.write(f"🍽️ **{kolicina}x** {jelo}")
                    st.divider()
                    st.metric("За наплату:", f"{ukupno:.2f} RSD")
                    if st.button("✅ Затвори (Наплаћено)", key=f"del_{sto}", use_container_width=True):
                        obrisi_sto(sto)
                        st.rerun()
    time.sleep(10)
    st.rerun()

# ==========================================
# 4. СТРАНИЦА ЗА ГОСТА (АПП ДИЗАЈН)
# ==========================================
def prikazi_gosta(sto):
    # Иницијализација система за "промену екрана"
    if "ekran" not in st.session_state:
        st.session_state.ekran = "meni"
    
    baza = ucitaj_iz_baze()
    moj_sto = baza.get(sto, {"stavke": {}, "zove_konobara": False, "trazi_racun": False})

    # Приказивање Тоаст обавештења за АИ
    if "ai_toast" in st.session_state and st.session_state.ai_toast:
        st.toast(st.session_state.ai_toast, icon="🛒")
        st.session_state.ai_toast = "" 

    # ---------------------------------------------------------
    # ЕКРАН 1: ГЛАВНИ МЕНИ (Стил Wolt/Glovo)
    # ---------------------------------------------------------
    if st.session_state.ekran == "meni":
        # Заглавље са бројем ставки у корпи
        broj_stavki = sum(moj_sto.get("stavke", {}).values())
        
        st.markdown(f"<h1 style='text-align: center; margin-bottom: 0px;'>🍽️ Корзо</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: gray;'>Сто {sto} • Уживајте у храни</p>", unsafe_allow_html=True)
        
        # Контролна дугмад на врху (Корпа и Конобар)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🛒 Корпа ({broj_stavki})", type="primary", use_container_width=True):
                st.session_state.ekran = "korpa"
                st.rerun()
        with col2:
            if moj_sto["zove_konobara"]:
                if st.button("❌ Откажи позив", type="secondary", use_container_width=True):
                    moj_sto["zove_konobara"] = False
                    snimi_u_bazu(sto, moj_sto)
                    st.rerun()
            else:
                if st.button("🙋‍♂️ Конобар", use_container_width=True):
                    moj_sto["zove_konobara"] = True
                    snimi_u_bazu(sto, moj_sto)
                    st.toast("Конобар је позван!", icon="🔔")
                    st.rerun()

        st.write("") # Размак
        
        # Табови за категорије
        kategorije = sorted(list(set([info["category"] for info in menu_database.values()])))
        tabs = st.tabs(kategorije)

        for i, tab in enumerate(tabs):
            with tab:
                kat = kategorije[i]
                jela = {k: v for k, v in menu_database.items() if v["category"] == kat}
                
                for jelo, info in jela.items():
                    with st.container(border=True):
                        st.image(prikazi_sliku(info["image"]), use_container_width=True)
                        st.markdown(f"<h3 style='margin-bottom: 0;'>{jelo}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color: gray; font-size: 14px;'>{info['desc']}</p>", unsafe_allow_html=True)
                        
                        col_cena, col_dugme = st.columns([1, 1])
                        with col_cena:
                            st.markdown(f"<h4 style='color: #E63946; margin-top: 5px;'>{info['price']:.2f} RSD</h4>", unsafe_allow_html=True)
                        with col_dugme:
                            if st.button("➕ Додај", key=f"add_{jelo}", use_container_width=True):
                                moj_sto["stavke"][jelo] = moj_sto["stavke"].get(jelo, 0) + 1
                                snimi_u_bazu(sto, moj_sto)
                                st.toast(f"Додато: {jelo}", icon="✅")
                                st.rerun()
                        
                        with st.expander("Nutritivne vrednosti"):
                            st.caption(f"🔥 {info['calories']} kcal | 🥩 {info['protein']}g протеина | 🍞 {info['carbs']}g угљ. хидрата | 🍬 {info['sugar']}g шећера | 🌾 {info['fiber']}g влакана")

        # АИ ЧАТБОТ
        st.divider()
        st.markdown("### 🤖 АИ Асистент")
        st.caption("Питајте ме за препоруку или ми реците шта желите да поручите!")
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        upit = st.chat_input("Напиши поруку...")
        if upit:
            st.session_state.chat_history.append({"role": "user", "content": upit})
            with st.chat_message("user"):
                st.markdown(upit)
                
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
                            Ако гост тражи да наручи, МОРАШ користити тачне називе у формату [DODAJ: Име јела грамажа].
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
    # ЕКРАН 2: КОРПА (ПРЕКО ЦЕЛОГ ЕКРАНА)
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
                    
                    # Приказ ставке са дугметом за брисање
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([1, 4, 1])
                        with c1:
                            st.markdown(f"**{qty}x**")
                        with c2:
                            st.markdown(f"**{jelo}**<br><span style='color:gray;'>{cena:.2f} RSD</span>", unsafe_allow_html=True)
                        with c3:
                            if st.button("🗑️", key=f"del_{jelo}"):
                                if moj_sto["stavke"][jelo] > 1:
                                    moj_sto["stavke"][jelo] -= 1
                                else:
                                    del moj_sto["stavke"][jelo]
                                snimi_u_bazu(sto, moj_sto)
                                st.rerun()
            
            st.divider()
            st.markdown(f"<h3 style='text-align: right;'>Укупно: <span style='color:#E63946;'>{ukupno:.2f} RSD</span></h3>", unsafe_allow_html=True)
            
            st.write("")
            if st.button("🧾 ЗАТРАЖИ РАЧУН И ПЛАТИ", type="primary", use_container_width=True):
                moj_sto["trazi_racun"] = True
                snimi_u_bazu(sto, moj_sto)
                st.success("Конобар стиже са рачуном за Ваш сто!")
                time.sleep(2)
                st.session_state.ekran = "meni"
                st.rerun()

# ==========================================
# 5. ГЛАВНИ РУТЕР
# ==========================================
params = st.query_params
if "konobar" in params: 
    prikazi_konobara()
elif "sto" in params: 
    prikazi_gosta(params["sto"])
else:
    st.markdown("<h2 style='text-align: center;'>Добродошли у Корзо 🍽️</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### 📱 За Госте")
            if st.button("Уђи као Сто 1", use_container_width=True):
                st.query_params["sto"] = "1"
                st.rerun()
    with col2:
        with st.container(border=True):
            st.markdown("### 👨‍🍳 За Особље")
            if st.button("Отвори Контролни Панел", type="primary", use_container_width=True):
                st.query_params["konobar"] = "true"
                st.rerun()
