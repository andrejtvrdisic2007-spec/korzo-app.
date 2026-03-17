import streamlit as st
import os
import time
import google.generativeai as genai
from supabase import create_client, Client

# ==========================================
# 1. ПОДЕШАВАЊЕ КЉУЧЕВА
# ==========================================
GEMINI_KEY = "AIzaSyBnOVsjyjJEnConG1mf7MNfHUNECktqUUY"
SUPABASE_URL = "https://mszsrorxwmkopoyvsbpw.supabase.co"
SUPABASE_KEY = "sb_publishable_mYfAEgWeQqUcjTIKqORx5w_A4hSqIc_"

# Повезивање са Супабејс
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ПОДЕШАВАЊЕ АИ (Флексибилно учитавање модела)
genai.configure(api_key=GEMINI_KEY)

def ucitaj_ai_model():
    # Пробамо неколико назива модела, један МОРА да ради
    for model_name in ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']:
        try:
            m = genai.GenerativeModel(model_name)
            return m
        except:
            continue
    return None

model_ai = ucitaj_ai_model()

st.set_page_config(page_title="Корзо Паметни Систем", page_icon="🍽️", layout="wide")

# ==========================================
# 2. КОМПЛЕТНА БАЗА ПОДАТАКА (СВИХ 21 СТАВКА)
# ==========================================
menu_database = {
    "Korzo doručak": {"category": "Doručak", "price": 630.00, "calories": 750, "protein": 35, "description": "2 jaja, sudžuk, goveđa pršuta, ajvar, sir", "image": "slike/korzo_dorucak.jpg"},
    "Kajgana": {"category": "Doručak", "price": 350.00, "calories": 300, "protein": 20, "description": "Domaća kajgana", "image": "slike/kajgana.jpg"},
    "Kačamak": {"category": "Doručak", "price": 300.00, "calories": 400, "protein": 10, "description": "Tradicionalni domaći kačamak", "image": "slike/kacamak.jpg"},
    "Juneća čorba 350g": {"category": "Toplo predjelo", "price": 480.00, "calories": 250, "protein": 15, "description": "Domaća topla juneća čorba", "image": "slike/juneca_corba.jpg"},
    "Juneće ćufte 350g": {"category": "Jela sa roštilja", "price": 990.00, "calories": 650, "protein": 45, "description": "Sočne juneće ćufte sa roštilja", "image": "slike/junece_cufte.jpg"},
    "Juneći ćevapi 350g": {"category": "Jela sa roštilja", "price": 960.00, "calories": 700, "protein": 50, "description": "Pravi domaći juneći ćevapi", "image": "slike/juneci_cevapi.jpg"},
    "Bagrem piletina 350g": {"category": "Jela sa roštilja", "price": 900.00, "calories": 500, "protein": 60, "description": "Specijalitet kuće od piletine", "image": "slike/bagrem_piletina.jpg"},
    "Goveđa pršuta 100g": {"category": "Hladno predjelo", "price": 900.00, "calories": 250, "protein": 30, "description": "Kvalitetna domaća goveđa pršuta", "image": "slike/govedja_prsuta.jpg"},
    "Sušeni sudžuk 100g": {"category": "Hladno predjelo", "price": 480.00, "calories": 400, "protein": 20, "description": "Domaћи сушени суџук", "image": "slike/suseni_sudzuk.jpg"},
    "Sir 100g": {"category": "Hladno predjelo", "price": 340.00, "calories": 350, "protein": 20, "description": "Domaћи бели сир", "image": "slike/sir.jpg"},
    "Mađarski juneći gulaš 450g": {"category": "Glavno jelo", "price": 1020.00, "calories": 600, "protein": 40, "description": "Bogati mađarski gulaš од јунетине", "image": "slike/madjarski_gulas.jpg"},
    "Ćufte u pireu 350g": {"category": "Glavno jelo", "price": 660.00, "calories": 550, "protein": 30, "description": "Домаће ћуфте у кремастом пире кромпиру", "image": "slike/cufte_u_pireu.jpg"},
    "Prebranac sa sudžukom 400g": {"category": "Glavno jelo", "price": 760.00, "calories": 650, "protein": 30, "description": "Запечени пасуљ са суџуком", "image": "slike/prebranac_sudzuk.jpg"},
    "Prebranac 300g": {"category": "Glavno jelo", "price": 590.00, "calories": 400, "protein": 18, "description": "Традиционални посни пребранац", "image": "slike/prebranac.jpg"},
    "Šopska salata 350g": {"category": "Salate", "price": 460.00, "calories": 200, "protein": 8, "description": "Парадајз, краставац, лук, паприка, сир", "image": "slike/sopska_salata.jpg"},
    "Srpska salata 300g": {"category": "Salate", "price": 410.00, "calories": 100, "protein": 3, "description": "Парадајз, краставац, лук, љута паприка", "image": "slike/srpska_salata.jpg"},
    "Kupus salata 300g": {"category": "Salate", "price": 330.00, "calories": 80, "protein": 2, "description": "Свежа купус салата", "image": "slike/kupus_salata.jpg"},
    "Ljuta paprika u ulju 1 komad": {"category": "Salate", "price": 150.00, "calories": 50, "protein": 0, "description": "Печена љута паприка", "image": "slike/ljuta_paprika.jpg"},
    "Lepinja 1 komad": {"category": "Dodaci", "price": 120.00, "calories": 250, "protein": 7, "description": "Свежа домаћа лепиња", "image": "slike/lepinja.jpg"},
    "Pomfrit 150g": {"category": "Dodaci", "price": 300.00, "calories": 450, "protein": 4, "description": "Хрскави пржени кромпирићи", "image": "slike/pomfrit.jpg"},
    "Kugla kajmaka 1 komad": {"category": "Dodaci", "price": 180.00, "calories": 200, "protein": 2, "description": "Домаћи зрели кајмак", "image": "slike/kugla_kajmaka.jpg"}
}

