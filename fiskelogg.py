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

if "delete_index" not in st.session_state:
    st.session_state.delete_index = None
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False
if "do_delete" not in st.session_state:
    st.session_state.do_delete = False

def visa_mina_fangster():
    st.title("Mina fångster")

    if df.empty:
        st.info("Du har inga fångster ännu.")
    else:
        for i, row in df.iterrows():
            with st.expander(f"{row['Datum']} – {row['Art']}"):
                st.write(f"Plats: {row['Plats']}")
                st.write(f"Vikt: {row['Vikt (kg)']} kg")
                if pd.notna(row['Bild']) and row['Bild'] != "":
                    st.image(row['Bild'], width=200)

                if st.session_state.delete_index is None:
                    if st.button("Ta bort logg", key=f"delete_{i}"):
                        st.session_state.delete_index = i
                elif st.session_state.delete_index == i:
                    st.warning("Är du säker på att du vill slänga tillbaks den här fisken i sjön?")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Ja, ta bort", key=f"confirm_{i}"):
                            st.session_state.confirm_delete = True
                    with col2:
                        if st.button("Nej, ångra", key=f"cancel_{i}"):
                            st.session_state.delete_index = None
                            st.session_state.confirm_delete = False

    if st.button("Tillbaka", key="tillbaka_fangster"):
        st.session_state.delete_index = None
        st.session_state.confirm_delete = False
        st.session_state.page = "home"

def ny_logg():
    global df
    st.title("Ny logg")
    with st.form("form_ny_logg"):
        datum = st.date_input("Datum")
        art = st.text_input("Art")
        vikt = st.number_input("Vikt (kg)", min_value=0.0, format="%.2f")
        plats = st.text_input("Plats")
        bild = st.file_uploader("Ladda upp bild", type=["png", "jpg", "jpeg"])

        submitted = st.form_submit_button("Spara logg")
        if submitted:
            os.makedirs("bilder", exist_ok=True)

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
            df.loc[len(df)] = ny_rad
            df.to_csv(LOGG_FIL, index=False)

            st.success("Logg sparad!")
            st.session_state.page = "home"

    if st.button("Tillbaka", key="tillbaka_nylogg"):
        st.session_state.page = "home"

# Huvudmeny och sidlogik
if st.session_state.page == "home":
    st.title("🎣 Fiskeloggen")
    if st.button("Mina fångster"):
        st.session_state.page = "mina_fangster"
    if st.button("Ny logg"):
        st.session_state.page = "ny_logg"

elif st.session_state.page == "mina_fangster":
    visa_mina_fangster()

    # Här gör vi själva borttagningen och rerun UTANFÖR funktionen
    if st.session_state.confirm_delete and st.session_state.delete_index is not None:
        i = st.session_state.delete_index
        row = df.iloc[i]

        # Ta bort bildfil om den finns
        if pd.notna(row['Bild']) and row['Bild'] != "" and os.path.exists(row['Bild']):
            os.remove(row['Bild'])

        df.drop(i, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.to_csv(LOGG_FIL, index=False)

        # Nollställ session state och rerun sidan
        st.session_state.delete_index = None
        st.session_state.confirm_delete = False
        st.experimental_rerun()

elif st.session_state.page == "ny_logg":
    ny_logg()
