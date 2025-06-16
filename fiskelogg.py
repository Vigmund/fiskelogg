import streamlit as st
import pandas as pd
import os
import random

LOGG_FIL = "loggar.csv"
USERS_FIL = "users.csv"

# Gröna färger som vi ska använda för text med variation
GRONA_FARGER = ["#25523B", "#358856", "#5AAB61", "#62BD69", "#30694B", "#0C3823"]

def load_users():
    if os.path.exists(USERS_FIL):
        return pd.read_csv(USERS_FIL)
    else:
        return pd.DataFrame(columns=["username", "password"])

def load_logs():
    if os.path.exists(LOGG_FIL):
        return pd.read_csv(LOGG_FIL)
    else:
        return pd.DataFrame(columns=["username", "Datum", "Art", "Vikt (kg)", "Längd (cm)", "Plats", "Meddelande", "Bild"])

def save_users(df):
    df.to_csv(USERS_FIL, index=False)

def save_logs(df):
    df.to_csv(LOGG_FIL, index=False)

users_df = load_users()
logs_df = load_logs()

def get_random_gron_farg():
    return random.choice(GRONA_FARGER)

def set_custom_theme():
    # Generera CSS för text med varierande gröna färger (genom klasser)
    grona_css = "\n".join(
        [f".gron{i} {{ color: {farg}; }}" for i, farg in enumerate(GRONA_FARGER)]
    )

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: #EDE8D0;
            color: #25523B;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        }}
        .css-1v3fvcr h1 {{
            color: #30694B;
        }}
        .stButton > button {{
            background-color: #5AAB61;
            color: white;
            border-radius: 8px;
            padding: 8px 18px;
            font-weight: 600;
            border: none;
        }}
        .stButton > button:hover {{
            background-color: #62BD69;
            color: white;
        }}
        input, textarea {{
            border-radius: 6px;
            border: 1px solid #358856;
            padding: 6px;
        }}
        .streamlit-expanderHeader {{
            color: #0C3823;
            font-weight: 600;
        }}
        {grona_css}
        </style>
        """,
        unsafe_allow_html=True,
    )

set_custom_theme()

if "page" not in st.session_state:
    st.session_state.page = "login"

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

def colored_label(text):
    i = random.randint(0, len(GRONA_FARGER)-1)
    return f"<span class='gron{i}'>{text}</span>"

def register():
    st.markdown(f"<h1 class='gron{GRONA_FARGER.index('#30694B')}'>Registrera nytt konto</h1>", unsafe_allow_html=True)
    st.markdown(colored_label("Användarnamn"), unsafe_allow_html=True)
    username = st.text_input("", key="reg_user")
    st.markdown(colored_label("Lösenord"), unsafe_allow_html=True)
    password = st.text_input("", type="password", key="reg_pw")

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

    if st.button("Tillbaka till inloggning"):
        st.session_state.page = "login"

def login():
    st.markdown(f"<h1 class='gron{GRONA_FARGER.index('#30694B')}'>Logga in</h1>", unsafe_allow_html=True)
    st.markdown(colored_label("Användarnamn"), unsafe_allow_html=True)
    username = st.text_input("", key="login_user")
    st.markdown(colored_label("Lösenord"), unsafe_allow_html=True)
    password = st.text_input("", type="password", key="login_pw")

    if st.button("Logga in"):
        global users_df
        if (users_df["username"] == username).any():
            correct_password = users_df.loc[users_df["username"] == username, "password"].values[0]
            if password == correct_password:
                st.success(f"Välkommen, {username}!")
                st.session_state.logged_in_user = username
                st.session_state.page = "home"
            else:
                st.error("Fel lösenord.")
        else:
            st.error("Användarnamnet finns inte.")

    if st.button("Registrera nytt konto"):
        st.session_state.page = "register"

def visa_mina_fangster():
    st.markdown(f"<h1 class='gron{GRONA_FARGER.index('#30694B')}'>Mina fångster</h1>", unsafe_allow_html=True)
    global logs_df
    user_logs = logs_df[logs_df["username"] == st.session_state.logged_in_user]

    if user_logs.empty:
        st.info("Du har inga fångster ännu.")
    else:
        for i, row in user_logs.iterrows():
            with st.expander(f"{row['Datum']} – {row['Art']}"):
                st.markdown(f"<p class='gron{random.randint(0,len(GRONA_FARGER)-1)}'>{colored_label('Plats')}: {row['Plats']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='gron{random.randint(0,len(GRONA_FARGER)-1)}'>{colored_label('Vikt')}: {row['Vikt (kg)']} kg</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='gron{random.randint(0,len(GRONA_FARGER)-1)}'>{colored_label('Längd')}: {row.get('Längd (cm)', 'N/A')} cm</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='gron{random.randint(0,len(GRONA_FARGER)-1)}'>{colored_label('Meddelande')}: {row.get('Meddelande', '')}</p>", unsafe_allow_html=True)
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
                            st.session_state.page = "mina_fangster"
                            st.session_state[f"ta_bort_{i}"] = False
                    with col2:
                        if st.button("Nej", key=f"nej_{i}"):
                            st.session_state[f"ta_bort_{i}"] = False

    if st.button("Tillbaka"):
        st.session_state.page = "home"

def ny_logg():
    st.markdown(f"<h1 class='gron{GRONA_FARGER.index('#30694B')}'>Ny logg</h1>", unsafe_allow_html=True)
    global logs_df

    with st.form("form_ny_logg"):
        st.markdown(colored_label("Datum"))
        datum = st.date_input("")
        st.markdown(colored_label("Art"))
        art = st.text_input("")
        st.markdown(colored_label("Vikt (kg)"))
        vikt = st.number_input("", min_value=0.0, format="%.2f")
        st.markdown(colored_label("Längd (cm)"))
        langd = st.number_input("", min_value=0, format="%d")
        st.markdown(colored_label("Plats"))
        plats = st.text_input("")
        st.markdown(colored_label("Meddelande"))
        meddelande = st.text_area("")
        st.markdown(colored_label("Bild (URL)"))
        bild = st.text_input("")

        submitted = st.form_submit_button("Spara logg")

        if submitted:
            ny_logg = {
                "username": st.session_state.logged_in_user,
                "Datum": datum.strftime("%Y-%m-%d"),
                "Art": art,
                "Vikt (kg)": vikt,
                "Längd (cm)": langd,
                "Plats": plats,
                "Meddelande": meddelande,
                "Bild": bild,
            }
            logs_df = pd.concat([logs_df, pd.DataFrame([ny_logg])], ignore_index=True)
            save_logs(logs_df)
            st.success("Logg sparad!")
            st.session_state.page = "mina_fangster"

def home():
    st.markdown(f"<h1 class='gron{GRONA_FARGER.index('#30694B')}'>🎣 Fiskeloggen</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Mina fångster", use_container_width=True):
            st.session_state.page = "mina_fangster"
    with col2:
        if st.button("Ny logg", use_container_width=True):
            st.session_state.page = "ny_logg"

    if st.button("Logga ut"):
        st.session_state.logged_in_user = None
        st.session_state.page = "login"

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
