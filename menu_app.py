import streamlit as st
import os
import time
import requests
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

# Подешавање изгледа странице
st.set_page_config(page_title="Корзо | Дигитални Мени", page_icon="🍽️", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 2. МЕНИ БАЗА (СВИХ 21 СТАВКА)
# ==========================================
menu_database = {
    "Korzo doručak": {"category": "Doručak", "price": 630.00, "calories": 750, "desc": "2 jaja, sudžuk, goveđa pršuta, ajvar, sir", "image": "slike/korzo_dorucak.jpg"},
    "Kajgana": {"category": "Doručak", "price": 350.00, "calories": 300, "desc": "Domaća kajgana", "image": "slike/kajgana.jpg"},
    "Kačamak": {"category": "Doručak", "price": 300.00, "calories": 400, "desc": "Tradicionalni domaći kačamak", "image": "slike/kacamak.jpg"},
    "Juneća čorba 350g": {"category": "Toplo predjelo", "price": 480.00, "calories": 250, "desc": "Domaća topla juneća čorba", "image": "slike/juneca_corba.jpg"},
    "Juneće ćufte 350g": {"category": "Roštilj", "price": 990.00, "calories": 650, "desc": "Sočne juneće ćufte sa roštilja", "image": "slike/junece_cufte.jpg"},
    "Juneći ćevapi 350g": {"category": "Roštilj", "price": 960.00, "calories": 700, "desc": "Pravi domaći juneći ćevapi", "image": "slike/juneci_cevapi.jpg"},
    "Bagrem piletina 350g": {"category": "Roštilj", "price": 900.00, "calories": 500, "desc": "Specijalitet kuće od piletine", "image": "slike/bagrem_piletina.jpg"},
    "Goveđa pršuta 100g": {"category": "Hladno predjelo", "price": 900.00, "calories": 250, "desc": "Kvalitetna domaća goveđa pršuta", "image": "slike/govedja_prsuta.jpg"},
    "Sušeni sudžuk 100g": {"category": "Hladno predjelo", "price": 480.00, "calories": 400, "desc": "Domaći sušeni sudžuk", "image": "slike/suseni_sudzuk.jpg"},
    "Sir 100g": {"category": "Hladno predjelo", "price": 340.00, "calories": 350, "desc": "Domaći beli sir", "image": "slike/sir.jpg"},
    "Mađarski juneći gulaš 450g": {"category": "Glavno jelo", "price": 1020.00, "calories": 600, "desc": "Bogati mađarski gulaš od junetine", "image": "slike/madjarski_gulas.jpg"},
    "Ćufte u pireu 350g": {"category": "Glavno jelo", "price": 660.00, "calories": 550, "desc": "Domaće ćufte u kremastom pireu", "image": "slike/cufte_u_pireu.jpg"},
    "Prebranac sa sudžukom 400g": {"category": "Glavno jelo", "price": 760.00, "calories": 650, "desc": "Zapečeni pasulj sa sudžukom", "image": "slike/prebranac_sudzuk.jpg"},
    "Prebranac 300g": {"category": "Glavno jelo", "price": 590.00, "calories": 400, "desc": "Tradicionalni posni prebranac", "image": "slike/prebranac.jpg"},
    "Šopska salata 350g": {"category": "Salate", "price": 460.00, "calories": 200, "desc": "Paradajz, krastavac, luk, paprika, sir", "image": "slike/sopska_salata.jpg"},
    "Srpska salata 300g": {"category": "Salate", "price": 410.00, "calories": 100, "desc": "Paradajz, krastavac, luk, ljuta paprika", "image": "slike/srpska_salata.jpg"},
    "Kupus salata 300g": {"category": "Salate", "price": 330.00, "calories": 80, "desc": "Sveža kupus salata", "image": "slike/kupus_salata.jpg"},
    "Ljuta paprika u ulju 1 komad": {"category": "Salate", "price": 150.00, "calories": 50, "desc": "Pečena ljuta paprika", "image": "slike/ljuta_paprika.jpg"},
    "Lepinja 1 komad": {"category": "Dodaci", "price": 120.00, "calories": 250, "desc": "Sveža domaća lepinja", "image": "slike/lepinja.jpg"},
    "Pomfrit 150g": {"category": "Dodaci", "price": 300.00, "calories": 450, "desc": "Hrskavi prženi krompirići", "image": "slike/pomfrit.jpg"},
    "Kugla kajmaka 1 komad": {"category": "Dodaci", "price": 180.00, "calories": 200, "desc": "Domaći zreli kajmak", "image": "slike/kugla_kajmaka.jpg"}
}

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
        "trazi_racun": podaci.get("trazi_racun", False)
    }
    if len(provera.data) > 0: supabase.table("porudzbine").update(nova_data).eq("sto", sto).execute()
    else: supabase.table("porudzbine").insert(nova_data).execute()

