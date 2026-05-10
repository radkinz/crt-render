import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

PALETTES = {
    "green": (20, 170, 75),
    "blue": (55, 125, 210),
    "pink": (255, 105, 180),
    "amber": (255, 170, 55),
    "white": (220, 230, 220),
}

ASCII_SETS = {
    "simple": " .:-=+*#%@",
    "soft": " .,:;i+*#%@",
    "chunky": " .:=#",
    "blocks": " ░▒▓█",
}

def render_ascii(
    img,
    ascii_width,
    font_size,
    palette_name,
    bg_color,
    brightness,
    contrast,
    sharpness,
    gamma,
    black_cutoff,
    glow,
    scanline_strength,
    ascii_set,
    invert,
):
    img = img.convert("L")

    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)

    arr = np.array(img).astype(np.float32) / 255.0
    arr = np.power(arr, gamma)
    img = Image.fromarray((arr * 255).astype(np.uint8))

    img = ImageEnhance.Sharpness(img).enhance(sharpness)

    aspect_ratio = img.height / img.width
    ascii_height = int(ascii_width * aspect_ratio * 0.50)

    img = img.resize((ascii_width, ascii_height))
    pixels = np.array(img)

    chars = ASCII_SETS[ascii_set]
    base_color = PALETTES[palette_name]

    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", font_size)

    char_width = int(font_size * 0.62)
    char_height = int(font_size * 0.95)

    canvas = Image.new(
        "RGB",
        (char_width * ascii_width, char_height * ascii_height),
        bg_color,
    )

    draw = ImageDraw.Draw(canvas)

    for y, row in enumerate(pixels):
        for x, pixel in enumerate(row):
            if pixel < black_cutoff:
                continue

            value = 255 - pixel if invert else pixel

            idx = int(value / 255 * (len(chars) - 1))
            char = chars[idx]

            strength = pixel / 255

            color = (
                int(base_color[0] * strength),
                int(base_color[1] * strength),
                int(base_color[2] * strength),
            )

            draw.text(
                (x * char_width, y * char_height),
                char,
                font=font,
                fill=color,
            )

    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    for y in range(0, canvas.height, 3):
        odraw.line(
            (0, y, canvas.width, y),
            fill=(0, 0, 0, scanline_strength),
        )

    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")

    blur = canvas.filter(ImageFilter.GaussianBlur(radius=1.4))
    canvas = Image.blend(canvas, blur, glow)

    return canvas


st.title("CRT ASCII Renderer")

uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

with st.sidebar:
    st.header("Controls")

    palette = st.selectbox("Palette", list(PALETTES.keys()))
    ascii_set = st.selectbox("ASCII Set", list(ASCII_SETS.keys()))

    ascii_width = st.slider("ASCII Width", 40, 260, 180)
    font_size = st.slider("Font Size", 5, 20, 8)

    brightness = st.slider("Brightness", 0.3, 3.0, 1.35)
    contrast = st.slider("Contrast", 0.3, 3.0, 1.15)
    sharpness = st.slider("Sharpness", 0.3, 4.0, 2.2)
    gamma = st.slider("Gamma", 0.25, 1.5, 0.72)

    black_cutoff = st.slider("Black Cutoff", 0, 160, 55)
    glow = st.slider("Glow", 0.0, 0.6, 0.12)
    scanline_strength = st.slider("Scanlines", 0, 120, 35)

    invert = st.checkbox("Invert ASCII mapping", False)

    bg_choice = st.selectbox("Background", ["black", "dark green", "dark blue", "dark pink"])

    bg_map = {
        "black": (0, 0, 0),
        "dark green": (0, 5, 0),
        "dark blue": (0, 0, 8),
        "dark pink": (8, 0, 5),
    }

if uploaded:
    img = Image.open(uploaded)

    result = render_ascii(
        img=img,
        ascii_width=ascii_width,
        font_size=font_size,
        palette_name=palette,
        bg_color=bg_map[bg_choice],
        brightness=brightness,
        contrast=contrast,
        sharpness=sharpness,
        gamma=gamma,
        black_cutoff=black_cutoff,
        glow=glow,
        scanline_strength=scanline_strength,
        ascii_set=ascii_set,
        invert=invert,
    )

    st.image(result, caption="ASCII Output", use_container_width=True)

    result.save("ascii_output.png")

    with open("ascii_output.png", "rb") as f:
        st.download_button(
            "Download PNG",
            f,
            file_name="ascii_output.png",
            mime="image/png",
        )