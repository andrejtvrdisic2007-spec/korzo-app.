import streamlit as st
import os
import time
from google import genai
from supabase import create_client, Client

# ==========================================
# 1. ПОДЕШАВАЊЕ КЉУЧЕВА И КОНЕКЦИЈЕ
# ==========================================
# ПАЖЊА: Овде унеси свој Gemini кључ са Google AI Studio
GEMINI_KEY = "AIzaSyBnOVsjyjJEnConG1mf7MNfHUNECktqUUY"

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
    "Korzo doručak": {"category": "Doručak", "price": 630.00, "calories": 750, "protein": 35, "carbs": 20, "fats": 55, "allergens": "Jaja, Mleko", "dietary_tags": [], "description": "2 jaja, sudžuk, goveđa pršuta, ajvar, sir", "image": "slike/korzo_dorucak.jpg"},
    "Kajgana": {"category": "Doručak", "price": 350.00, "calories": 300, "protein": 20, "carbs": 2, "fats": 22, "allergens": "Jaja", "dietary_tags": ["Vegetarijansko"], "description": "Domaća kajgana", "image": "slike/kajgana.jpg"},
    "Kačamak": {"category": "Doručak", "price": 300.00, "calories": 400, "protein": 10, "carbs": 50, "fats": 15, "allergens": "Mleko", "dietary_tags": ["Vegetarijansko"], "description": "Tradicionalni domaći kačamak", "image": "slike/kacamak.jpg"},
    "Juneća čorba 350g": {"category": "Toplo predjelo", "price": 480.00, "calories": 250, "protein": 15, "carbs": 10, "fats": 12, "allergens": "Celer", "dietary_tags": [], "description": "Domaća topla juneća čorba", "image": "slike/juneca_corba.jpg"},
    "Juneće ćufte 350g": {"category": "Jela sa roštilja", "price": 990.00, "calories": 650, "protein": 45, "carbs": 15, "fats": 40, "allergens": "Gluten", "dietary_tags": [], "description": "Sočne juneće ćufte sa roštilja", "image": "slike/junece_cufte.jpg"},
    "Juneći ćevapi 350g": {"category": "Jela sa roštilja", "price": 960.00, "calories": 700, "protein": 50, "carbs": 5, "fats": 50, "allergens": "Nema", "dietary_tags": [], "description": "Pravi domaći juneći ćevapi", "image": "slike/juneci_cevapi.jpg"},
    "Bagrem piletina 350g": {"category": "Jela sa roštilja", "price": 900.00, "calories": 500, "protein": 60, "carbs": 5, "fats": 20, "allergens": "Nema", "dietary_tags": ["Visok protein"], "description": "Specijalitet kuće od piletine", "image": "slike/bagrem_piletina.jpg"},
    "Goveđa pršuta 100g": {"category": "Hladno predjelo", "price": 900.00, "calories": 250, "protein": 30, "carbs": 0, "fats": 12, "allergens": "Nema", "dietary_tags": [], "description": "Kvalitetna domaća goveđa pršuta", "image": "slike/govedja_prsuta.jpg"},
    "Sušeni sudžuk 100g": {"category": "Hladno predjelo", "price": 480.00, "calories": 400, "protein": 20, "carbs": 2, "fats": 35, "allergens": "Nema", "dietary_tags": [], "description": "Domaći sušeni sudžuk", "image": "slike/suseni_sudzuk.jpg"},
    "Sir 100g": {"category": "Hladno predjelo", "price": 340.00, "calories": 350, "protein": 20, "carbs": 2, "fats": 28, "allergens": "Mleko", "dietary_tags": ["Vegetarijansko"], "description": "Domaћи beli sir", "image": "slike/sir.jpg"},
    "Mađarski juneći gulaš 450g": {"category": "Glavno jelo", "price": 1020.00, "calories": 600, "protein": 40, "carbs": 30, "fats": 30, "allergens": "Celer, Gluten", "dietary_tags": [], "description": "Bogati mađarski gulaš od junetine", "image": "slike/madjarski_gulas.jpg"},
    "Ćufte u pireu 350g": {"category": "Glavno jelo", "price": 660.00, "calories": 550, "protein": 30, "carbs": 45, "fats": 25, "allergens": "Mleko, Gluten", "dietary_tags": [], "description": "Domaće ćufte u kremastom pire krompiru", "image": "slike/cufte_u_pireu.jpg"},
    "Prebranac sa sudžukom 400g": {"category": "Glavno jelo", "price": 760.00, "calories": 650, "protein": 30, "carbs": 60, "fats": 30, "allergens": "Nema", "dietary_tags": [], "description": "Zapečeni pasulj sa sudžukom", "image": "slike/prebranac_sudzuk.jpg"},
    "Prebranac 300g": {"category": "Glavno jelo", "price": 590.00, "calories": 400, "protein": 18, "carbs": 50, "fats": 15, "allergens": "Nema", "dietary_tags": ["Vegansko", "Vegetarijansko"], "description": "Tradicionalni posni prebranac", "image": "slike/prebranac.jpg"},
    "Šopska salata 350g": {"category": "Salate", "price": 460.00, "calories": 200, "protein": 8, "carbs": 10, "fats": 15, "allergens": "Mleko", "dietary_tags": ["Vegetarijansko"], "description": "Paradajz, krastavac, luk, paprika, sir", "image": "slike/sopska_salata.jpg"},
    "Srpska salata 300g": {"category": "Salate", "price": 410.00, "calories": 100, "protein": 3, "carbs": 12, "fats": 5, "allergens": "Nema", "dietary_tags": ["Vegansko", "Vegetarijansko"], "description": "Paradajz, krastavac, luk, ljuta paprika", "image": "slike/srpska_salata.jpg"},
    "Kupus salata 300g": {"category": "Salate", "price": 330.00, "calories": 80, "protein": 2, "carbs": 10, "fats": 4, "allergens": "Nema", "dietary_tags": ["Vegansko", "Vegetarijansko"], "description": "Sveжа kupus salata", "image": "slike/kupus_salata.jpg"},
    "Ljuta paprika u ulju 1 komad": {"category": "Salate", "price": 150.00, "calories": 50, "protein": 0, "carbs": 2, "fats": 4, "allergens": "Nema", "dietary_tags": ["Vegansko", "Vegetarijansko"], "description": "Pečena ljuta paprika", "image": "slike/ljuta_paprika.jpg"},
    "Lepinja 1 komad": {"category": "Dodaci", "price": 120.00, "calories": 250, "protein": 7, "carbs": 50, "fats": 2, "allergens": "Gluten", "dietary_tags": ["Vegansko", "Vegetarijansko"], "description": "Sveжа domaća lepinja", "image": "slike/lepinja.jpg"},
    "Pomfrit 150g": {"category": "Dodaci", "price": 300.00, "calories": 450, "protein": 4, "carbs": 60, "fats": 20, "allergens": "Nema", "dietary_tags": ["Vegansko", "Vegetarijansko"], "description": "Hrskavi prženi krompirići", "image": "slike/pomfrit.jpg"},
    "Kugla kajmaka 1 komad": {"category": "Dodaci", "price": 180.00, "calories": 200, "protein": 2, "carbs": 1, "fats": 22, "allergens": "Mleko", "dietary_tags": ["Vegetarijansko"], "description": "Domaћи zreli kajmak", "image": "slike/kugla_kajmaka.jpg"}
}

