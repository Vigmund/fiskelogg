import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Fiskeloggen", page_icon="🐟", layout="centered")

# Anpassa bakgrundsfärg
st.markdown("""
    <style>
    body {
        background-color: #EDE8D0;
    }
    </style>
    """, unsafe_allow_html=True)

DATAFIL = "fiskeloggar.csv"

def safe_rerun():
    st.rerun()

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

    if not st.session_state.inloggad:
        menyval = st.sidebar.radio("Navigering", ["Logga in", "Skapa konto"])
        if menyval == "Logga in":
            login()
        elif menyval == "Skapa konto":
            register()
    else:
        menyval = st.sidebar.radio("Navigering", ["Logga ny fisk", "Mina loggar", "Logga ut"])
        if menyval == "Logga ny fisk":
            ny_logg()
        elif menyval == "Mina loggar":
            home()
        elif menyval == "Logga ut":
            st.session_state.inloggad = False
            st.session_state.användare = ""
            safe_rerun()

def login():
    st.subheader("Logga in")
    användarnamn = st.text_input("Användarnamn")
    lösenord = st.text_input("Lösenord", type="password")
    if st.button("Logga in"):
        if användarnamn and lösenord:
            st.session_state.inloggad = True
            st.session_state.användare = användarnamn
            st.success("Inloggning lyckades!")
            safe_rerun()
        else:
            st.error("Fyll i både användarnamn och lösenord.")

def register():
    st.subheader("Skapa konto")
    användarnamn = st.text_input("Välj användarnamn")
    lösenord = st.text_input("Välj lösenord", type="password")
    if st.button("Skapa konto"):
        if användarnamn and lösenord:
            st.session_state.inloggad = True
            st.session_state.användare = användarnamn
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
    art = st.text_input("Vilken art fångade du?")
    plats = st.text_input("Var fångade du den?")
    längd = st.number_input("Hur lång var fisken? (cm)", min_value=0.0, step=0.1)
    vikt = st.number_input("Hur mycket vägde den? (kg)", min_value=0.0, step=0.1)
    datum = st.date_input("När fångades fisken?", value=datetime.today())
    bild = st.file_uploader("Ladda upp en bild (valfritt)", type=["jpg", "jpeg", "png"])

    if st.button("Spara logg"):
        if not art or not plats:
            st.error("Fyll i alla obligatoriska fält.")
            return

        bildfilnamn = ""
        if bild:
            bildfilnamn = f"bilder/{datetime.now().strftime('%Y%m%d%H%M%S')}_{bild.name}"
            os.makedirs("bilder", exist_ok=True)
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
