import streamlit as st
import os
import time
from google import genai
from supabase import create_client, Client

# ==========================================
# 1. ПОДЕШАВАЊЕ КЉУЧЕВА
# ==========================================
# Унеси свој Гугл АИ кључ овде:
GEMINI_KEY = "AIzaSyBnOVsjyjJEnConG1mf7MNfHUNECktqUUY"

# Твоји Супабејс подаци (већ убачени)
SUPABASE_URL = "https://mszsrorxwmkopoyvsbpw.supabase.co"
SUPABASE_KEY = "sb_publishable_mYfAEgWeQqUcjTIKqORx5w_A4hSqIc_"

# Повезивање
client_ai = genai.Client(api_key=GEMINI_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Корзо Паметни Систем", page_icon="🍽️", layout="wide")

# ==========================================
# 2. БАЗА ПОДАТАКА (МЕНИ)
# ==========================================
menu_database = {
    "Korzo doručak": {"price": 630.00, "image": "slike/korzo_dorucak.jpg", "desc": "2 jaja, sudžuk, pršuta, sir"},
    "Kajgana": {"price": 350.00, "image": "slike/kajgana.jpg", "desc": "Domaća kajgana"},
    "Juneći ćevapi 350g": {"price": 960.00, "image": "slike/juneci_cevapi.jpg", "desc": "Pravi domaći ćevapi"},
    "Šopska salata": {"price": 460.00, "image": "slike/sopska_salata.jpg", "desc": "Sveжа салата са сиром"},
    "Lepinja": {"price": 120.00, "image": "slike/lepinja.jpg", "desc": "Sveža domaća lepinja"}
}

# --- ФУНКЦИЈЕ ЗА БАЗУ ---
def ucitaj_iz_baze():
    res = supabase.table("porudzbine").select("*").execute()
    return {item['sto']: item for item in res.data}

def snimi_u_bazu(sto, podaci):
    provera = supabase.table("porudzbine").select("*").eq("sto", sto).execute()
    nova_data = {
        "sto": sto,
        "stavke": podaci.get("stavke", {}),
        "zove_konobara": podaci.get("zove_konobara", False),
        "trazi_racun": podaci.get("trazi_racun", False),
        "nacin_placanja": podaci.get("nacin_placanja", "")
    }
    if len(provera.data) > 0:
        supabase.table("porudzbine").update(nova_data).eq("sto", sto).execute()
    else:
        supabase.table("porudzbine").insert(nova_data).execute()

def obrisi_sto(sto):
    supabase.table("porudzbine").delete().eq("sto", sto).execute()

def prikazi_sliku(putanja):
    return putanja if os.path.exists(putanja) else "https://via.placeholder.com/400x250.png?text=Korzo+Restoran"

# ==========================================
# 3. ПАНЕЛ ЗА КОНОБАРА
# ==========================================
def prikazi_konobara():
    st.title("👨‍🍳 Контролни Панел - Ресторан Корзо")
    st.info("Овај панел се аутоматски освежава сваких 10 секунди.")
    
    baza = ucitaj_iz_baze()
    
    if not baza:
        st.success("Нема активних поруџбина. Ресторан је спреман за нове госте!")
    else:
        cols = st.columns(3)
        for i, (sto, podaci) in enumerate(baza.items()):
            with cols[i % 3]:
                with st.container(border=True):
                    # Обавештења
                    if podaci['zove_konobara']:
                        st.error(f"🔔 СТО {sto} ВАС ЗОВЕ!")
                    elif podaci['trazi_racun']:
                        st.warning(f"💳 СТО {sto} ТРАЖИ РАЧУН ({podaci['nacin_placanja']})")
                    else:
                        st.subheader(f"📍 Сто {sto}")
                    
                    st.write("---")
                    ukupno = 0
                    for jelo, kolicina in podaci.get("stavke", {}).items():
                        cena = menu_database[jelo]["price"] * kolicina
                        ukupno += cena
                        st.write(f"**{kolicina}x** {jelo}")
                    
                    st.metric("За наплату:", f"{ukupno:.2f} RSD")
                    
                    if st.button(f"✅ Готово / Наплаћено", key=f"del_{sto}"):
                        obrisi_sto(sto)
                        st.rerun()

    # Аутоматски рефреш
    time.sleep(10)
    st.rerun()

# ==========================================
# 4. СТРАНИЦА ЗА ГОСТА
# ==========================================
def prikazi_gosta(broj_stola):
    baza = ucitaj_iz_baze()
    moj_sto = baza.get(broj_stola, {"stavke": {}, "zove_konobara": False, "trazi_racun": False, "nacin_placanja": ""})

    st.sidebar.title(f"📍 Сто: {broj_stola}")
    
    # Позив конобара
    if st.sidebar.button("🙋‍♂️ Позови конобара", use_container_width=True):
        moj_sto["zove_konobara"] = True
        snimi_u_bazu(broj_stola, moj_sto)
        st.sidebar.success("Особље стиже!")

    # Приказ рачуна
    st.sidebar.markdown("---")
    st.sidebar.subheader("🛒 Ваш рачун")
    ukupno = 0
    for jelo, qty in moj_sto["stavke"].items():
        cena = menu_database[jelo]["price"] * qty
        ukupno += cena
        st.sidebar.write(f"{qty}x {jelo} - {cena} RSD")
    st.sidebar.metric("Укупно:", f"{ukupno:.2f} RSD")

    if st.sidebar.button("🧾 Плати рачун (Кеш)", type="primary"):
        moj_sto["trazi_racun"] = True
        moj_sto["nacin_placanja"] = "Кеш"
        snimi_u_bazu(broj_stola, moj_sto)
        st.sidebar.info("Затражили сте рачун!")

    # Мени
    st.title("🍽️ Корзо Паметни Мени")
    cols = st.columns(2)
    for i, (ime, info) in enumerate(menu_database.items()):
        with cols[i % 2]:
            with st.container(border=True):
                st.image(prikazi_sliku(info["image"]), use_container_width=True)
                st.subheader(ime)
                st.write(f"Цена: **{info['price']} RSD**")
                if st.button(f"🛒 Додај", key=f"add_{ime}"):
                    moj_sto["stavke"][ime] = moj_sto["stavke"].get(ime, 0) + 1
                    snimi_u_bazu(broj_stola, moj_sto)
                    st.toast(f"Додато: {ime}")
                    st.rerun()

    # AI Четбот
    st.divider()
    st.subheader("🤖 Питајте нашег AI конобара")
    upit = st.chat_input("Питајте нешто о храни...")
    if upit:
        with st.chat_message("user"): st.markdown(upit)
        kontekst = f"Мени ресторана Корзо. Гост је за столом {broj_stola}. Питање: {upit}"
        with st.chat_message("assistant"):
            odgovor = client_ai.models.generate_content(model='gemini-2.5-flash', contents=kontekst)
            st.markdown(odgovor.text)

# ==========================================
# 5. ГЛАВНИ РУТЕР
# ==========================================
parametri = st.query_params
if "konobar" in parametri:
    prikazi_konobara()
elif "sto" in parametri:
    prikazi_gosta(parametri["sto"])
else:
    st.title("Добродошли у Корзо! 🍽️")
    st.write("Изаберите режим за тестирање:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📱 Отвори као Сто 1"):
            st.query_params["sto"] = "1"
            st.rerun()
    with col2:
        if st.button("👨‍🍳 Отвори Конобарски Панел"):
            st.query_params["konobar"] = "true"
            st.rerun()