# --- ПОМОЋНЕ ФУНКЦИЈЕ ---
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
    st.info("Екран се аутоматски освежава на сваких 10 секунди.")
    
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
                        # ✅ ЗАШТИТА: Проверавамо да ли јело постоји у менију пре него што узмемо цену
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
    if st.sidebar.button("🙋‍♂️ ПОЗОВИ КОНОБАРА", type="primary", use_container_width=True):
        moj_sto["zove_konobara"] = True
        snimi_u_bazu(sto, moj_sto)
        st.sidebar.success("Особље стиже!")

    st.sidebar.divider()
    st.sidebar.subheader("🛒 Ваша Поруџбина")
    ukupno = 0
    stavke_korpa = moj_sto.get("stavke", {})
    for jelo, qty in stavke_korpa.items():
        # ✅ ЗАШТИТА: Проверавамо да ли јело постоји у менију пре приказа цене
        if jelo in menu_database:
            cena_stavke = menu_database[jelo]["price"] * qty
            ukupno += cena_stavke
            st.sidebar.write(f"**{qty}x** {jelo} ({cena_stavke:.2f} RSD)")
        else:
            st.sidebar.write(f"⚠️ *{jelo}* (Стара ставка)")
            
    st.sidebar.metric("Укупно:", f"{ukupno:.2f} RSD")

    if st.sidebar.button("🧾 Плати рачун (Кеш)", use_container_width=True):
        moj_sto["trazi_racun"] = True
        moj_sto["nacin_placanja"] = "Кеш"
        snimi_u_bazu(sto, moj_sto)
        st.sidebar.info("Затражили сте рачун!")

    # ГЛАВНИ МЕНИ СА КАТЕГОРИЈАМА
    st.title("🍽️ Корзо Паметни Мени")
    
    # Добијамо јединствене категорије из базе менија
    sve_kategorije = sorted(list(set([info["category"] for info in menu_database.values()])))
    tabs = st.tabs(sve_kategorije)

    for i, tab in enumerate(tabs):
        with tab:
            kat = sve_kategorije[i]
            # Филтрирамо јела за ову категорију
            jela_kat = {k: v for k, v in menu_database.items() if v["category"] == kat}
            
            cols = st.columns(2)
            for j, (ime, info) in enumerate(jela_kat.items()):
                with cols[j % 2]:
                    with st.container(border=True):
                        st.image(prikazi_sliku(info["image"]), use_container_width=True)
                        st.subheader(ime)
                        st.write(f"Цена: **{info['price']:.2f} RSD**")
                        st.caption(info['description'])
                        
                        with st.expander("Више информација (Нутритиве)"):
                            st.write(f"🔥 {info['calories']} kcal | 🥩 {info['protein']}g протеина")
                            st.write(f"⚠️ Алергени: {info['allergens']}")
                        
                        if st.button(f"🛒 Додај", key=f"add_{ime}"):
                            moj_sto["stavke"][ime] = moj_sto["stavke"].get(ime, 0) + 1
                            snimi_u_bazu(sto, moj_sto)
                            st.toast(f"Додато: {ime}")
                            st.rerun()

    # AI ЧАТБОТ
    st.divider()
    st.subheader("🤖 Питајте нашег AI конобара")
    upit = st.chat_input("Напишите питање овде...")
    if upit:
        with st.chat_message("user"): st.markdown(upit)
        context = f"Ти си конобар у ресторану Корзо у Крагујевцу. Наш мени: {list(menu_database.keys())}. Гост пита: {upit}"
        with st.chat_message("assistant"):
            try:
                odgovor = client_ai.models.generate_content(model='gemini-2.0-flash', contents=context)
                st.markdown(odgovor.text)
            except:
                st.markdown("Извините, мој АИ мозак је тренутно заузет. Пробајте поново!")

# ==========================================
# 5. ГЛАВНИ РУТЕР (REDIRECT)
# ==========================================
params = st.query_params
if "konobar" in params:
    prikazi_konobara()
elif "sto" in params:
    prikazi_gosta(params["sto"])
else:
    st.title("Добродошли у Корзо! 🍽️")
    st.write("Скенирајте QR код на свом столу да поручите храну.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📱 Уђи као Сто 1 (Тест)"):
            st.query_params["sto"] = "1"
            st.rerun()
    with col2:
        if st.button("👨‍🍳 Контролни Панел"):
            st.query_params["konobar"] = "true"
            st.rerun()
