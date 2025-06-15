import streamlit as st
import pandas as pd
import os

LOGG_FIL = "loggar.csv"

# Läs in loggar
if os.path.exists(LOGG_FIL):
    df = pd.read_csv(LOGG_FIL)
else:
    df = pd.DataFrame(columns=["Datum", "Art", "Vikt (kg)", "Plats", "Bild"])

# Initiera sidan i session_state om inte satt
if "page" not in st.session_state:
    st.session_state.page = "home"

def visa_mina_fangster():
    st.title("Mina fångster")
    if df.empty:
        st.info("Du har inga fångster ännu.")
    else:
        for i, row in df.iterrows():
            with st.expander(f"{row['Datum']} – {row['Art']}"):
                st.write(f"Plats: {row['Plats']}")
                st.write(f"Vikt: {row['Vikt (kg)']} kg")
                if pd.notna(row['Bild']):
                    st.image(row['Bild'], width=200)
    if st.button("Tillbaka", key="tillbaka_fangster"):
        st.session_state.page = "home"

def ny_logg():
    st.title("Ny logg")
    with st.form("form_ny_logg"):
        datum = st.date_input("Datum")
        art = st.text_input("Art")
        vikt = st.number_input("Vikt (kg)", min_value=0.0, format="%.2f")
        plats = st.text_input("Plats")
        bild = st.file_uploader("Ladda upp bild", type=["png", "jpg", "jpeg"])

        submitted = st.form_submit_button("Spara logg")
        if submitted:
            # Spara bilden lokalt och spara sökväg i CSV (för enkelhetens skull)
            bild_path = ""
            if bild is not None:
                bild_path = f"bilder/{bild.name}"
                with open(bild_path, "wb") as f:
                    f.write(bild.getbuffer())

            ny_rad = {
                "Datum": datum.strftime("%Y-%m-%d"),
                "Art": art,
                "Vikt (kg)": vikt,
                "Plats": plats,
                "Bild": bild_path
            }
            global df
            df = df.append(ny_rad, ignore_index=True)
            df.to_csv(LOGG_FIL, index=False)
            st.success("Logg sparad!")
            st.session_state.page = "home"

    if st.button("Tillbaka", key="tillbaka_nylogg"):
        st.session_state.page = "home"

# Huvudmeny
if st.session_state.page == "home":
    st.title("🎣 Fiskeloggen")
    if st.button("Mina fångster"):
        st.session_state.page = "mina_fangster"
    if st.button("Ny logg"):
        st.session_state.page = "ny_logg"

elif st.session_state.page == "mina_fangster":
    visa_mina_fangster()

elif st.session_state.page == "ny_logg":
    ny_logg()