# --- ФУНКЦИЈЕ ЗА БАЗУ ---
def ucitaj_iz_baze():
    try:
        res = supabase.table("porudzbine").select("*").execute()
        return {item['sto']: item for item in res.data}
    except: return {}

def snimi_u_bazu(sto, podaci):
    try:
        provera = supabase.table("porudzbine").select("*").eq("sto", sto).execute()
        nova_data = {"sto": sto, "stavke": podaci.get("stavke", {}), "zove_konobara": podaci.get("zove_konobara", False), "trazi_racun": podaci.get("trazi_racun", False), "nacin_placanja": podaci.get("nacin_placanja", "")}
        if len(provera.data) > 0:
            supabase.table("porudzbine").update(nova_data).eq("sto", sto).execute()
        else:
            supabase.table("porudzbine").insert(nova_data).execute()
    except Exception as e: st.error(f"Грешка са базом: {e}")

def obrisi_sto(sto):
    supabase.table("porudzbine").delete().eq("sto", sto).execute()

def prikazi_sliku(putanja):
    return putanja if os.path.exists(putanja) else "https://via.placeholder.com/400x250.png?text=Korzo+Restoran"

# ==========================================
# 3. ПАНЕЛ ЗА КОНОБАРА
# ==========================================
def prikazi_konobara():
    st.title("👨‍🍳 Контролни Панел - Корзо")
    st.info("Аутоматско освежавање: 10с.")
    baza = ucitaj_iz_baze()
    if not baza: st.success("Тренутно нема поруџбина.")
    else:
        cols = st.columns(3)
        for i, (sto, podaci) in enumerate(baza.items()):
            with cols[i % 3]:
                with st.container(border=True):
                    if podaci.get('zove_konobara'): st.error(f"🔔 СТО {sto} ЗОВЕ!")
                    elif podaci.get('trazi_racun'): st.warning(f"💳 СТО {sto} РАЧУН")
                    else: st.subheader(f"📍 Сто {sto}")
                    ukupno = 0
                    for jelo, kolicina in podaci.get("stavke", {}).items():
                        if jelo in menu_database:
                            cena = menu_database[jelo]["price"] * kolicina
                            ukupno += cena
                            st.write(f"**{kolicina}x** {jelo}")
                    st.metric("За наплату:", f"{ukupno:.2f} RSD")
                    if st.button("✅ Готово", key=f"del_{sto}"):
                        obrisi_sto(sto)
                        st.rerun()
    time.sleep(10)
    st.rerun()

# ==========================================
# 4. СТРАНИЦА ЗА ГОСТА
# ==========================================
def prikazi_gosta(sto):
    baza = ucitaj_iz_baze()
    moj_sto = baza.get(sto, {"stavke": {}, "zove_konobara": False, "trazi_racun": False})

    st.sidebar.title(f"📍 Сто: {sto}")
    if st.sidebar.button("🙋‍♂️ ПОЗОВИ КОНОБАРА", type="primary", width='stretch'):
        moj_sto["zove_konobara"] = True
        snimi_u_bazu(sto, moj_sto)
        st.sidebar.success("Конобар стиже!")

    st.sidebar.divider()
    ukupno = 0
    for jelo, qty in moj_sto.get("stavke", {}).items():
        if jelo in menu_database:
            ukupno += menu_database[jelo]["price"] * qty
            st.sidebar.write(f"**{qty}x** {jelo}")
    st.sidebar.metric("Укупно:", f"{ukupno:.2f} RSD")

    st.title("🍽️ Корзо Мени")
    kategorije = sorted(list(set([info["category"] for info in menu_database.values()])))
    tabs = st.tabs(kategorije)

    for i, tab in enumerate(tabs):
        with tab:
            kat = kategorije[i]
            jela_kat = {k: v for k, v in menu_database.items() if v["category"] == kat}
            cols = st.columns(2)
            for j, (ime, info) in enumerate(jela_kat.items()):
                with cols[j % 2]:
                    with st.container(border=True):
                        st.image(prikazi_sliku(info["image"]), width='stretch')
                        st.subheader(ime)
                        st.write(f"Цена: **{info['price']:.2f} RSD**")
                        st.caption(info['description'])
                        if st.button(f"🛒 Додај", key=f"add_{ime}"):
                            moj_sto["stavke"][ime] = moj_sto["stavke"].get(ime, 0) + 1
                            snimi_u_bazu(sto, moj_sto)
                            st.rerun()

    # АИ ЧАТБОТ
    st.divider()
    st.subheader("🤖 Питајте AI конобара")
    upit = st.chat_input("Питајте нешто...")
    if upit:
        with st.chat_message("user"): st.markdown(upit)
        with st.chat_message("assistant"):
            if model_ai:
                try:
                    odgovor = model_ai.generate_content(f"Ти си конобар у Корзоу. Мени: {list(menu_database.keys())}. Питање: {upit}")
                    st.markdown(odgovor.text)
                except Exception as e:
                    st.error(f"Грешка: {e}")
            else:
                st.error("АИ модел није могао бити учитан.")

# ==========================================
# 5. ГЛАВНИ РУТЕР
# ==========================================
params = st.query_params
if "konobar" in params: prikazi_konobara()
elif "sto" in params: prikazi_gosta(params["sto"])
else:
    st.title("Добродошли у Корзо! 🍽️")
    if st.button("📱 Уђи као Сто 1"):
        st.query_params["sto"] = "1"
        st.rerun()
