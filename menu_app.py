import streamlit as st
import os
import time
import google.generativeai as genai
from supabase import create_client, Client

# ==========================================
# 1. СИГУРНО ПОДЕШАВАЊЕ (Secrets)
# ==========================================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ Кључ није подешен у Streamlit Secrets!")
    st.stop()

GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
SUPABASE_URL = "https://mszsrorxwmkopoyvsbpw.supabase.co"
SUPABASE_KEY = "sb_publishable_mYfAEgWeQqUcjTIKqORx5w_A4hSqIc_"

# Конфигурација Gemini 3 Flash модела
genai.configure(api_key=GEMINI_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Корзо Паметни Мени", page_icon="🍽️", layout="wide")

# ==========================================
# 2. БАЗА ПОДАТАКА (СВИХ 21 ЈЕЛО)
# ==========================================
menu_database = {
    "Korzo doručak": {"category": "Doručak", "price": 630.0, "desc": "2 jaja, sudžuk, pršuta, ajvar, sir", "image": "slike/korzo_dorucak.jpg"},
    "Kajgana": {"category": "Doručak", "price": 350.0, "desc": "Domaća kajgana", "image": "slike/kajgana.jpg"},
    "Kačamak": {"category": "Doručak", "price": 300.0, "desc": "Tradicionalni domaći kačamak", "image": "slike/kacamak.jpg"},
    "Juneća čorba 350g": {"category": "Toplo predjelo", "price": 480.0, "desc": "Domaća topla juneća čorba", "image": "slike/juneca_corba.jpg"},
    "Juneće ćufte 350g": {"category": "Jela sa roštilja", "price": 990.0, "desc": "Sočne juneće ćufte", "image": "slike/junece_cufte.jpg"},
    "Juneći ćevapi 350g": {"category": "Jela sa roštilja", "price": 960.0, "desc": "Pravi domaći ćevapi", "image": "slike/juneci_cevapi.jpg"},
    "Bagrem piletina 350g": {"category": "Jela sa roštilja", "price": 900.0, "desc": "Specijalitet kuće", "image": "slike/bagrem_piletina.jpg"},
    "Goveđa pršuta 100g": {"category": "Hladno predjelo", "price": 900.0, "desc": "Domaća goveđa pršuta", "image": "slike/govedja_prsuta.jpg"},
    "Sušeni sudžuk 100g": {"category": "Hladno predjelo", "price": 480.0, "desc": "Domaći sušeni sudžuk", "image": "slike/suseni_sudzuk.jpg"},
    "Sir 100g": {"category": "Hladno predjelo", "price": 340.0, "desc": "Domaћи бели сир", "image": "slike/sir.jpg"},
    "Mađarski juneći gulaš 450g": {"category": "Glavno jelo", "price": 1020.0, "desc": "Bogati gulaš", "image": "slike/madjarski_gulas.jpg"},
    "Ćufte u pireu 350g": {"category": "Glavno jelo", "price": 660.0, "desc": "Ćufte и пире", "image": "slike/cufte_u_pireu.jpg"},
    "Prebranac sa sudžukom 400g": {"category": "Glavno jelo", "price": 760.0, "desc": "Pasulj sa sudžukom", "image": "slike/prebranac_sudzuk.jpg"},
    "Prebranac 300g": {"category": "Glavno jelo", "price": 590.0, "desc": "Posni prebranac", "image": "slike/prebranac.jpg"},
    "Šopska salata 350g": {"category": "Salate", "price": 460.0, "desc": "Sveža šopska", "image": "slike/sopska_salata.jpg"},
    "Srpska salata 300g": {"category": "Salate", "price": 410.0, "desc": "Paradajz, krastavac, luk", "image": "slike/srpska_salata.jpg"},
    "Kupus salata 300g": {"category": "Salate", "price": 330.0, "desc": "Svež kupus", "image": "slike/kupus_salata.jpg"},
    "Ljuta paprika u ulju 1 komad": {"category": "Salate", "price": 150.0, "desc": "Ljuta paprika", "image": "slike/ljuta_paprika.jpg"},
    "Lepinja 1 komad": {"category": "Dodaci", "price": 120.0, "desc": "Domaћа лепиња", "image": "slike/lepinja.jpg"},
    "Pomfrit 150g": {"category": "Dodaci", "price": 300.0, "desc": "Pomfrit", "image": "slike/pomfrit.jpg"},
    "Kugla kajmaka 1 komad": {"category": "Dodaci", "price": 180.0, "desc": "Domaći kajmak", "image": "slike/kugla_kajmaka.jpg"}
}

# --- ПОМОЋНЕ ФУНКЦИЈЕ ---
def ucitaj_iz_baze():
    try:
        res = supabase.table("porudzbine").select("*").execute()
        return {item['sto']: item for item in res.data}
    except: return {}

def snimi_u_bazu(sto, podaci):
    provera = supabase.table("porudzbine").select("*").eq("sto", sto).execute()
    nova_data = {"sto": sto, "stavke": podaci.get("stavke", {}), "zove_konobara": podaci.get("zove_konobara", False)}
    if len(provera.data) > 0: supabase.table("porudzbine").update(nova_data).eq("sto", sto).execute()
    else: supabase.table("porudzbine").insert(nova_data).execute()

def prikazi_sliku(putanja):
    return putanja if os.path.exists(putanja) else "https://via.placeholder.com/400x250.png?text=Korzo"

# ==========================================
# 3. ПРИКАЗ ГЛАВНОГ МЕНИЈА
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
                        st.subheader(ime)
                        st.write(f"**{info['price']} RSD**")
                        if st.button(f"🛒 Додај", key=f"add_{ime}"):
                            moj_sto["stavke"][ime] = moj_sto["stavke"].get(ime, 0) + 1
                            snimi_u_bazu(sto, moj_sto)
                            st.rerun()

    # --- АИ ЧЕТБОТ СА GEMINI 3 FLASH ---
    st.divider()
    upit = st.chat_input("Питај АИ конобара...")
    if upit:
        with st.chat_message("user"): st.markdown(upit)
        with st.chat_message("assistant"):
            try:
                # КОРИСТИМО GEMINI-3-FLASH МОДЕЛ
                model = genai.GenerativeModel('gemini-3-flash')
                res = model.generate_content(f"Ti si konobar u restoranu Korzo. Meni: {list(menu_database.keys())}. Pitanje: {upit}")
                st.markdown(res.text)
            except Exception as e:
                st.error(f"АИ Грешка: {e}")
else:
    st.title("Добродошли у Корзо! 🍽️")
    if st.button("📱 Уђи као Сто 1"):
        st.query_params["sto"] = "1"
        st.rerun()