def obrisi_sto(sto):
    supabase.table("porudzbine").delete().eq("sto", sto).execute()

def prikazi_sliku(putanja):
    return putanja if os.path.exists(putanja) else "https://via.placeholder.com/600x400.png?text=Корзо+Крагујевац"

# ==========================================
# 3. ПАНЕЛ ЗА КОНОБАРА (ЛЕПШИ И ПРЕГЛЕДНИЈИ)
# ==========================================
def prikazi_konobara():
    st.markdown("<h1 style='text-align: center; color: #E63946;'>👨‍🍳 Контролни Панел - Корзо</h1>", unsafe_allow_html=True)
    st.info("🔄 Екран се аутоматски освежава сваких 10 секунди.")
    st.divider()
    
    baza = ucitaj_iz_baze()
    if not baza: 
        st.success("✨ Тренутно нема активних поруџбина. Ресторан је миран!")
    else:
        cols = st.columns(3)
        for i, (sto, podaci) in enumerate(baza.items()):
            with cols[i % 3]:
                # Боја картице се мења ако гост зове или тражи рачун
                if podaci.get('zove_konobara'):
                    st.error(f"🚨 СТО {sto} ВАС ЗОВЕ!")
                elif podaci.get('trazi_racun'):
                    st.warning(f"💳 СТО {sto} ТРАЖИ РАЧУН!")
                else:
                    st.info(f"📍 Сто {sto} - Активна поруџбина")
                
                with st.container(border=True):
                    ukupno = 0
                    st.markdown("### Поручено:")
                    for jelo, kolicina in podaci.get("stavke", {}).items():
                        if jelo in menu_database:
                            ukupno += menu_database[jelo]["price"] * kolicina
                            st.write(f"🍽️ **{kolicina}x** {jelo}")
                        else:
                            st.write(f"⚠️ {jelo} (Није у менију)")
                    
                    st.divider()
                    st.metric("За наплату:", f"{ukupno:.2f} RSD")
                    
                    if st.button("✅ Затвори сто (Наплаћено)", key=f"del_{sto}", use_container_width=True):
                        obrisi_sto(sto)
                        st.rerun()
    time.sleep(10)
    st.rerun()

