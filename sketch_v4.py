# fashion_collage_designer.py
# 3 SKETCHES → 1×3 HORIZONTAL COLLAGE | STYLE-AWARE | PENCIL SKETCH
import os
import sys
import re
from pathlib import Path
from io import BytesIO
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN TWEAKS & KEYWORDS
# ─────────────────────────────────────────────────────────────────────────────
DESIGN_TWEAKS = {
    "indian_bridal": [
        "with delicate zari border and subtle pearl edging",
        "featuring hand-embroidered floral butta motifs on pallu",
        "accented with kundan work on the blouse neckline"
    ],
    "western_gown": [
        "with an elegant asymmetric hem and soft chiffon layering",
        "featuring a deep V-neck with illusion mesh",
        "with a cinched waist and flowing train"
    ],
    "casual_day": [
        "with playful ruffled sleeves and a cinched waist bow",
        "featuring a breezy cotton fabric with polka dot print",
        "with a flared midi skirt and side pockets"
    ],
    "cultural_traditional": [
        "with authentic regional embroidery in silk thread",
        "accented with a matching silk sash and minimal floral motif",
        "featuring traditional drape and modest neckline"
    ],
    "minimalist_modern": [
        "with clean lines and a sculpted square neckline",
        "featuring geometric laser-cut patterns on sleeves",
        "with a structured silhouette and hidden zipper"
    ],
    "bohemian": [
        "with delicate lace inserts and fringe hem detailing",
        "featuring layered earth-tone fabrics with bell sleeves",
        "in flowy maxi length with open back"
    ],
    "royal_princess": [
        "with a diamond-encrusted clasp and velvet cape trim",
        "featuring a crystal tiara and pearl drop earrings",
        "with hand-painted gold filigree along the hem"
    ],
    "roman_royal": [
        "with deep crimson silk and gold laurel leaf embroidery",
        "draped in classic toga style with purple trim",
        "with intricate SPQR embroidery on the hem"
    ]
}
TYPE_KEYWORDS = {
    "indian_bridal": ["indian", "lehenga", "saree", "sari", "bridal", "wedding", "anarkali"],
    "western_gown": ["gown", "evening", "cocktail", "prom", "ballgown", "formal"],
    "casual_day": ["casual", "summer", "day", "cotton", "midi", "sundress"],
    "cultural_traditional": ["kimono", "hanbok", "ao dai", "kebaya", "cheongsam", "traditional"],
    "minimalist_modern": ["minimal", "clean", "modern", "sleek", "structured", "monochrome"],
    "bohemian": ["boho", "bohemian", "flowy", "maxi", "hippie", "fringe"],
    "royal_princess": ["royal", "princess", "cinderella", "tiara", "palace"],
    "roman_royal": ["roman", "rome", "empire", "caesar", "king", "toga", "imperial", "spqr"]
}
_tweak_index = {}

# ─────────────────────────────────────────────────────────────────────────────
# SAFE COLLAGE NAMING
# ─────────────────────────────────────────────────────────────────────────────
def get_next_collage_filename() -> Path:
    out_dir = Path("./output")
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(r"^collage_(\d+)\.png$", re.IGNORECASE)
    max_num = 0
    for file in out_dir.iterdir():
        if file.is_file():
            match = pattern.match(file.name)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
    next_num = max_num + 1
    return out_dir / f"collage_{next_num}.png"

# ─────────────────────────────────────────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def build_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env")
    return genai.Client(api_key=api_key)

def detect_dress_type(prompt: str) -> str | None:
    lowered = prompt.lower()
    for dtype, keywords in TYPE_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return dtype
    return None

def get_next_tweak(dress_type: str) -> str:
    if not dress_type or dress_type not in DESIGN_TWEAKS:
        return ""
    tweaks = DESIGN_TWEAKS[dress_type]
    idx = _tweak_index.get(dress_type, 0) % len(tweaks)
    tweak = tweaks[idx]
    _tweak_index[dress_type] = idx + 1
    return tweak

