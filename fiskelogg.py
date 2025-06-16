import streamlit as st
import pandas as pd
import os

LOGG_FIL = "loggar.csv"
USERS_FIL = "users.csv"

def load_users():
    if os.path.exists(USERS_FIL):
        return pd.read_csv(USERS_FIL)
    else:
        return pd.DataFrame(columns=["username", "password"])

def load_logs():
    if os.path.exists(LOGG_FIL):
        return pd.read_csv(LOGG_FIL)
    else:
        return pd.DataFrame(columns=["username", "Datum", "Art", "Vikt (kg)", "Plats", "Bild"])

def save_users(df):
    df.to_csv(USERS_FIL, index=False)

def save_logs(df):
    df.to_csv(LOGG_FIL, index=False)

users_df = load_users()
logs_df = load_logs()

def set_custom_theme():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #EDE8D0;
            color: #25523B;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        }
        .css-1v3fvcr h1 {
            color: #30694B;
        }
        .stButton > button {
            background-color: #5AAB61;
            color: white;
            border-radius: 8px;
            padding: 8px 18px;
            font-weight: 600;
            border: none;
        }
        .stButton > button:hover {
            background-color: #62BD69;
            color: white;
        }
        input, textarea {
            border-radius: 6px;
            border: 1px solid #358856;
            padding: 6px;
        }
        .streamlit-expanderHeader {
            color: #0C3823;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

set_custom_theme()

if "page" not in st.session_state:
    st.session_state.page = "login"

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

def register():
    st.title("Registrera nytt konto")
    username = st.text_input("Användarnamn", key="reg_user")
    password = st.text_input("Lösenord", type="password", key="reg_pw")

    if st.button("Registrera"):
        global users_df
        if username.strip() == "" or password.strip() == "":
            st.warning("Användarnamn och lösenord får inte vara tomma.")
        elif username in users_df["username"].values:
            st.error("Användarnamnet är upptaget, välj ett annat.")
        else:
            ny_user = {"username": username, "password": password}
            users_df = pd.concat([users_df, pd.DataFrame([ny_user])], ignore_index=True)
            save_users(users_df)
            st.success("Konto skapat! Logga in nu.")
            st.session_state.page = "login"
            # Istället för direkt rerun här, gör en liten knapp för användaren att trycka
            st.experimental_rerun()

    if st.button("Tillbaka till inloggning"):
        st.session_state.page = "login"
        st.experimental_rerun()

def login():
    st.title("Logga in")
    username = st.text_input("Användarnamn", key="login_user")
    password = st.text_input("Lösenord", type="password", key="login_pw")

    if st.button("Logga in"):
        global users_df
        if (users_df["username"] == username).any():
            correct_password = users_df.loc[users_df["username"] == username, "password"].values[0]
            if password == correct_password:
                st.success(f"Välkommen, {username}!")
                st.session_state.logged_in_user = username
                st.session_state.page = "home"
                st.experimental_rerun()
            else:
                st.error("Fel lösenord.")
        else:
            st.error("Användarnamnet finns inte.")

    if st.button("Registrera nytt konto"):
        st.session_state.page = "register"
        st.experimental_rerun()

def visa_mina_fangster():
    st.title("Mina fångster")
    global logs_df
    user_logs = logs_df[logs_df["username"] == st.session_state.logged_in_user]

    if user_logs.empty:
        st.info("Du har inga fångster ännu.")
    else:
        for i, row in user_logs.iterrows():
            with st.expander(f"{row['Datum']} – {row['Art']}"):
                st.write(f"Plats: {row['Plats']}")
                st.write(f"Vikt: {row['Vikt (kg)']} kg")
                if pd.notna(row['Bild']) and row['Bild'] != "":
                    st.image(row['Bild'], width=200)

                if f"ta_bort_{i}" not in st.session_state:
                    st.session_state[f"ta_bort_{i}"] = False

                if not st.session_state[f"ta_bort_{i}"]:
                    if st.button("Ta bort logg", key=f"btn_{i}"):
                        st.session_state[f"ta_bort_{i}"] = True
                else:
                    st.warning("Är du säker på att du vill slänga tillbaks den här fisken i sjön?")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Ja, ta bort", key=f"ja_{i}"):
                            logs_df = logs_df.drop(row.name)
                            save_logs(logs_df)
                            st.success("Logg borttagen!")
                            st.experimental_rerun()
                    with col2:
                        if st.button("Nej", key=f"nej_{i}"):
                            st.session_state[f"ta_bort_{i}"] = False
                            st.experimental_rerun()

    if st.button("Tillbaka"):
        st.session_state.page = "home"
        st.experimental_rerun()

def ny_logg():
    st.title("Ny logg")
    global logs_df

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
                "username": st.session_state.logged_in_user,
                "Datum": datum.strftime("%Y-%m-%d"),
                "Art": art,
                "Vikt (kg)": vikt,
                "Plats": plats,
                "Bild": bild_path
            }
            logs_df = pd.concat([logs_df, pd.DataFrame([ny_rad])], ignore_index=True)
            save_logs(logs_df)
            st.success("Logg sparad!")
            st.session_state.page = "home"
            st.experimental_rerun()

    if st.button("Tillbaka"):
        st.session_state.page = "home"
        st.experimental_rerun()

def home():
    st.title("🎣 Fiskeloggen")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Mina fångster", use_container_width=True):
            st.session_state.page = "mina_fangster"
            st.experimental_rerun()
    with col2:
        if st.button("Ny logg", use_container_width=True):
            st.session_state.page = "ny_logg"
            st.experimental_rerun()

    if st.button("Logga ut"):
        st.session_state.logged_in_user = None
        st.session_state.page = "login"
        st.experimental_rerun()

if st.session_state.page == "login":
    login()
elif st.session_state.page == "register":
    register()
elif st.session_state.page == "home":
    home()
elif st.session_state.page == "mina_fangster":
    visa_mina_fangster()
elif st.session_state.page == "ny_logg":
    ny_logg()
else:
    st.error("Okänt läge!")
