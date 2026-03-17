import streamlit as st
import os
import time
from google import genai
from supabase import create_client, Client

# ==========================================
# 1. ПОДЕШАВАЊЕ КЉУЧЕВА (УНЕСИ СВОЈЕ!)
# ==========================================
# Овде залепи свој кључ са Google AI Studio (почиње са AIza...)
GEMINI_KEY = "УНЕСИ_СВОЈ_GEMINI_API_KEY"

# Твоји Супабејс подаци (већ убачени)
SUPABASE_URL = "https://mszsrorxwmkopoyvsbpw.supabase.co"
SUPABASE_KEY = "sb_publishable_mYfAEgWeQqUcjTIKqORx5w_A4hSqIc_"

# Иницијализација клијената
client_ai = genai.Client(api_key=GEMINI_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Корзо Паметни Систем", page_icon="🍽️", layout="wide")

# ==========================================
# 2. КОМПЛЕТНА БАЗА ПОДАТАКА (МЕНИ)
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
    "Sušeni sudžuk 100g": {"category": "Hladno predjelo", "price": 480.00, "calories": 400, "protein": 20, "description": "Domaći sušeni sudžuk", "image": "slike/suseni_sudzuk.jpg"},
    "Sir 100g": {"category": "Hladno predjelo", "price": 340.00, "calories": 350, "protein": 20, "description": "Domaћи beli sir", "image": "slike/sir.jpg"},
    "Mađarski juneći gulaš 450g": {"category": "Glavno jelo", "price": 1020.00, "calories": 600, "protein": 40, "description": "Bogati mađarski gulaš od junetine", "image": "slike/madjarski_gulas.jpg"},
    "Ćufte u pireu 350g": {"category": "Glavno jelo", "price": 660.00, "calories": 550, "protein": 30, "description": "Domaће ćufte u кремaстом пире кропмпиру", "image": "slike/cufte_u_pireu.jpg"},
    "Prebranac sa sudžukom 400g": {"category": "Glavno jelo", "price": 760.00, "calories": 650, "protein": 30, "description": "Zapečeni pasulj са sudžukom", "image": "slike/prebranac_sudzuk.jpg"},
    "Prebranac 300g": {"category": "Glavno jelo", "price": 590.00, "calories": 400, "protein": 18, "description": "Традиционални посни пребранац", "image": "slike/prebranac.jpg"},
    "Šopska salata 350g": {"category": "Salate", "price": 460.00, "calories": 200, "protein": 8, "description": "Paradajz, krastavac, luk, paprika, sir", "image": "slike/sopska_salata.jpg"},
    "Srpska salata 300g": {"category": "Salate", "price": 410.00, "calories": 100, "protein": 3, "description": "Paradajz, krastavac, luk, ljuta paprika", "image": "slike/srpska_salata.jpg"},
    "Kupus salata 300g": {"category": "Salate", "price": 330.00, "calories": 80, "protein": 2, "description": "Sveжа купус салата", "image": "slike/kupus_salata.jpg"},
    "Ljuta paprika u ulju 1 komad": {"category": "Salate", "price": 150.00, "calories": 50, "protein": 0, "description": "Печена љута паприка", "image": "slike/ljuta_paprika.jpg"},
    "Lepinja 1 komad": {"category": "Dodaci", "price": 120.00, "calories": 250, "protein": 7, "description": "Sveжа домаћа лепиња", "image": "slike/lepinja.jpg"},
    "Pomfrit 150g": {"category": "Dodaci", "price": 300.00, "calories": 450, "protein": 4, "description": "Hrskavi prženi krompirići", "image": "slike/pomfrit.jpg"},
    "Kugla kajmaka 1 komad": {"category": "Dodaci", "price": 180.00, "calories": 200, "protein": 2, "description": "Domaћи зрели кајмак", "image": "slike/kugla_kajmaka.jpg"}
}

