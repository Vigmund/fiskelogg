import streamlit as st
import base64

# Ladda bilden som bakgrund
def add_bg_from_local(image_file):
    with open(image_file, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Lägg till din bakgrund
add_bg_from_local("fiskeloggen bakgrund.png")

# Exempel på innehåll ovanpå bilden
st.markdown("<h1 style='text-align: center; color: white;'>Välkommen till Fiskeloggen</h1>", unsafe_allow_html=True)
st.button("Logga in")
st.button("Skapa konto")
