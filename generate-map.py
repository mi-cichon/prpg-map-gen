from PIL import Image, ImageDraw, ImageFont
import json
import textwrap
import os

# === CONFIG ===
map_path = "map.png"
districts_json_path = "districts.json"
output_path = "custom_map.png"

font_path = "Fredoka-Bold.ttf"
font_size = 18
text_color = (229, 154, 0)
outline_color = (0, 0, 0)
outline_width = 1
wrap_limit = 8
line_spacing = 4

# === Load map and data ===
image = Image.open(map_path).convert("RGBA")
draw = ImageDraw.Draw(image)
font = ImageFont.truetype(font_path, font_size)

with open(districts_json_path, "r", encoding="utf-8") as f:
    districts = json.load(f)

# === Draw wrapped text with safe word wrapping ===
for district in districts:
    name = district["name"]
    x, y = district["x"], district["y"]

    lines = textwrap.wrap(
        name,
        width=wrap_limit,
        break_long_words=False,
        break_on_hyphens=False
    )

    total_height = len(lines) * (font_size + line_spacing)
    start_y = y - total_height // 2  # center vertically

    for i, line in enumerate(lines):
        text_width = font.getlength(line)  # get length of this line in pixels
        line_x = x - text_width / 2        # center horizontally
        line_y = start_y + i * (font_size + line_spacing)

        # Draw outline
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((line_x + dx, line_y + dy), line, font=font, fill=outline_color)

        # Draw main text
        draw.text((line_x, line_y), line, font=font, fill=text_color)

# === Save ===
image.save(output_path)
os.startfile(output_path)
print(f"✅ Saved wrapped labeled map to: {output_path}")
