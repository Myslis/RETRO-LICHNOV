import streamlit as st
from PIL import Image, ImageEnhance, ImageDraw
import random

st.set_page_config(page_title="Lichnov Retro Studio", page_icon="🚂")

st.title("🚂 Lichnov Retro Studio")
st.write("Vítejte v editoru pro kolejiště Lichnov.")

uploaded_file = st.file_uploader("Nahraj fotografii...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    width, height = img.size
    
    st.sidebar.header("Nastavení")
    age = st.sidebar.slider("Stáří (0-100)", 0, 100, 30)
    damage = st.sidebar.slider("Poškození (0-100)", 0, 100, 15)

    # Efekt stáří
    enhancer = ImageEnhance.Color(img)
    processed = enhancer.enhance(1 - (age / 100))
    processed = ImageEnhance.Contrast(processed).enhance(1 + (age / 250))

    # Efekt poškození
    if damage > 0:
        overlay = Image.new('RGBA', processed.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        for _ in range(int(damage / 4)):
            x = random.randint(0, width)
            draw.line([(x, 0), (x, height)], fill=(220, 220, 220, 100), width=1)
        processed.paste(overlay, (0, 0), mask=overlay)

    st.image(processed, caption="Výsledek", use_container_width=True)
