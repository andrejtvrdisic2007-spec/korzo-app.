import streamlit as st
import os
import time
import google.generativeai as genai
from supabase import create_client, Client

# ==========================================
# 1. СИГУРНО ПОДЕШАВАЊЕ КЉУЧЕВА (Secrets)
# ==========================================
try:
    # Кључ се више не пише овде, већ у Settings -> Secrets на Streamlit-у
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("Нисте подесили 'GEMINI_API_KEY' у Secrets подешавањима!")
    st.stop()

SUPABASE_URL = "https://mszsrorxwmkopoyvsbpw.supabase.co"
SUPABASE_KEY = "sb_publishable_mYfAEgWeQqUcjTIKqORx5w_A4hSqIc_"

# Конфигурација сервиса
genai.configure(api_key=GEMINI_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Корзо Паметни Систем", page_icon="🍽️", layout="wide")

# ==========================================
# 2. КОМПЛЕТНА БАЗА ПОДАТАКА (СВИХ 21 СТАВКА)
# ==========================================
menu_database = {
    "Korzo doručak": {"category": "Doručak", "price": 630.00, "desc": "2 jaja, sudžuk, goveđa pršuta, ajvar, sir"},
    "Kajgana": {"category": "Doručak", "price": 350.00, "desc": "Domaća kajgana"},
    "Kačamak": {"category": "Doručak", "price": 300.00, "desc": "Tradicionalni domaći kačamak"},
    "Juneća čorba 350g": {"category": "Toplo predjelo", "price": 480.00, "desc": "Domaća topla juneća čorba"},
    "Juneće ćufte 350g": {"category": "Jela sa roštilja", "price": 990.00, "desc": "Sočne juneće ćufte sa roštilja"},
    "Juneći ćevapi 350g": {"category": "Jela sa roštilja", "price": 960.00, "desc": "Pravi domaći juneći ćevapi"},
    "Bagrem piletina 350g": {"category": "Jela sa roštilja", "price": 900.00, "desc": "Specijalitet kuće od piletine"},
    "Goveđa pršuta 100g": {"category": "Hladno predjelo", "price": 900.00, "desc": "Kvalitetna domaća goveđa pršuta"},
    "Sušeni sudžuk 100g": {"category": "Hladno predjelo", "price": 480.00, "desc": "Domaћи сушени суџук"},
    "Sir 100g": {"category": "Hladno predjelo", "price": 340.00, "desc": "Domaћи бели сир"},
    "Mađarski juneći gulaš 450g": {"category": "Glavno jelo", "price": 1020.00, "desc": "Bogati mađarski gulaš од јунетине"},
    "Ćufte u pireu 350g": {"category": "Glavno jelo", "price": 660.00, "desc": "Домаће ћуфте у кремастом пире кромпиру"},
    "Prebranac sa sudžukom 400g": {"category": "Glavno jelo", "price": 760.00, "desc": "Запечени пасуљ са суџуком"},
    "Prebranac 300g": {"category": "Glavno jelo", "price": 590.00, "desc": "Традиционални посни пребранац"},
    "Šopska salata 350g": {"category": "Salate", "price": 460.00, "desc": "Парадајз, краставац, лук, паприка, сир"},
    "Srpska salata 300g": {"category": "Salate", "price": 410.00, "desc": "Парадајз, краставац, лук, љута паприка"},
    "Kupus salata 300g": {"category": "Salate", "price": 330.00, "desc": "Свежа купус салата"},
    "Ljuta paprika u ulju 1 komad": {"category": "Salate", "price": 150.00, "desc": "Печена љута паприка"},
    "Lepinja 1 komad": {"category": "Dodaci", "price": 120.00, "desc": "Свежа домаћа лепиња"},
    "Pomfrit 150g": {"category": "Dodaci", "price": 300.00, "desc": "Хрскави пржени кромпирићи"},
    "Kugla kajmaka 1 komad": {"category": "Dodaci", "price": 180.00, "desc": "Домаћи зрели кајмак"}
}

# --- ПОМОЋНЕ ФУНКЦИЈЕ ---
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

# ==========================================
# 3. ПАНЕЛ ЗА КОНОБАРА
# ==========================================
def prikazi_konobara():
    st.title("👨‍🍳 Контролни Панел - Корзо")
    baza = ucitaj_iz_baze()
    if not baza: st.success("Нема активних поруџбина.")
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
                            ukupno += menu_database[jelo]["price"] * kolicina
                            st.write(f"**{kolicina}x** {jelo}")
                        else: st.write(f"⚠️ {jelo} (Застарело)")
                    st.metric("Укупно:", f"{ukupno:.2f} RSD")
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
    st.sidebar.metric("Ваш рачун:", f"{ukupno:.2f} RSD")

    st.title("🍽️ Корзо Паметни Мени")
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
                        st.subheader(ime)
                        st.write(f"Цена: **{info['price']:.2f} RSD**")
                        st.caption(info['desc'])
                        if st.button(f"🛒 Додај", key=f"add_{ime}"):
                            moj_sto["stavke"][ime] = moj_sto["stavke"].get(ime, 0) + 1
                            snimi_u_bazu(sto, moj_sto)
                            st.rerun()

    # --- АИ ЧАТБОТ ---
    st.divider()
    upit = st.chat_input("Питајте АИ конобара...")
    if upit:
        with st.chat_message("user"): st.markdown(upit)
        with st.chat_message("assistant"):
            try:
                # Користимо стабилну верзију модела
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(f"Ти си конобар у Корзоу. Мени: {list(menu_database.keys())}. Питање: {upit}")
                st.markdown(res.text)
            except Exception as e:
                st.error(f"АИ Грешка: {e}")

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
