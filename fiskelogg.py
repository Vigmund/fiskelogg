import streamlit as st
import pandas as pd
import os
import hashlib

LOGG_FIL = "loggar.csv"
USERS_FIL = "users.csv"

# --- Läs in data ---
if os.path.exists(LOGG_FIL):
    df = pd.read_csv(LOGG_FIL)
else:
    df = pd.DataFrame(columns=["Username", "Datum", "Art", "Vikt (kg)", "Plats", "Bild"])

if os.path.exists(USERS_FIL):
    users_df = pd.read_csv(USERS_FIL)
else:
    users_df = pd.DataFrame(columns=["Username", "PasswordHash"])

# --- Hjälpfunktioner ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# --- Initiera session_state ---
if "page" not in st.session_state:
    st.session_state.page = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""

# --- Funktioner ---
def login():
    st.title("Logga in eller registrera dig")

    tab1, tab2 = st.tabs(["Logga in", "Registrera"])

    with tab1:
        username = st.text_input("Användarnamn (login)", key="login_username")
        password = st.text_input("Lösenord", type="password", key="login_password")
        if st.button("Logga in", key="btn_login"):
            if username in users_df["Username"].values:
                user_row = users_df[users_df["Username"] == username].iloc[0]
                if verify_password(password, user_row["PasswordHash"]):
                    st.session_state.logged_in = True
                    st.session_state.user = username
                    st.session_state.page = "home"
                    st.experimental_rerun()
                else:
                    st.error("Fel lösenord.")
            else:
                st.error("Användarnamnet finns inte.")

    with tab2:
        new_username = st.text_input("Användarnamn (registrera)", key="reg_username")
        new_password = st.text_input("Lösenord", type="password", key="reg_password")
        confirm_password = st.text_input("Bekräfta lösenord", type="password", key="reg_password_confirm")
        if st.button("Registrera", key="btn_register"):
            if new_username.strip() == "" or new_password.strip() == "":
                st.error("Användarnamn och lösenord får inte vara tomma.")
            elif new_username in users_df["Username"].values:
                st.error("Användarnamnet är upptaget.")
            elif new_password != confirm_password:
                st.error("Lösenorden matchar inte.")
            else:
                new_user = {
                    "Username": new_username,
                    "PasswordHash": hash_password(new_password)
                }
                global users_df
                users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
                users_df.to_csv(USERS_FIL, index=False)
                st.success("Registrering lyckades! Du kan nu logga in.")
                # Rensa registreringsfält
                st.session_state.reg_username = ""
                st.session_state.reg_password = ""
                st.session_state.reg_password_confirm = ""

def visa_mina_fangster():
    st.title(f"Mina fångster — {st.session_state.user}")
    user_loggar = df[df["Username"] == st.session_state.user]
    if user_loggar.empty:
        st.info("Du har inga fångster ännu.")
    else:
        for i, row in user_loggar.iterrows():
            with st.expander(f"{row['Datum']} – {row['Art']}"):
                st.write(f"Plats: {row['Plats']}")
                st.write(f"Vikt: {row['Vikt (kg)']} kg")
                if pd.notna(row['Bild']) and row['Bild'] != "":
                    st.image(row['Bild'], width=200)
                if st.button("Ta bort logg", key=f"ta_bort_{i}"):
                    if st.confirm("Är du säker på att du vill slänga tillbaks den här fisken i sjön?"):
                        global df
                        df = df.drop(i)
                        df.to_csv(LOGG_FIL, index=False)
                        st.success("Logg borttagen")
                        st.experimental_rerun()
    if st.button("Logga ut"):
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.session_state.page = "login"
        st.experimental_rerun()

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
            bild_path = ""
            if bild is not None:
                if not os.path.exists("bilder"):
                    os.mkdir("bilder")
                bild_path = f"bilder/{st.session_state.user}_{bild.name}"
                with open(bild_path, "wb") as f:
                    f.write(bild.getbuffer())

            ny_rad = {
                "Username": st.session_state.user,
                "Datum": datum.strftime("%Y-%m-%d"),
                "Art": art,
                "Vikt (kg)": vikt,
                "Plats": plats,
                "Bild": bild_path
            }
            global df
            df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
            df.to_csv(LOGG_FIL, index=False)
            st.success("Logg sparad!")
            st.session_state.page = "home"
            st.experimental_rerun()

    if st.button("Tillbaka"):
        st.session_state.page = "home"
        st.experimental_rerun()

# --- Layout och navigation ---
if st.session_state.logged_in:
    if st.session_state.page == "home":
        st.title("🎣 Fiskeloggen")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Mina fångster"):
                st.session_state.page = "mina_fangster"
                st.experimental_rerun()
        with col2:
            if st.button("Ny logg"):
                st.session_state.page = "ny_logg"
                st.experimental_rerun()

    elif st.session_state.page == "mina_fangster":
        visa_mina_fangster()

    elif st.session_state.page == "ny_logg":
        ny_logg()

else:
    login()