# --- ФУНКЦИЈЕ ЗА БАЗУ ПОДАТАКА ---
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
    st.title("👨‍🍳 Контролни Панел - Корзо")
    st.info("Екран се аутоматски освежава сваких 10 секунди.")
    
    baza = ucitaj_iz_baze()
    if not baza:
        st.success("Нема активних поруџбина.")
    else:
        cols = st.columns(3)
        for i, (sto, podaci) in enumerate(baza.items()):
            with cols[i % 3]:
                with st.container(border=True):
                    if podaci.get('zove_konobara'): st.error(f"🔔 СТО {sto} ВАС ЗОВЕ!")
                    elif podaci.get('trazi_racun'): st.warning(f"💳 СТО {sto} ТРАЖИ РАЧУН ({podaci.get('nacin_placanja')})")
                    else: st.subheader(f"📍 Сто {sto}")
                    
                    st.write("---")
                    ukupno = 0
                    stavke = podaci.get("stavke", {})
                    for jelo, kolicina in stavke.items():
                        # ✅ ЗАШТИТА: Спречава KeyError ако је назив из базе застарео
                        if jelo in menu_database:
                            cena_stavke = menu_database[jelo]["price"] * kolicina
                            ukupno += cena_stavke
                            st.write(f"**{kolicina}x** {jelo}")
                        else:
                            st.write(f"⚠️ *{jelo}* (Није у менију)")
                    
                    st.metric("За наплату:", f"{ukupno:.2f} RSD")
                    if st.button(f"✅ Наплаћено / Очисти", key=f"del_{sto}"):
                        obrisi_sto(sto)
                        st.rerun()
    time.sleep(10)
    st.rerun()

# ==========================================
# 4. СТРАНИЦА ЗА ГОСТА
# ==========================================
def prikazi_gosta(sto):
    baza = ucitaj_iz_baze()
    moj_sto = baza.get(sto, {"stavke": {}, "zove_konobara": False, "trazi_racun": False, "nacin_placanja": ""})

    # САЈДБАР (КОРПА)
    st.sidebar.title(f"📍 Сто: {sto}")
    if st.sidebar.button("🙋‍♂️ ПОЗОВИ КОНОБАРА", type="primary", width='stretch'):
        moj_sto["zove_konobara"] = True
        snimi_u_bazu(sto, moj_sto)
        st.sidebar.success("Особље стиже!")

    st.sidebar.divider()
    st.sidebar.subheader("🛒 Ваша Поруџбина")
    ukupno = 0
    stavke_korpa = moj_sto.get("stavke", {})
    for jelo, qty in stavke_korpa.items():
        if jelo in menu_database:
            cena_stavke = menu_database[jelo]["price"] * qty
            ukupno += cena_stavke
            st.sidebar.write(f"**{qty}x** {jelo} ({cena_stavke:.2f} RSD)")
        else:
            st.sidebar.write(f"⚠️ *{jelo}* (Застарело)")
            
    st.sidebar.metric("Укупно:", f"{ukupno:.2f} RSD")

    if st.sidebar.button("🧾 Плати рачун (Кеш)", width='stretch'):
        moj_sto["trazi_racun"] = True
        moj_sto["nacin_placanja"] = "Кеш"
        snimi_u_bazu(sto, moj_sto)
        st.sidebar.info("Затражили сте рачун!")

    # ГЛАВНИ МЕНИ
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
                        st.image(prikazi_sliku(info["image"]), width='stretch')
                        st.subheader(ime)
                        st.write(f"Цена: **{info['price']:.2f} RSD**")
                        st.caption(info['description'])
                        with st.expander("Нутритивне вредности"):
                            st.write(f"🔥 {info['calories']} kcal | 🥩 {info['protein']}g протеина")
                        if st.button(f"🛒 Додај", key=f"add_{ime}"):
                            moj_sto["stavke"][ime] = moj_sto["stavke"].get(ime, 0) + 1
                            snimi_u_bazu(sto, moj_sto)
                            st.toast(f"Додато: {ime}")
                            st.rerun()

    # AI ЧАТБОТ
    st.divider()
    st.subheader("🤖 Питајте нашег AI асистента")
    upit = st.chat_input("Питајте нешто о храни...")
    if upit:
        with st.chat_message("user"): st.markdown(upit)
        context = f"Ти си конобар у ресторану Корзо. Мени: {list(menu_database.keys())}. Питање: {upit}"
        with st.chat_message("assistant"):
            try:
                # Користимо стабилнији 1.5-flash модел
                odgovor = client_ai.models.generate_content(model='gemini-1.5-flash', contents=context)
                st.markdown(odgovor.text)
            except Exception as e:
                # ПРИКАЗ ГРЕШКЕ ЗА ДЕБАГОВАЊЕ
                st.error(f"АИ Грешка: {e}")
                st.markdown("Извините, мој АИ мозак је тренутно заузет. Пробајте поново!")

# ==========================================
# 5. ГЛАВНИ РУТЕР
# ==========================================
params = st.query_params
if "konobar" in params: prikazi_konobara()
elif "sto" in params: prikazi_gosta(params["sto"])
else:
    st.title("Добродошли у Корзо! 🍽️")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📱 Отвори као Сто 1"):
            st.query_params["sto"] = "1"
            st.rerun()
    with col2:
        if st.button("👨‍🍳 Контролни Панел"):
            st.query_params["konobar"] = "true"
            st.rerun()
