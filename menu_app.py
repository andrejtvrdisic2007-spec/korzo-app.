import streamlit as st
import os
import time
import google.generativeai as genai
from supabase import create_client, Client

# ==========================================
# 1. СИГУРНО ПОДЕШАВАЊЕ (Secrets)
# ==========================================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ ГРЕШКА: GEMINI_API_KEY није подешен у Streamlit Secrets!")
    st.stop()

GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
SUPABASE_URL = "https://mszsrorxwmkopoyvsbpw.supabase.co"
SUPABASE_KEY = "sb_publishable_mYfAEgWeQqUcjTIKqORx5w_A4hSqIc_"

# Иницијализација
genai.configure(api_key=GEMINI_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Корзо Паметни Систем", page_icon="🍽️", layout="wide")

# ==========================================
# 2. КОМПЛЕТНА БАЗА (СВИХ 21 СТАВКА)
# ==========================================
menu_database = {
    "Korzo doručak": {"category": "Doručak", "price": 630.00, "calories": 750, "protein": 35, "desc": "2 jaja, sudžuk, goveđa pršuta, ajvar, sir", "image": "slike/korzo_dorucak.jpg"},
    "Kajgana": {"category": "Doručak", "price": 350.00, "calories": 300, "protein": 20, "desc": "Domaća kajgana", "image": "slike/kajgana.jpg"},
    "Kačamak": {"category": "Doručak", "price": 300.00, "calories": 400, "protein": 10, "desc": "Tradicionalni domaći kačamak", "image": "slike/kacamak.jpg"},
    "Juneća čorba 350g": {"category": "Toplo predjelo", "price": 480.00, "calories": 250, "protein": 15, "desc": "Domaća топла јунећа чорба", "image": "slike/juneca_corba.jpg"},
    "Juneće ćufte 350g": {"category": "Jela sa roštilja", "price": 990.00, "calories": 650, "protein": 45, "desc": "Sočne juneće ćufte са роштиља", "image": "slike/junece_cufte.jpg"},
    "Juneći ćevapi 350g": {"category": "Jela sa roštilja", "price": 960.00, "calories": 700, "protein": 50, "desc": "Pravi domaći juneći ćevapi", "image": "slike/juneci_cevapi.jpg"},
    "Bagrem piletina 350g": {"category": "Jela sa roštilja", "price": 900.00, "calories": 500, "protein": 60, "desc": "Specijalitet kuće од пилетине", "image": "slike/bagrem_piletina.jpg"},
    "Goveđa pršuta 100g": {"category": "Hladno predjelo", "price": 900.00, "calories": 250, "protein": 30, "desc": "Kvalitetna domaća goveđa pršuta", "image": "slike/govedja_prsuta.jpg"},
    "Sušeni sudžuk 100g": {"category": "Hladno predjelo", "price": 480.00, "calories": 400, "protein": 20, "desc": "Domaћи сушени суџук", "image": "slike/suseni_sudzuk.jpg"},
    "Sir 100g": {"category": "Hladno predjelo", "price": 340.00, "calories": 350, "protein": 20, "desc": "Domaћи бели сир", "image": "slike/sir.jpg"},
    "Mađarski juneći gulaš 450g": {"category": "Glavno jelo", "price": 1020.00, "calories": 600, "protein": 40, "desc": "Bogati mađarski gulaš од јунетине", "image": "slike/madjarski_gulas.jpg"},
    "Ćufte u pireu 350g": {"category": "Glavno jelo", "price": 660.00, "calories": 550, "protein": 30, "desc": "Domaће ћуфте у кремастом пиреу", "image": "slike/cufte_u_pireu.jpg"},
    "Prebranac sa sudžukom 400g": {"category": "Glavno jelo", "price": 760.00, "calories": 650, "protein": 30, "desc": "Zapečeni pasulj са суџуком", "image": "slike/prebranac_sudzuk.jpg"},
    "Prebranac 300g": {"category": "Glavno jelo", "price": 590.00, "calories": 400, "protein": 18, "desc": "Традиционални посни пребранац", "image": "slike/prebranac.jpg"},
    "Šopska salata 350g": {"category": "Salate", "price": 460.00, "calories": 200, "protein": 8, "desc": "Парадајз, краставац, лук, паприка, сир", "image": "slike/sopska_salata.jpg"},
    "Srpska salata 300g": {"category": "Salate", "price": 410.00, "calories": 100, "protein": 3, "desc": "Парадајз, краставац, лук, љута паприка", "image": "slike/srpska_salata.jpg"},
    "Kupus salata 300g": {"category": "Salate", "price": 330.00, "calories": 80, "protein": 2, "desc": "Свежа купус салата", "image": "slike/kupus_salata.jpg"},
    "Ljuta paprika u ulju 1 komad": {"category": "Salate", "price": 150.00, "calories": 50, "protein": 0, "desc": "Печена љута паприка", "image": "slike/ljuta_paprika.jpg"},
    "Lepinja 1 komad": {"category": "Dodaci", "price": 120.00, "calories": 250, "protein": 7, "desc": "Свежа домаћа лепиња", "image": "slike/lepinja.jpg"},
    "Pomfrit 150g": {"category": "Dodaci", "price": 300.00, "calories": 450, "protein": 4, "desc": "Хрскави пржени кромпирићи", "image": "slike/pomfrit.jpg"},
    "Kugla kajmaka 1 komad": {"category": "Dodaci", "price": 180.00, "calories": 200, "protein": 2, "desc": "Домаћи зрели кајмак", "image": "slike/kugla_kajmaka.jpg"}
}

# --- ФУНКЦИЈЕ ---
def ucitaj_iz_baze():
    try:
        res = supabase.table("porudzbine").select("*").execute()
        return {item['sto']: item for item in res.data}
    except: return {}

def snimi_u_bazu(sto, podaci):
    try:
        provera = supabase.table("porudzbine").select("*").eq("sto", sto).execute()
        nova_data = {"sto": sto, "stavke": podaci.get("stavke", {}), "zove_konobara": podaci.get("zove_konobara", False)}
        if len(provera.data) > 0:
            supabase.table("porudzbine").update(nova_data).eq("sto", sto).execute()
        else:
            supabase.table("porudzbine").insert(nova_data).execute()
    except Exception as e: st.error(f"Грешка са базом (Провери RLS): {e}")

def prikazi_sliku(putanja):
    return putanja if os.path.exists(putanja) else "https://via.placeholder.com/400x250.png?text=Korzo+Restoran"

# ==========================================
# 4. СТРАНИЦА ЗА ГОСТА
# ==========================================
params = st.query_params
if "sto" in params:
    sto = params["sto"]
    baza = ucitaj_iz_baze()
    moj_sto = baza.get(sto, {"stavke": {}, "zove_konobara": False})

    st.sidebar.title(f"📍 Сто: {sto}")
    if st.sidebar.button("🙋‍♂️ ПОЗОВИ КОНОБАРА", type="primary", width='stretch'):
        moj_sto["zove_konobara"] = True
        snimi_u_bazu(sto, moj_sto)
        st.sidebar.success("Конобар стиже!")

    st.title("🍽️ Корзо Паметни Мени")
    tabs = st.tabs(sorted(list(set([v["category"] for v in menu_database.values()]))))

    for i, tab in enumerate(tabs):
        with tab:
            kat = sorted(list(set([v["category"] for v in menu_database.values()])))[i]
            items = {k: v for k, v in menu_database.items() if v["category"] == kat}
            cols = st.columns(2)
            for j, (ime, info) in enumerate(items.items()):
                with cols[j % 2]:
                    with st.container(border=True):
                        st.image(prikazi_sliku(info["image"]), width='stretch')
                        st.subheader(ime)
                        st.write(f"**{info['price']:.2f} RSD**")
                        if st.button(f"🛒 Додај", key=f"add_{ime}"):
                            moj_sto["stavke"][ime] = moj_sto["stavke"].get(ime, 0) + 1
                            snimi_u_bazu(sto, moj_sto)
                            st.rerun()

    # --- АИ ЧАТБОТ ---
    st.divider()
    upit = st.chat_input("Питај АИ конобара...")
    if upit:
        with st.chat_message("user"): st.markdown(upit)
        with st.chat_message("assistant"):
            try:
                # Користимо стабилизовани назив за 2026. годину
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(f"Ти си конобар у Корзоу. Мени: {list(menu_database.keys())}. Питање: {upit}")
                st.markdown(res.text)
            except Exception as e:
                st.error(f"АИ Грешка (Провери Сецретс): {e}")

else:
    st.title("Добродошли у Корзо! 🍽️")
    if st.button("📱 Уђи као Сто 1"):
        st.query_params["sto"] = "1"
        st.rerun()