def clean_prompt(user_prompt: str) -> str:
    clean = user_prompt.strip()
    prefixes = ["generate ", "create ", "make ", "an image of ", "a picture of ", "image of "]
    for p in prefixes:
        if clean.lower().startswith(p.lower()):
            clean = clean[len(p):].strip()
            break
    return clean

def build_sketch_prompt(base: str) -> str:
    dress_type = detect_dress_type(base)
    tweak = get_next_tweak(dress_type)
    enhanced = f"{base}, {tweak}" if tweak else base
    enhanced = f"{enhanced}, isolated on pure white background, no person, no model, no mannequin, just the garment, flat lay or hanging view"
    return (
        "PENCIL SKETCH ONLY. "
        "BLACK AND WHITE. "
        "NO COLOR. "
        "FASHION ILLUSTRATION. "
        "CLEAN LINES, DETAILED SHADING. "
        "NO PHOTO. "
        "MONOCHROME. "
        f"{enhanced}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# IMAGE GENERATION
# ─────────────────────────────────────────────────────────────────────────────
def generate_image(prompt: str) -> Image.Image | None:
    try:
        client = build_client()
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
        )
        for part in response.parts:
            if part.inline_data:
                return Image.open(BytesIO(part.inline_data.data))
    except Exception as e:
        print(f"Error: {e}")
    return None

# ─────────────────────────────────────────────────────────────────────────────
# 1×3 HORIZONTAL COLLAGE (3 variations only)
# ─────────────────────────────────────────────────────────────────────────────
def create_collage(images: list[Image.Image], title: str) -> Image.Image:
    if len(images) != 3:
        return None

    target_size = (520, 720)  # Balanced for 1×3
    margin = 50
    title_height = 80

    resized = [img.resize(target_size, Image.LANCZOS) for img in images]
    w, h = target_size

    collage_w = w * 3 + margin * 4
    collage_h = title_height + h + margin * 2

    collage = Image.new("RGB", (collage_w, collage_h), "white")
    draw = ImageDraw.Draw(collage)

    # Title
    try:
        font_title = ImageFont.truetype("arial.ttf", 44)
    except:
        font_title = ImageFont.load_default()
    title_w = draw.textlength(title, font=font_title)
    draw.text(((collage_w - title_w) // 2, 20), title, fill="black", font=font_title)

    # Paste 3 images
    y_start = title_height + margin
    labels = ["Variation 1", "Variation 2", "Variation 3"]
    for i, img in enumerate(resized):
        x = margin + i * (w + margin)
        collage.paste(img, (x, y_start))
        # Label below
        label_font = ImageFont.load_default()
        label_w = draw.textlength(labels[i], font=label_font)
        draw.text((x + (w - label_w) // 2, y_start + h + 8), labels[i], fill="gray", font=label_font)

    return collage

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("FASHION COLLAGE DESIGNER (1×3 – 3 Variations)")
    print("=" * 60)

    raw_prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("\nEnter dress prompt: ").strip()
    if not raw_prompt:
        print("No input. Exiting.")
        return

    dress_type = detect_dress_type(raw_prompt)
    style = dress_type.replace("_", " ").title() if dress_type else "General"
    title = f"{style} Dress - 3 Variations"

    print(f"\nStyle: {style}")
    print("Generating 3 sketch variations...\n")

    base_clean = clean_prompt(raw_prompt)
    sketches = []
    for i in range(3):  # Only 3
        prompt = build_sketch_prompt(base_clean)
        print(f"  → Variation {i+1}")
        img = generate_image(prompt)
        if img:
            sketches.append(img)
        else:
            print(f"  Failed variation {i+1}")

    if len(sketches) == 3:
        print("\nCreating 1×3 collage...")
        collage = create_collage(sketches, title)
        if collage:
            filename = get_next_collage_filename()
            collage.save(filename)
            print(f"\nCOLLAGE SAVED: {filename}")
        else:
            print("Failed to create collage.")
    else:
        print(f"\nOnly {len(sketches)} sketches generated. Need 3 for collage.")

if __name__ == "__main__":
    main()