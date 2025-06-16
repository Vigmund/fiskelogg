import streamlit as st
import pandas as pd
import os
import hashlib

LOGG_FIL = "loggar.csv"
USERS_FIL = "users.csv"
BILD_MAPP = "bilder"

# --- HJÄLPFUNKTIONER ---

def hash_losen(losen):
    return hashlib.sha256(losen.encode()).hexdigest()

def las_in_loggar():
    if os.path.exists(LOGG_FIL):
        return pd.read_csv(LOGG_FIL)
    else:
        return pd.DataFrame(columns=["Datum", "Art", "Vikt (kg)", "Plats", "Bild", "Användare"])

def las_in_users():
    if os.path.exists(USERS_FIL):
        return pd.read_csv(USERS_FIL)
    else:
        return pd.DataFrame(columns=["Användarnamn", "Lösenhash"])

def spara_loggar(df):
    df.to_csv(LOGG_FIL, index=False)

def spara_users(df):
    df.to_csv(USERS_FIL, index=False)

def skapa_mapp_om_saknas(mapp):
    if not os.path.exists(mapp):
        os.makedirs(mapp)

# --- GLOBALA VARIABLER ---
if "users_df" not in st.session_state:
    st.session_state.users_df = las_in_users()

if "df" not in st.session_state:
    st.session_state.df = las_in_loggar()

if "page" not in st.session_state:
    st.session_state.page = "login"

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "confirm_delete_index" not in st.session_state:
    st.session_state.confirm_delete_index = None

# --- SIDOR/FUNKTIONER ---

def login_page():
    st.title("Logga in / Registrera")
    användarnamn = st.text_input("Användarnamn")
    lösen = st.text_input("Lösenord", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Logga in"):
            if användarnamn == "" or lösen == "":
                st.error("Fyll i användarnamn och lösenord.")
                return
            users_df = st.session_state.users_df
            hashed = hash_losen(lösen)
            user_row = users_df[(users_df["Användarnamn"] == användarnamn) & (users_df["Lösenhash"] == hashed)]
            if not user_row.empty:
                st.session_state.current_user = användarnamn
                st.session_state.page = "home"
                st.success(f"Välkommen tillbaka, {användarnamn}!")
            else:
                st.error("Felaktigt användarnamn eller lösenord.")

    with col2:
        if st.button("Registrera nytt konto"):
            if användarnamn == "" or lösen == "":
                st.error("Fyll i användarnamn och lösenord.")
                return
            users_df = st.session_state.users_df
            if användarnamn in users_df["Användarnamn"].values:
                st.error("Användarnamnet är upptaget. Välj ett annat.")
            else:
                ny_rad = {"Användarnamn": användarnamn, "Lösenhash": hash_losen(lösen)}
                st.session_state.users_df = pd.concat([users_df, pd.DataFrame([ny_rad])], ignore_index=True)
                spara_users(st.session_state.users_df)
                st.success("Konto skapat! Logga in nu.")

def home_page():
    st.title(f"🎣 Fiskeloggen - Välkommen {st.session_state.current_user}")

    if st.button("Mina fångster"):
        st.session_state.page = "mina_fangster"

    if st.button("Ny logg"):
        st.session_state.page = "ny_logg"

    if st.button("Logga ut"):
        st.session_state.current_user = None
        st.session_state.page = "login"

def visa_mina_fangster():
    st.title("Mina fångster")
    df = st.session_state.df
    användare = st.session_state.current_user
    mina_fangster = df[df["Användare"] == användare]

    if mina_fangster.empty:
        st.info("Du har inga fångster ännu.")
    else:
        for i, row in mina_fangster.iterrows():
            with st.expander(f"{row['Datum']} – {row['Art']}"):
                st.write(f"Plats: {row['Plats']}")
                st.write(f"Vikt: {row['Vikt (kg)']} kg")
                if pd.notna(row['Bild']) and row['Bild'] != "":
                    try:
                        st.image(row['Bild'], width=200)
                    except:
                        st.warning("Bild kunde inte laddas.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Ta bort logg #{i}", key=f"ta_bort_{i}"):
                        st.session_state.confirm_delete_index = i

    if st.session_state.confirm_delete_index is not None:
        if st.button("Ja, ta bort loggen"):
            i = st.session_state.confirm_delete_index
            st.session_state.df = st.session_state.df.drop(i).reset_index(drop=True)
            spara_loggar(st.session_state.df)
            st.success("Logg borttagen.")
            st.session_state.confirm_delete_index = None
            st.experimental_rerun()
        if st.button("Nej, ångra"):
            st.session_state.confirm_delete_index = None
            st.experimental_rerun()

    if st.button("Tillbaka"):
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
            skapa_mapp_om_saknas(BILD_MAPP)
            bild_path = ""
            if bild is not None:
                bild_path = os.path.join(BILD_MAPP, bild.name)
                with open(bild_path, "wb") as f:
                    f.write(bild.getbuffer())

            ny_rad = {
                "Datum": datum.strftime("%Y-%m-%d"),
                "Art": art,
                "Vikt (kg)": vikt,
                "Plats": plats,
                "Bild": bild_path,
                "Användare": st.session_state.current_user
            }
            df = st.session_state.df
            st.session_state.df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
            spara_loggar(st.session_state.df)
            st.success("Logg sparad!")
            st.session_state.page = "home"

    if st.button("Tillbaka"):
        st.session_state.page = "home"

# --- HUVUDPROGRAM ---

if st.session_state.page == "login":
    login_page()

elif st.session_state.page == "home":
    home_page()

elif st.session_state.page == "mina_fangster":
    visa_mina_fangster()

elif st.session_state.page == "ny_logg":
    ny_logg()
