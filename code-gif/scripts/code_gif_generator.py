#!/usr/bin/env python3
import sys
import os
from PIL import Image, ImageDraw, ImageFont

def draw_mac_window(d, width, height):
    d.rectangle([0, 0, width, 40], fill=(45, 45, 45))
    d.ellipse([15, 12, 29, 26], fill=(255, 95, 86)) # Red
    d.ellipse([35, 12, 49, 26], fill=(255, 189, 46)) # Yellow
    d.ellipse([55, 12, 69, 26], fill=(39, 201, 63)) # Green

def create_gif(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Slides separated by "---SLIDE---"
    slides = content.split("---SLIDE---")
    texts = [s.strip() for s in slides if s.strip()]
    
    if not texts:
        print("No slides found in input file.")
        sys.exit(1)

    frames = []
    width, height = 1200, 800
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    for text in texts:
        img = Image.new('RGB', (width, height), color=(30, 30, 30))
        d = ImageDraw.Draw(img)
        draw_mac_window(d, width, height)
        # Formatting
        text = text.replace("✓", "[OK]")
        d.text((30, 60), text, fill=(200, 200, 200), font=font)
        frames.append(img)
        
    frames[0].save(output_file, save_all=True, append_images=frames[1:], duration=2000, loop=0)
    print(f"GIF successfully generated at {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python code_gif_generator.py <input_frames.txt> <output.gif>")
        sys.exit(1)
    create_gif(sys.argv[1], sys.argv[2])
