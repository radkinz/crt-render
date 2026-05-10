from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter,
    ImageEnhance,
)

import numpy as np

# ============================================
# SETTINGS
# ============================================

INPUT_IMAGE = "abc.jpeg"
OUTPUT_IMAGE = "ascii_crt.png"

ASCII_CHARS = " .,:;i+*#%@"

ASCII_WIDTH = 220
FONT_SIZE = 7

# optional pixel font
# FONT_PATH = "fonts/Px437_IBM_VGA8.ttf"
FONT_PATH = None

UPSCALE_FACTOR = 3

BG_COLOR = (2, 10, 4)

PALETTE = "blue"   # "green", "blue", "amber", "white"
BLACK_CUTOFF = 60  # higher = more empty black space

PALETTES = {
    "green": (20, 170, 75),
    "blue": (40, 160, 255),
    "amber": (255, 170, 55),
    "white": (210, 230, 220),
    "pink": (255, 105, 180),
}

# ============================================
# LOAD IMAGE
# ============================================

img = Image.open(INPUT_IMAGE).convert("L")

# ============================================
# CROP
# ============================================

w, h = img.size

img = img.crop((
    int(w * 0.08),
    int(h * 0.02),
    int(w * 0.78),
    int(h * 0.92)
))

# ============================================
# IMAGE PROCESSING
# ============================================

# softer CRT look
img = img.filter(
    ImageFilter.GaussianBlur(radius=0.3)
)

img = ImageEnhance.Brightness(img).enhance(1.55)
img = ImageEnhance.Contrast(img).enhance(1.25)

# gamma correction
arr = np.array(img).astype(np.float32) / 255.0
arr = np.power(arr, 0.55)

img = Image.fromarray(
    (arr * 255).astype(np.uint8)
)

# sharpen details
img = ImageEnhance.Sharpness(img).enhance(2.2)

# ============================================
# RESIZE
# ============================================

aspect_ratio = img.height / img.width

ascii_height = int(
    ASCII_WIDTH * aspect_ratio * 0.50
)

img = img.resize(
    (ASCII_WIDTH, ascii_height)
)

pixels = np.array(img)

# ============================================
# ASCII CONVERSION
# ============================================

ascii_img = []
color_img = []

base_color = PALETTES[PALETTE]

for row in pixels:

    line = ""
    color_row = []

    for pixel in row:

        if pixel < BLACK_CUTOFF:
            line += " "
            color_row.append((0, 0, 0))
            continue

        idx = int(
                (255 - pixel) / 255
                * (len(ASCII_CHARS) - 1)
            )

        char = ASCII_CHARS[idx]
        line += char

        strength = pixel / 255

        color_row.append((
            int(base_color[0] * strength),
            int(base_color[1] * strength),
            int(base_color[2] * strength),
        ))

    ascii_img.append(line)
    color_img.append(color_row)
    
# ============================================
# FONT
# ============================================

if FONT_PATH:

    font = ImageFont.truetype(
        FONT_PATH,
        FONT_SIZE
    )

else:

    font = ImageFont.truetype(
        "/System/Library/Fonts/Menlo.ttc",
        FONT_SIZE
    )

char_width = int(FONT_SIZE * 0.62)
char_height = int(FONT_SIZE * 0.95)

canvas_width = char_width * ASCII_WIDTH
canvas_height = char_height * ascii_height

# ============================================
# CREATE CANVAS
# ============================================

canvas = Image.new(
    "RGB",
    (canvas_width, canvas_height),
    BG_COLOR
)

draw = ImageDraw.Draw(canvas)

# ============================================
# DRAW ASCII
# ============================================

for y, line in enumerate(ascii_img):

    for x, char in enumerate(line):

        draw.text(
            (
                x * char_width,
                y * char_height
            ),
            char,
            font=font,
            fill=color_img[y][x]
        )

# ============================================
# CRT SCANLINES
# ============================================

overlay = Image.new(
    "RGBA",
    canvas.size,
    (0, 0, 0, 0)
)

overlay_draw = ImageDraw.Draw(overlay)

for y in range(0, canvas.height, 3):

    overlay_draw.line(
        (
            0,
            y,
            canvas.width,
            y
        ),
        fill=(0, 0, 0, 35)
    )

canvas = Image.alpha_composite(
    canvas.convert("RGBA"),
    overlay
).convert("RGB")

# ============================================
# PHOSPHOR GLOW
# ============================================

blur = canvas.filter(
    ImageFilter.GaussianBlur(radius=1.2)
)

canvas = Image.blend(
    canvas,
    Image.new("RGB", canvas.size, (10, 18, 12)),
    0.08
)

# ============================================
# UPSCALE
# ============================================

canvas = canvas.resize(
    (
        canvas.width * UPSCALE_FACTOR,
        canvas.height * UPSCALE_FACTOR
    ),
    Image.NEAREST
)


# ============================================
# SAVE
# ============================================

canvas.save(OUTPUT_IMAGE)

print(f"saved -> {OUTPUT_IMAGE}")