# ==========================================
# 4. СТРАНИЦА ЗА ГОСТА (ПРЕМИЈУМ ИЗГЛЕД)
# ==========================================
def prikazi_gosta(sto):
    baza = ucitaj_iz_baze()
    moj_sto = baza.get(sto, {"stavke": {}, "zove_konobara": False, "trazi_racun": False})

    # --- САЈДБАР (МОЈ РАЧУН И ПОЗИВИ) ---
    with st.sidebar:
        st.markdown(f"<h2 style='text-align: center;'>📍 Ваш Сто: {sto}</h2>", unsafe_allow_html=True)
        st.divider()
        
        # Дугме за позив
        if st.button("🙋‍♂️ ПОЗОВИ КОНОБАРА", type="primary", use_container_width=True):
            moj_sto["zove_konobara"] = True
            snimi_u_bazu(sto, moj_sto)
            st.success("Особље је обавештено и стиже ускоро!")

        st.divider()
        st.markdown("### 🛒 Ваша Корпа")
        ukupno = 0
        ставке = moj_sto.get("stavke", {})
        
        if не ставке:
            st.info("Ваша корпа је тренутно празна.")
        else:
            for jelo, qty in ставке.items():
                if jelo in menu_database:
                    цена_ставке = menu_database[jelo]["price"] * qty
                    ukupno += цена_ставке
                    st.markdown(f"**{qty}x** {jelo} <br> *{цена_ставке:.2f} RSD*", unsafe_allow_html=True)
            
            st.divider()
            st.metric("Укупно за плаћање:", f"{ukupno:.2f} RSD")
            
            # Дугме за рачун
            if st.button("🧾 ЗАТРАЖИ РАЧУН", use_container_width=True):
                moj_sto["trazi_racun"] = True
                snimi_u_bazu(sto, moj_sto)
                st.warning("Конобар долази са Вашим рачуном!")

    # --- ГЛАВНИ ПРИКАЗ МЕНИЈА ---
    st.markdown("<h1 style='text-align: center;'>🍽️ Добродошли у Корзо</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Изаберите категорију и уживајте у нашој храни.</p>", unsafe_allow_html=True)
    st.write("")

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
                        # Слика преко целе ширине картице
                        st.image(prikazi_sliku(info["image"]), width='stretch')
                        
                        st.markdown(f"### {ime}")
                        st.markdown(f"**{info['price']:.2f} RSD**")
                        st.caption(info['desc'])
                        
                        # Експандер за детаље
                        with st.expander("ℹ️ Нутритивне вредности"):
                            st.write(f"🔥 Калорије: **{info['calories']} kcal**")
                            if "protein" in info:
                                st.write(f"🥩 Протеини: **{info['protein']}g**")

                        # Дугме за додавање у корпу
                        if st.button(f"➕ Додај у корпу", key=f"add_{ime}", use_container_width=True):
                            moj_sto["stavke"][ime] = moj_sto["stavke"].get(ime, 0) + 1
                            snimi_u_bazu(sto, moj_sto)
                            st.rerun()

    # --- ДИРЕКТАН АИ ПОЗИВ ---
    st.divider()
    st.markdown("### 🤖 Имате питање? Питајте нашег АИ конобара!")
    upit = st.chat_input("Питај ме нешто о менију (нпр. 'Шта препоручујеш за доручак?')...")
    
    if upit:
        with st.chat_message("user"): st.markdown(upit)
        with st.chat_message("assistant"):
            try:
                # Најстабилнији директан позив без икаквих пакета
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": f"Ти си љубазни конобар у ресторану Корзо у Крагујевцу. Наш мени: {list(menu_database.keys())}. Одговори кратко, љубазно и на српском језику. Питање госта: {upit}"}]}]
                }
                response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
                
                if response.status_code == 200:
                    odgovor = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(odgovor)
                else:
                    st.error("Извините, тренутно сам заузет. Позовите правог конобара преко дугмета лево!")
            except Exception as e:
                st.error("Систем за ћаскање тренутно није доступан.")

# ==========================================
# 5. ГЛАВНИ РУТЕР
# ==========================================
params = st.query_params
if "konobar" in params: 
    prikazi_konobara()
elif "sto" in params: 
    prikazi_gosta(params["sto"])
else:
    # ПОЧЕТНА СТРАНИЦА ЗА ТЕСТИРАЊЕ
    st.markdown("<h1 style='text-align: center;'>Добродошли у Корзо Систем 🍽️</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### 📱 За Госте")
            st.write("Скенирајте QR код на столу или уђите овде за тест.")
            if st.button("Уђи као Сто 1", use_container_width=True):
                st.query_params["sto"] = "1"
                st.rerun()
            if st.button("Уђи као Сто 2", use_container_width=True):
                st.query_params["sto"] = "2"
                st.rerun()
                
    with col2:
        with st.container(border=True):
            st.markdown("### 👨‍🍳 За Особље")
            st.write("Приступ контролном панелу за праћење поруџбина.")
            if st.button("Отвори Контролни Панел", type="primary", use_container_width=True):
                st.query_params["konobar"] = "true"
                st.rerun()
