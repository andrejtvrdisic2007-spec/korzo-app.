import streamlit as st
import os
import json
from google import genai 

# ==========================================
# ПОДЕШАВАЊЕ СТРАНИЦЕ И AI МОДЕЛА
# ==========================================
st.set_page_config(page_title="Корзо Паметни Систем", page_icon="🍽️", layout="wide")

# ОВДЕ УНЕСИ СВОЈ НОВИ ГУГЛ КЉУЧ 
API_KEY = "AIzaSyBnOVsjyjJEnConG1mf7MNfHUNECktqUUY" 

try:
    client = genai.Client(api_key=API_KEY)
except:
    client = None

# ==========================================
# БАЗА ПОДАТАКА (JSON ФАЈЛ)
# ==========================================
DB_FILE = "baza_podataka.json"

def ucitaj_bazu():
    """Чита стање свих столова из фајла."""
    if not os.path.exists(DB_FILE):
        return {} # Враћа празну базу ако фајл не постоји
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def sacuvaj_bazu(podaci):
    """Уписује нове промене у фајл да би их сви видели."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(podaci, f, indent=4, ensure_ascii=False)

# ==========================================
# ПОДАЦИ О МЕНИЈУ
# ==========================================
menu_database = {
    "Korzo doručak": {"category": "Doručak", "price": 630.00, "calories": 750, "protein": 35, "carbs": 20, "fats": 55, "allergens": "Jaja, Mleko", "description": "2 jaja, sudžuk, goveđa pršuta, ajvar, sir", "image": "slike/korzo_dorucak.jpg"},
    "Kajgana": {"category": "Doručak", "price": 350.00, "calories": 300, "protein": 20, "carbs": 2, "fats": 22, "allergens": "Jaja", "description": "Domaća kajgana", "image": "slike/kajgana.jpg"},
    "Juneći ćevapi 350g": {"category": "Roštilj", "price": 960.00, "calories": 700, "protein": 50, "carbs": 5, "fats": 50, "allergens": "Nema", "description": "Pravi domaći juneći ćevapi", "image": "slike/juneci_cevapi.jpg"},
    "Šopska salata 350g": {"category": "Salate", "price": 460.00, "calories": 200, "protein": 8, "carbs": 10, "fats": 15, "allergens": "Mleko", "description": "Paradajz, krastavac, luk, paprika, sir", "image": "slike/sopska_salata.jpg"},
    "Lepinja 1 komad": {"category": "Dodaci", "price": 120.00, "calories": 250, "protein": 7, "carbs": 50, "fats": 2, "allergens": "Gluten", "description": "Sveža domaća lepinja", "image": "slike/lepinja.jpg"}
} # Напомена: Овде сам мало скратио мени због прегледности кода, слободно врати цео свој речник касније!

def prikazi_sliku(putanja):
    return putanja if os.path.exists(putanja) else "https://via.placeholder.com/500x300.png?text=Slika+uskoro"

# ==========================================
# 1. СТРАНИЦА ЗА КОНОБАРА (ПАНЕЛ)
# ==========================================
def prikazi_konobarski_panel():
    st.title("👨‍🍳 Контролни Панел за Конобаре")
    st.info("Ова страница стоји на рачунару за шанком. Аутоматски се ажурира када кликнете 'Освежи'.")
    
    if st.button("🔄 Освежи стање у ресторану", type="primary"):
        st.rerun()

    st.markdown("---")
    baza = ucitaj_bazu()
    
    if not baza:
        st.success("Тренутно нема активних столова. Ресторан је празан.")
        return

    cols = st.columns(3)
    col_idx = 0
    
    for sto, podaci in baza.items():
        with cols[col_idx]:
            with st.container(border=True):
                st.subheader(f"Сто {sto}")
                
                # Упозорења за конобара
                if podaci.get("zove_konobara"):
                    st.error("🔔 ГОСТ ЗОВЕ КОНОБАРА!")
                if podaci.get("trazi_racun"):
                    nacin = podaci.get("nacin_placanja", "Кеш")
                    st.warning(f"💳 ТРАЖИ РАЧУН ({nacin})")
                
                # Приказ поруџбине
                st.write("**Поруџбина:**")
                ukupno = 0
                for jelo, kolicina in podaci.get("porudzbina", {}).items():
                    cena = menu_database[jelo]["price"] * kolicina
                    ukupno += cena
                    st.write(f"- {kolicina}x {jelo} ({cena} RSD)")
                
                st.metric("Укупна задужења:", f"{ukupno:.2f} RSD")
                
                # Дугмад за конобара (решавање захтева)
                if st.button(f"✅ Решен позив/рачун", key=f"reseno_{sto}"):
                    baza[sto]["zove_konobara"] = False
                    baza[sto]["trazi_racun"] = False
                    sacuvaj_bazu(baza)
                    st.rerun()
                    
                if st.button(f"🧹 Очисти сто (Наплаћено)", key=f"ocisti_{sto}"):
                    del baza[sto]
                    sacuvaj_bazu(baza)
                    st.rerun()
                    
        col_idx = (col_idx + 1) % 3

# ==========================================
# 2. СТРАНИЦА ЗА ГОСТА (ПРЕКО QR КОДА)
# ==========================================
def prikazi_stranicu_za_gosta(broj_stola):
    baza = ucitaj_bazu()
    
    # Ако сто не постоји у бази, правимо га
    if broj_stola not in baza:
        baza[broj_stola] = {
            "porudzbina": {},
            "zove_konobara": False,
            "trazi_racun": False,
            "nacin_placanja": ""
        }
        sacuvaj_bazu(baza)

    st.sidebar.header(f"📍 Ваш Сто: {broj_stola}")
    
    # -- ДУГМАД ЗА ИНТЕРАКЦИЈУ СА КОНОБАРОМ --
    st.sidebar.markdown("### 🔔 Позовите особље")
    if st.sidebar.button("🙋‍♂️ Позови конобара", use_container_width=True):
        baza[broj_stola]["zove_konobara"] = True
        sacuvaj_bazu(baza)
        st.sidebar.success("Конобар је обавештен и стиже ускоро!")

    st.sidebar.markdown("### 💳 Плаћање")
    nacin = st.sidebar.radio("Како желите да платите?", ["Кеш", "Картица"])
    if st.sidebar.button("🧾 Затражи рачун", type="primary", use_container_width=True):
        baza[broj_stola]["trazi_racun"] = True
        baza[broj_stola]["nacin_placanja"] = nacin
        sacuvaj_bazu(baza)
        st.sidebar.success(f"Затражили сте рачун ({nacin}). Конобар стиже!")

    # -- ПРИКАЗ КОРПЕ И ПОРУЧИВАЊЕ --
    st.sidebar.markdown("---")
    st.sidebar.header("🛒 Ваш тренутни рачун")
    ukupno = 0
    trenutna_porudzbina = baza[broj_stola].get("porudzbina", {})
    
    if trenutna_porudzbina:
        for jelo, qty in trenutna_porudzbina.items():
            cena = menu_database[jelo]["price"] * qty
            ukupno += cena
            st.sidebar.write(f"**{qty}x** {jelo} - {cena} RSD")
        st.sidebar.metric(label="За плаћање:", value=f"{ukupno:.2f} RSD")
    else:
        st.sidebar.info("Још увек нисте ништа поручили.")

    # -- ПРИКАЗ МЕНИЈА --
    st.title("🍽️ Корзо Мени")
    st.markdown(f"Добродошли! Ви седите за **Столом {broj_stola}**. Додајте јела кликом на дугме испод.")

    cols = st.columns(3)
    col_idx = 0
    for item_name, info in menu_database.items():
        with cols[col_idx]:
            with st.container(border=True):
                st.image(prikazi_sliku(info["image"]), use_container_width=True)
                st.subheader(f"{item_name}")
                st.markdown(f"### {info['price']:.2f} RSD")
                
                if st.button("🛒 Поручи ово", key=f"btn_{item_name}"):
                    if item_name in baza[broj_stola]["porudzbina"]:
                        baza[broj_stola]["porudzbina"][item_name] += 1
                    else:
                        baza[broj_stola]["porudzbina"][item_name] = 1
                    sacuvaj_bazu(baza)
                    st.toast(f"Додато на ваш рачун: {item_name}!")
                    st.rerun()
        col_idx = (col_idx + 1) % 3

    st.divider()

    # -- AI КОНОБАР --
    st.subheader("🤖 Ваш лични AI Конобар")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "content": "Изволите, питајте ме нешто о менију!"}]

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_question = st.chat_input("Питај нешто...")
    if user_question and client:
        with st.chat_message("user"):
            st.markdown(user_question)
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        kontekst = f"Мени ресторана. Гост седи за столом {broj_stola}. Питање: {user_question}"
        
        with st.chat_message("assistant"):
            try:
                odgovor = client.models.generate_content(model='gemini-2.5-flash', contents=kontekst)
                st.markdown(odgovor.text)
                st.session_state.chat_history.append({"role": "assistant", "content": odgovor.text})
            except:
                st.error("AI тренутно није доступан.")

# ==========================================
# 3. ГЛАВНА ЛОГИКА (РУТИРАЊЕ ПОМОЋУ ЛИНКА)
# ==========================================
# Читамо шта пише у линку (URL-у)
parametri_linka = st.query_params

if "konobar" in parametri_linka:
    prikazi_konobarski_panel()
elif "sto" in parametri_linka:
    broj_stola = parametri_linka["sto"]
    prikazi_stranicu_za_gosta(broj_stola)
else:
    # Ако неко отвори само localhost:8501 без ичега
    st.title("Добродошли у Ресторан Корзо! 🍽️")
    st.write("Ово је почетна страница. У стварности, гости ће скенирати QR кôд који ће их директно одвести на њихов сто.")
    st.write("Одаберите режим испод да бисте тестирали систем:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📱 Симулирај Сто 1 (Гост)"):
            st.query_params["sto"] = "1"
            st.rerun()
    with col2:
        if st.button("📱 Симулирај Сто 5 (Гост)"):
            st.query_params["sto"] = "5"
            st.rerun()
    with col3:
        if st.button("👨‍🍳 Отвори Конобарски Панел"):
            st.query_params["konobar"] = "tajna"
            st.rerun()