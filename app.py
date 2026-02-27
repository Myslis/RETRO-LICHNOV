import streamlit as st
from PIL import Image, ImageEnhance, ImageOps, ImageDraw
import numpy as np
import io

# Nastavení stránky
st.set_page_config(page_title="Lichnov Retro Studio", page_icon="🚂", layout="centered")

# CSS pro stylování rozhraní (tmavý retro vzhled)
st.markdown("""
    <style>
    .main { background-color: #0f0e0d; color: #d4c4b0; }
    .stButton>button { background-color: #a67c52; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

def apply_vignette(img, intensity):
    """Přidá efekt vinětace (ztmavení rohů)."""
    if intensity <= 0:
        return img
    
    width, height = img.size
    # Vytvoření masky pro vinětaci
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    
    # Intenzita vinětace ovlivňuje poloměr a průhlednost
    max_dim = max(width, height)
    for i in range(int(max_dim * 0.8), int(max_dim * 0.4), -1):
        alpha = int(255 * (intensity / 100) * (1 - i / (max_dim * 0.8)))
        draw.ellipse([width//2 - i, height//2 - i, width//2 + i, height//2 + i], fill=alpha)
    
    # Vytvoření černé vrstvy
    black = Image.new('RGB', (width, height), (0, 0, 0))
    # Prolnutí původního obrázku s černou podle masky
    return Image.composite(black, img, mask)

def apply_tint(img, tint_value):
    """Přidá studené (modré) nebo teplé (oranžové) tónování."""
    if tint_value == 0:
        return img
    
    width, height = img.size
    if tint_value > 0:
        # Teplá: Oranžovo-žlutá
        overlay_color = (255, 150, 0)
        alpha = int(abs(tint_value) * 0.6)
    else:
        # Studená: Modrá
        overlay_color = (0, 100, 255)
        alpha = int(abs(tint_value) * 0.6)
        
    overlay = Image.new('RGB', (width, height), overlay_color)
    # Použití prolnutí (blend) k simulaci barevného filtru
    return Image.blend(img, overlay, alpha / 1000)

def process_image(img, age, exposure, tint, vignette):
    """Hlavní logika zpracování obrazu podle parametrů z editoru."""
    
    # 1. Stáří (Saturace a Sepia)
    # Snížení sytosti
    sat_enhancer = ImageEnhance.Color(img)
    img = sat_enhancer.enhance(1.0 - (age * 0.015))
    
    # Sepia efekt pro vyšší stáří
    if age > 30:
        sepia_intensity = (age - 30) / 70.0
        # Vytvoření sepia tónu
        gray = ImageOps.grayscale(img).convert("RGB")
        sepia_overlay = Image.new('RGB', img.size, (255, 240, 190))
        img = Image.blend(gray, sepia_overlay, sepia_intensity * 0.3)

    # 2. Expozice (Brightness & Contrast)
    bright_factor = 1.0 + (exposure * 0.007)
    bright_enhancer = ImageEnhance.Brightness(img)
    img = bright_enhancer.enhance(bright_factor)
    
    contrast_factor = 1.0 + (age * 0.003) + (abs(exposure) * 0.004)
    contrast_enhancer = ImageEnhance.Contrast(img)
    img = contrast_enhancer.enhance(contrast_factor)

    # 3. Tónování
    img = apply_tint(img, tint)

    # 4. Vinětace
    img = apply_vignette(img, vignette)
    
    return img

# --- UI APLIKACE ---
st.title("🚂 LICHNOV RETRO STUDIO")
st.write("Ateliér historické fotografie | Marcel Balon")
st.markdown("---")

uploaded_file = st.file_uploader("Vyberte snímek z kolejiště...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Načtení
    source_img = Image.open(uploaded_file).convert("RGB")
    
    # Ovládací prvky v bočním panelu
    st.sidebar.header("Nastavení parametrů")
    
    age = st.sidebar.slider("Stáří (Barvy)", 0, 100, 40)
    exposure = st.sidebar.slider("Expozice (Pod / Pře)", -100, 100, 0)
    tint = st.sidebar.slider("Tónování (Studené / Teplé)", -100, 100, 0)
    vignette = st.sidebar.slider("Vinětace (Rohy)", 0, 100, 30)
    
    if st.sidebar.button("✨ Aplikovat FOTO_LICHNOV"):
        age, exposure, tint, vignette = 55, 15, 20, 40
        # Streamlit neumožňuje přímou změnu sliderů z buttonu bez session state, 
        # ale hodnoty se přepíší pro aktuální výpočet
        st.sidebar.info("Nastavení FOTO_LICHNOV aktivováno.")

    # Zpracování
    with st.spinner('Vyvolávám fotografii v temné komoře...'):
        result_img = process_image(source_img, age, exposure, tint, vignette)
    
    # Zobrazení
    st.image(result_img, caption="Výsledný historický snímek", use_container_width=True)
    
    # Stažení
    buf = io.BytesIO()
    result_img.save(buf, format="JPEG", quality=95)
    byte_im = buf.getvalue()
    
    st.download_button(
        label="📥 Uložit fotografii do archivu",
        data=byte_im,
        file_name="Lichnov_Retro_Foto.jpg",
        mime="image/jpeg"
    )
    
    st.info("💡 Tip: Pro nejlepší výsledek u modelů ČSD doporučuji mírnou kladnou expozici.")

else:
    st.info("Nahrajte fotografii svého kolejiště pro zahájení úprav.")
