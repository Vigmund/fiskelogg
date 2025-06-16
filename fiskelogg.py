import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Fiskeloggen", page_icon="🐟", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #EDE8D0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

DATAFIL = "fiskeloggar.csv"

def safe_rerun():
    try:
        st.experimental_rerun()
    except Exception:
        pass

def läs_data():
    if os.path.exists(DATAFIL):
        return pd.read_csv(DATAFIL)
    else:
        return pd.DataFrame(columns=["Användare", "Art", "Plats", "Längd (cm)", "Vikt (kg)", "Datum", "Bildfil"])

def spara_data(df):
    df.to_csv(DATAFIL, index=False)

def startsida():
    st.title("🐟 Fiskeloggen")

    if "inloggad" not in st.session_state:
        st.session_state.inloggad = False
    if "användare" not in st.session_state:
        st.session_state.användare = ""

    if not st.session_state.inloggad:
        st.write("### Välj ett alternativ:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Logga in", key="btn_logga_in"):
                st.session_state.val = "Logga in"
                safe_rerun()
        with col2:
            if st.button("Skapa konto", key="btn_skapa_konto"):
                st.session_state.val = "Skapa konto"
                safe_rerun()

        val = st.session_state.get("val", None)
        if val == "Logga in":
            login()
        elif val == "Skapa konto":
            register()
    else:
        st.write(f"### Välkommen, {st.session_state.användare}!")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Logga ny fisk", key="btn_logga_ny_fisk"):
                st.session_state.val = "Logga ny fisk"
                safe_rerun()
        with col2:
            if st.button("Mina loggar", key="btn_mina_loggar"):
                st.session_state.val = "Mina loggar"
                safe_rerun()
        with col3:
            if st.button("Logga ut", key="btn_logga_ut"):
                st.session_state.inloggad = False
                st.session_state.användare = ""
                st.session_state.val = None
                safe_rerun()

        val = st.session_state.get("val", None)
        if val == "Logga ny fisk":
            ny_logg()
        elif val == "Mina loggar":
            home()

def login():
    st.subheader("Logga in")
    användarnamn = st.text_input("Användarnamn", key="login_anvandarnamn")
    lösenord = st.text_input("Lösenord", type="password", key="login_losenord")
    if st.button("Logga in", key="btn_logga_in_knapp"):
        if användarnamn and lösenord:
            st.session_state.inloggad = True
            st.session_state.användare = användarnamn
            st.session_state.val = None
            st.success("Inloggning lyckades!")
            safe_rerun()
        else:
            st.error("Fyll i både användarnamn och lösenord.")

def register():
    st.subheader("Skapa konto")
    användarnamn = st.text_input("Välj användarnamn", key="register_anvandarnamn")
    lösenord = st.text_input("Välj lösenord", type="password", key="register_losenord")
    if st.button("Skapa konto", key="btn_skapa_konto_register"):
        if användarnamn and lösenord:
            st.session_state.inloggad = True
            st.session_state.användare = användarnamn
            st.session_state.val = None
            st.success("Konto skapades!")
            safe_rerun()
        else:
            st.error("Fyll i både användarnamn och lösenord.")

def home():
    st.title("📖 Mina fiskeloggar")
    df = läs_data()
    användare = st.session_state.användare
    användarloggar = df[df["Användare"] == användare]

    if användarloggar.empty:
        st.info("Du har inte loggat någon fisk ännu.")
    else:
        for i, rad in användarloggar.iterrows():
            with st.container():
                st.markdown(f"**Art:** {rad['Art']}")
                st.markdown(f"**Plats:** {rad['Plats']}")
                st.markdown(f"**Längd:** {rad['Längd (cm)']} cm")
                st.markdown(f"**Vikt:** {rad['Vikt (kg)']} kg")
                st.markdown(f"**Datum:** {rad['Datum']}")
                if rad["Bildfil"] and os.path.exists(rad["Bildfil"]):
                    st.image(rad["Bildfil"], width=300)
                if st.button("🗑️ Ta bort", key=f"ta_bort_{i}"):
                    df = df.drop(i)
                    spara_data(df)
                    st.success("Loggen togs bort.")
                    safe_rerun()

def ny_logg():
    st.title("➕ Logga ny fisk")
    art = st.text_input("Vilken art fångade du?", key="nylogg_art")
    plats = st.text_input("Var fångade du den?", key="nylogg_plats")
    längd = st.number_input("Hur lång var fisken? (cm)", min_value=0.0, step=0.1, key="nylogg_langd")
    vikt = st.number_input("Hur mycket vägde den? (kg)", min_value=0.0, step=0.1, key="nylogg_vikt")
    datum = st.date_input("När fångades fisken?", value=datetime.today(), key="nylogg_datum")
    bild = st.file_uploader("Ladda upp en bild (valfritt)", type=["jpg", "jpeg", "png"], key="nylogg_bild")

    if st.button("Spara logg", key="btn_spara_logg"):
        if not art or not plats:
            st.error("Fyll i alla obligatoriska fält.")
            return

        bildfilnamn = ""
        if bild:
            os.makedirs("bilder", exist_ok=True)
            bildfilnamn = f"bilder/{datetime.now().strftime('%Y%m%d%H%M%S')}_{bild.name}"
            with open(bildfilnamn, "wb") as f:
                f.write(bild.read())

        ny_rad = pd.DataFrame([{
            "Användare": st.session_state.användare,
            "Art": art,
            "Plats": plats,
            "Längd (cm)": längd,
            "Vikt (kg)": vikt,
            "Datum": datum.strftime("%Y-%m-%d"),
            "Bildfil": bildfilnamn
        }])

        df = läs_data()
        df = pd.concat([df, ny_rad], ignore_index=True)
        spara_data(df)
        st.success("Fångsten sparades!")
        safe_rerun()

# Starta appen
startsida()
