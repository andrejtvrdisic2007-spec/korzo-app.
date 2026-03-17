import streamlit as st
import os
import time
import google.generativeai as genai
from supabase import create_client, Client

# ==========================================
# 1. SIGURNO PODEŠAVANJE (Streamlit Secrets)
# ==========================================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ KLJUČ NIJE PRONAĐEN! Moraš ga uneti u Streamlit Cloud Settings -> Secrets.")
    st.stop()

GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
SUPABASE_URL = "https://mszsrorxwmkopoyvsbpw.supabase.co"
SUPABASE_KEY = "sb_publishable_mYfAEgWeQqUcjTIKqORx5w_A4hSqIc_"

# Inicijalizacija
genai.configure(api_key=GEMINI_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Korzo Pametni Meni", page_icon="🍽️", layout="wide")

# ==========================================
# 2. KOMPLETNA BAZA (SVIH 21 JELO)
# ==========================================
menu_database = {
    "Korzo doručak": {"category": "Doručak", "price": 630.00, "calories": 750, "protein": 35, "desc": "2 jaja, sudžuk, goveđa pršuta, ajvar, sir", "image": "slike/korzo_dorucak.jpg"},
    "Kajgana": {"category": "Doručak", "price": 350.00, "calories": 300, "protein": 20, "desc": "Domaća kajgana", "image": "slike/kajgana.jpg"},
    "Kačamak": {"category": "Doručak", "price": 300.00, "calories": 400, "protein": 10, "desc": "Tradicionalni domaći kačamak", "image": "slike/kacamak.jpg"},
    "Juneća čorba 350g": {"category": "Toplo predjelo", "price": 480.00, "calories": 250, "protein": 15, "desc": "Domaća topla juneća čorba", "image": "slike/juneca_corba.jpg"},
    "Juneće ćufte 350g": {"category": "Jela sa roštilja", "price": 990.00, "calories": 650, "protein": 45, "desc": "Sočne juneće ćufte sa roštilja", "image": "slike/junece_cufte.jpg"},
    "Juneći ćevapi 350g": {"category": "Jela sa roštilja", "price": 960.00, "calories": 700, "protein": 50, "desc": "Pravi domaći juneći ćevapi", "image": "slike/juneci_cevapi.jpg"},
    "Bagrem piletina 350g": {"category": "Jela sa roštilja", "price": 900.00, "calories": 500, "protein": 60, "desc": "Specijalitet kuće od piletine", "image": "slike/bagrem_piletina.jpg"},
    "Goveđa pršuta 100g": {"category": "Hladno predjelo", "price": 900.00, "calories": 250, "protein": 30, "desc": "Kvalitetna domaća goveđa pršuta", "image": "slike/govedja_prsuta.jpg"},
    "Sušeni sudžuk 100g": {"category": "Hladno predjelo", "price": 480.00, "calories": 400, "protein": 20, "desc": "Domaći sušeni sudžuk", "image": "slike/suseni_sudzuk.jpg"},
    "Sir 100g": {"category": "Hladno predjelo", "price": 340.00, "calories": 350, "protein": 20, "desc": "Domaći beli sir", "image": "slike/sir.jpg"},
    "Mađarski juneći gulaš 450g": {"category": "Glavno jelo", "price": 1020.00, "calories": 600, "protein": 40, "desc": "Bogati mađarski gulaš od junetine", "image": "slike/madjarski_gulas.jpg"},
    "Ćufte u pireu 350g": {"category": "Glavno jelo", "price": 660.00, "calories": 550, "protein": 30, "desc": "Domaće ćufte u kremastom pireu", "image": "slike/cufte_u_pireu.jpg"},
    "Prebranac sa sudžukom 400g": {"category": "Glavno jelo", "price": 760.00, "calories": 650, "protein": 30, "desc": "Zapečeni pasulj sa sudžukom", "image": "slike/prebranac_sudzuk.jpg"},
    "Prebranac 300g": {"category": "Glavno jelo", "price": 590.00, "calories": 400, "protein": 18, "desc": "Tradicionalni posni prebranac", "image": "slike/prebranac.jpg"},
    "Šopska salata 350g": {"category": "Salate", "price": 460.00, "calories": 200, "protein": 8, "desc": "Paradajz, krastavac, luk, paprika, sir", "image": "slike/sopska_salata.jpg"},
    "Srpska salata 300g": {"category": "Salate", "price": 410.00, "calories": 100, "protein": 3, "desc": "Paradajz, krastavac, luk, ljuta paprika", "image": "slike/srpska_salata.jpg"},
    "Kupus salata 300g": {"category": "Salate", "price": 330.00, "calories": 80, "protein": 2, "desc": "Sveža kupus salata", "image": "slike/kupus_salata.jpg"},
    "Ljuta paprika u ulju 1 komad": {"category": "Salate", "price": 150.00, "calories": 50, "protein": 0, "desc": "Pečena ljuta paprika", "image": "slike/ljuta_paprika.jpg"},
    "Lepinja 1 komad": {"category": "Dodaci", "price": 120.00, "calories": 250, "protein": 7, "desc": "Sveža domaća lepinja", "image": "slike/lepinja.jpg"},
    "Pomfrit 150g": {"category": "Dodaci", "price": 300.00, "calories": 450, "protein": 4, "desc": "Hrskavi prženi krompirići", "image": "slike/pomfrit.jpg"},
    "Kugla kajmaka 1 komad": {"category": "Dodaci", "price": 180.00, "calories": 200, "protein": 2, "desc": "Domaći zreli kajmak", "image": "slike/kugla_kajmaka.jpg"}
}

# --- FUNKCIJE ---
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
    except Exception as e: st.error(f"Baza greška: {e}")

def obrisi_sto(sto):
    supabase.table("porudzbine").delete().eq("sto", sto).execute()

def prikazi_sliku(putanja):
    return putanja if os.path.exists(putanja) else "https://via.placeholder.com/400x250.png?text=Korzo+Slika"

# ==========================================
# 3. PANEL ZA KONOBARA
# ==========================================
def prikazi_konobara():
    st.title("👨‍🍳 Kontrolni Panel - Korzo")
    baza = ucitaj_iz_baze()
    if not baza: st.success("Nema porudžbina.")
    else:
        cols = st.columns(3)
        for i, (sto, podaci) in enumerate(baza.items()):
            with cols[i % 3]:
                with st.container(border=True):
                    if podaci.get('zove_konobara'): st.error(f"🔔 STO {sto} ZOVE!")
                    elif podaci.get('trazi_racun'): st.warning(f"💳 STO {sto} RAČUN")
                    else: st.subheader(f"📍 Sto {sto}")
                    ukupno = 0
                    for jelo, kolicina in podaci.get("stavke", {}).items():
                        if jelo in menu_database:
                            ukupno += menu_database[jelo]["price"] * kolicina
                            st.write(f"**{kolicina}x** {jelo}")
                    st.metric("Ukupno:", f"{ukupno:.2f} RSD")
                    if st.button("✅ Završi", key=f"del_{sto}"):
                        obrisi_sto(sto)
                        st.rerun()
    time.sleep(10)
    st.rerun()

# ==========================================
# 4. STRANICA ZA GOSTA
# ==========================================
def prikazi_gosta(sto):
    baza = ucitaj_iz_baze()
    moj_sto = baza.get(sto, {"stavke": {}, "zove_konobara": False, "trazi_racun": False})

    st.sidebar.title(f"📍 Sto: {sto}")
    if st.sidebar.button("🙋‍♂️ POZOVI KONOBARA", type="primary", use_container_width=True):
        moj_sto["zove_konobara"] = True
        snimi_u_bazu(sto, moj_sto)
        st.sidebar.success("Stižemo!")

    st.sidebar.divider()
    ukupno = 0
    for jelo, qty in moj_sto.get("stavke", {}).items():
        if jelo in menu_database:
            ukupno += menu_database[jelo]["price"] * qty
            st.sidebar.write(f"**{qty}x** {jelo}")
    st.sidebar.metric("Račun:", f"{ukupno:.2f} RSD")

    st.title("🍽️ Korzo Pametni Meni")
    kategorije = sorted(list(set([info["category"] for info in menu_database.values()])))
    tabs = st.tabs(kategorije)

    for i, tab in enumerate(tabs):
        with tab:
            items = {k: v for k, v in menu_database.items() if v["category"] == kategorije[i]}
            cols = st.columns(2)
            for j, (ime, info) in enumerate(items.items()):
                with cols[j % 2]:
                    with st.container(border=True):
                        st.image(prikazi_sliku(info["image"]), use_container_width=True)
                        st.subheader(ime)
                        st.write(f"**{info['price']:.2f} RSD**")
                        st.caption(info['desc'])
                        with st.expander("Nutricije"):
                            st.write(f"🔥 {info['calories']} kcal | 🥩 {info['protein']}g protein")
                        if st.button(f"🛒 Dodaj", key=f"add_{ime}"):
                            moj_sto["stavke"][ime] = moj_sto["stavke"].get(ime, 0) + 1
                            snimi_u_bazu(sto, moj_sto)
                            st.rerun()

    # AI CHAT
    st.divider()
    upit = st.chat_input("Pitaj AI konobara...")
    if upit:
        with st.chat_message("user"): st.markdown(upit)
        with st.chat_message("assistant"):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(f"Ti si konobar u Korzo Kragujevac. Meni: {list(menu_database.keys())}. Odgovori kratko: {upit}")
                st.markdown(res.text)
            except Exception as e: st.error(f"AI Greška: {e}")

# ==========================================
# 5. RUTER
# ==========================================
p = st.query_params
if "konobar" in p: prikazi_konobara()
elif "sto" in p: prikazi_gosta(p["sto"])
else:
    st.title("Dobrodošli u Korzo! 🍽️")
    if st.button("📱 Sto 1"):
        st.query_params["sto"] = "1"
        st.rerun()
