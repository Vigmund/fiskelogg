import streamlit as st

st.set_page_config(page_title="Fiskeloggen", page_icon="🐟", layout="centered")

# Bakgrundsbild (lägg bilden i samma mapp eller i en undermapp som t.ex. "bilder/")
background_url = "fiskeloggen bakgrund.png"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{background_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    .title-container {{
        text-align: center;
        margin-top: 50px;
    }}
    .title-text {{
        font-size: 48px;
        font-weight: bold;
        color: #3CA36C;
        font-family: Arial, sans-serif;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Visa logotyp och namn centrerat
st.markdown("""
<div class="title-container">
    <div class="title-text">🐟 FISKELOGGEN</div>
</div>
""", unsafe_allow_html=True)
