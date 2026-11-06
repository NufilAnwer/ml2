"""
Generate High-Fidelity Authentic Assets for VisionGuard Report
Outputs to: report_assets_v2/
"""

import os
import sys
import subprocess
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = "report_assets_v2"
os.makedirs(OUT_DIR, exist_ok=True)

# Path to system font
FONT_PATH = "C:/Windows/Fonts/consola.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/consolab.ttf"
SANS_FONT_PATH = "C:/Windows/Fonts/segoeui.ttf"
SANS_BOLD_PATH = "C:/Windows/Fonts/segoeuib.ttf"

def get_font(size=14, bold=False):
    p = FONT_BOLD_PATH if bold else FONT_PATH
    if os.path.exists(p):
        return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def get_sans(size=13, bold=False):
    p = SANS_BOLD_PATH if bold else SANS_FONT_PATH
    if os.path.exists(p):
        return ImageFont.truetype(p, size)
    return ImageFont.load_default()

# ════════════════════════════════════════════════════════════════════════════
# 1. VS Code Integrated Terminal Screenshot Generator
# ════════════════════════════════════════════════════════════════════════════
def render_vscode_terminal(lines, filename, width=960, prompt_dir="C:\\Users\\hassa\\OneDrive\\Desktop\\MLL"):
    """
    Renders an authentic VS Code dark theme integrated terminal screenshot.
    lines: list of (text, color_tuple_or_hex, bold_bool)
    """
    font = get_font(14)
    font_bold = get_font(14, bold=True)
    ui_font = get_sans(12)
    ui_font_bold = get_sans(12, bold=True)

    header_h = 36
    line_h = 22
    pad_x = 18
    pad_y = 12

    total_h = header_h + pad_y * 2 + len(lines) * line_h + 8

    img = Image.new("RGB", (width, total_h), "#181818")
    d = ImageDraw.Draw(img)

    # 1. Top Tabs Bar (#1f1f1f)
    d.rectangle([0, 0, width, header_h], fill="#1f1f1f")
    d.line([0, header_h, width, header_h], fill="#2b2b2b", width=1)

    tabs = ["PROBLEMS", "OUTPUT", "DEBUG CONSOLE", "TERMINAL", "PORTS"]
    tx = 16
    for t in tabs:
        if t == "TERMINAL":
            d.text((tx, 10), t, font=ui_font_bold, fill="#ffffff")
            tw = d.textlength(t, font=ui_font_bold)
            d.line([tx, header_h - 2, tx + tw, header_h - 2], fill="#0078d4", width=2)
        else:
            d.text((tx, 10), t, font=ui_font, fill="#858585")
            tw = d.textlength(t, font=ui_font)
        tx += tw + 20

    # Right icons on tab bar
    term_tag = "1: pwsh"
    tt_w = d.textlength(term_tag, font=ui_font)
    d.text((width - tt_w - 55, 10), term_tag, font=ui_font, fill="#cccccc")
    d.text((width - 40, 10), "+  v  x", font=ui_font, fill="#858585")

    # 2. Terminal Output Content
    y = header_h + pad_y
    for item in lines:
        if isinstance(item, str):
            text = item
            color = "#cccccc"
            is_bold = False
        elif len(item) == 2:
            text, color = item
            is_bold = False
        else:
            text, color, is_bold = item

        f = font_bold if is_bold else font
        d.text((pad_x, y), text, font=f, fill=color)
        y += line_h

    # Subtle border around image
    d.rectangle([0, 0, width - 1, total_h - 1], outline="#2b2b2b", width=1)

    out_path = os.path.join(OUT_DIR, filename)
    img.save(out_path, quality=95)
    print(f"  [OK] Saved terminal: {out_path}")
    return out_path


# ════════════════════════════════════════════════════════════════════════════
# 2. Browser Window Screenshot Frame Generator
# ════════════════════════════════════════════════════════════════════════════
def add_browser_chrome(viewport_img_path, output_filename, url="http://127.0.0.1:5000", title="VisionGuard - AI vs Real Image Classification"):
    """
    Wraps a webpage screenshot in an authentic Windows Chrome browser frame.
    """
    vp = Image.open(viewport_img_path)
    vp_w, vp_h = vp.size

    chrome_top_h = 75
    total_w = vp_w
    total_h = vp_h + chrome_top_h

    canvas_img = Image.new("RGB", (total_w, total_h), "#202124")
    d = ImageDraw.Draw(canvas_img)

    ui_font = get_sans(12)
    ui_bold = get_sans(12, bold=True)
    sym_font = get_sans(14)

    # 1. Title / Tabs Bar (#202124)
    tab_w = 240
    d.rectangle([0, 0, total_w, 40], fill="#202124")

    # Active Tab (#323639)
    d.rectangle([10, 8, 10 + tab_w, 40], fill="#323639")
    # Tab title with shield icon
    d.text((24, 16), "🛡️  " + title[:28] + "...", font=ui_font, fill="#e8eaed")
    d.text((10 + tab_w - 22, 16), "x", font=ui_font, fill="#9aa0a6")

    # New tab button
    d.text((10 + tab_w + 12, 16), "+", font=sym_font, fill="#9aa0a6")

    # Window controls (Min, Max, Close)
    d.text((total_w - 100, 12), "—    □    ✕", font=sym_font, fill="#9aa0a6")

    # 2. Navigation / URL Bar (#323639)
    d.rectangle([0, 40, total_w, chrome_top_h], fill="#292a2d")

    # Nav buttons
    d.text((18, 48), "←   →   ↻", font=sym_font, fill="#9aa0a6")

    # Address bar pill
    addr_x1 = 120
    addr_x2 = total_w - 110
    d.rounded_rectangle([addr_x1, 44, addr_x2, 68], radius=12, fill="#202124", outline="#3c4043", width=1)
    d.text((addr_x1 + 14, 49), "🔒  " + url, font=ui_font, fill="#e8eaed")

    # Extension icons
    d.text((total_w - 95, 48), "★   🧩   ⋮", font=sym_font, fill="#9aa0a6")

    # Paste viewport
    canvas_img.paste(vp, (0, chrome_top_h))

    out_path = os.path.join(OUT_DIR, output_filename)
    canvas_img.save(out_path, quality=95)
    print(f"  [OK] Saved browser frame: {out_path}")
    return out_path


# ════════════════════════════════════════════════════════════════════════════
# 3. Clean Professional Matplotlib Plots (White Background)
# ════════════════════════════════════════════════════════════════════════════
def make_clean_plot(figsize=(7, 4.2)):
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial"]
    fig, ax = plt.subplots(figsize=figsize, facecolor="#ffffff")
    ax.set_facecolor("#ffffff")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#444444")
    ax.spines["bottom"].set_color("#444444")
    ax.grid(True, linestyle="--", alpha=0.4, color="#cccccc")
    return fig, ax

print("Assets generator framework loaded successfully.")
