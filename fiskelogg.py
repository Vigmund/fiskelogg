import streamlit as st
import pandas as pd
import os

LOGG_FIL = "loggar.csv"
USERS_FIL = "users.csv"

# Läs in användare
if os.path.exists(USERS_FIL):
    users_df = pd.read_csv(USERS_FIL)
else:
    users_df = pd.DataFrame(columns=["username", "password"])
    users_df.to_csv(USERS_FIL, index=False)

# Läs in loggar
if os.path.exists(LOGG_FIL):
    df = pd.read_csv(LOGG_FIL)
else:
    df = pd.DataFrame(columns=["Datum", "Art", "Vikt (kg)", "Plats", "Bild", "username"])

# Initiera session_state variabler
if "page" not in st.session_state:
    st.session_state.page = "login"
if "username" not in st.session_state:
    st.session_state.username = None

def save_users():
    users_df.to_csv(USERS_FIL, index=False)

def save_logs():
    df.to_csv(LOGG_FIL, index=False)

def login():
    global users_df
    st.title("🎣 Fiskeloggen - Logga in eller registrera dig")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Logga in")
        with st.form("login_form"):
            username = st.text_input("Användarnamn", key="login_user")
            password = st.text_input("Lösenord", type="password", key="login_pass")
            submitted = st.form_submit_button("Logga in")
            if submitted:
                user = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
                if not user.empty:
                    st.session_state.username = username
                    st.session_state.page = "home"
                    st.experimental_rerun()
                else:
                    st.error("Fel användarnamn eller lösenord")

    with col2:
        st.subheader("Registrera nytt konto")
        with st.form("register_form"):
            new_username = st.text_input("Nytt användarnamn", key="reg_user")
            new_password = st.text_input("Nytt lösenord", type="password", key="reg_pass")
            submitted = st.form_submit_button("Registrera")
            if submitted:
                if new_username.strip() == "" or new_password.strip() == "":
                    st.error("Användarnamn och lösenord får inte vara tomma")
                elif new_username in users_df['username'].values:
                    st.error("Användarnamnet är redan taget")
                else:
                    users_df.loc[len(users_df)] = [new_username, new_password]
                    save_users()
                    users_df = pd.read_csv(USERS_FIL)  # Ladda om users_df efter sparande
                    st.success("Konto skapat! Logga in ovan.")
                    st.session_state.page = "login"
                    st.experimental_rerun()

def visa_mina_fangster():
    global df
    st.title(f"Mina fångster - {st.session_state.username}")
    user_logs = df[df['username'] == st.session_state.username]
    if user_logs.empty:
        st.info("Du har inga fångster ännu.")
    else:
        for i, row in user_logs.iterrows():
            with st.expander(f"{row['Datum']} – {row['Art']}"):
                st.write(f"Plats: {row['Plats']}")
                st.write(f"Vikt: {row['Vikt (kg)']} kg")
                if pd.notna(row['Bild']) and row['Bild'] != "":
                    st.image(row['Bild'], width=200)
                if st.button("Ta bort logg", key=f"ta_bort_{i}"):
                    if st.confirm("Är du säker på att du vill slänga tillbaks den här fisken i sjön?"):
                        df = df.drop(i).reset_index(drop=True)
                        save_logs()
                        st.success("Logg borttagen.")
                        st.experimental_rerun()
    if st.button("Tillbaka"):
        st.session_state.page = "home"
        st.experimental_rerun()

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
            bild_path = ""
            if bild is not None:
                if not os.path.exists("bilder"):
                    os.makedirs("bilder")
                bild_path = f"bilder/{bild.name}"
                with open(bild_path, "wb") as f:
                    f.write(bild.getbuffer())

            ny_rad = {
                "Datum": datum.strftime("%Y-%m-%d"),
                "Art": art,
                "Vikt (kg)": vikt,
                "Plats": plats,
                "Bild": bild_path,
                "username": st.session_state.username
            }
            df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
            save_logs()
            st.success("Logg sparad!")
            st.session_state.page = "home"
            st.experimental_rerun()

    if st.button("Tillbaka"):
        st.session_state.page = "home"
        st.experimental_rerun()

def home():
    st.title("🎣 Fiskeloggen")
    if st.button("Mina fångster"):
        st.session_state.page = "mina_fangster"
        st.experimental_rerun()
    if st.button("Ny logg"):
        st.session_state.page = "ny_logg"
        st.experimental_rerun()
    if st.button("Logga ut"):
        st.session_state.username = None
        st.session_state.page = "login"
        st.experimental_rerun()

if st.session_state.page == "login":
    login()
elif st.session_state.page == "home":
    home()
elif st.session_state.page == "mina_fangster":
    visa_mina_fangster()
elif st.session_state.page == "ny_logg":
    ny_logg()
