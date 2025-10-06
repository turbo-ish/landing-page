# src/qr_svg.py
import base64
import string
from io import BytesIO
from pathlib import Path

import qrcode
import qrcode.image.svg
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer


def make_qr_border_svg(qr_id: int, top_text: str, bottom_text: str, lang: str, size_px=850, ring_radius=310, ring_width=50,
                       top_font_px=60, bottom_font_px=60, text_color="#000000",
                        gap_top=60, gap_bottom=20) -> string :
    cx = cy = size_px / 2
    r = ring_radius
    r_text_top = r + (ring_width / 2) + gap_top
    r_text_bottom = r + (ring_width / 2) + gap_bottom

    ring_arc_top    = f"M {cx - r},{cy} a {r},{r} 0 0 0 {2*r},0"
    ring_arc_bottom = f"M {cx - r},{cy} a {r},{r} 0 0 1 {2*r},0"
    text_arc_top    = f"M {cx - r_text_top},{cy} a {r_text_top},{r_text_top} 0 0 0 {2*r_text_top},0"
    text_arc_bottom = f"M {cx - r_text_bottom},{cy} a {r_text_bottom},{r_text_bottom} 0 0 1 {2*r_text_bottom},0"

    data = "https://movetogether.now/" + lang + "/" + str(qr_id)

    page_code = qrcode.main.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        version=8,
        box_size=8,
        border=0
    )
    page_code.add_data(data)

    page_code.make(fit=True)

    img = page_code.make_image(
        image_factory=StyledPilImage,
        eye_drawer=RoundedModuleDrawer(radius_ratio=1),
        module_drawer=CircleModuleDrawer(),
        color_mask = RadialGradiantColorMask(back_color=(255, 255, 255), center_color=(176, 0, 0), edge_color=(249, 115, 6))
    )

    qr_width = img.pixel_size

    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    with open("static/logo_round.png", "rb") as image_file:
        image_data = image_file.read()
    image_base64 = base64.b64encode(image_data).decode('utf-8')

    logo_size = qr_width / 2

    font = None
    with open('static/custom_font.txt', 'r') as f:
        font = f.read()

    svg_code = f'''
    <svg xmlns="http://www.w3.org/2000/svg" width="{size_px}" height="{size_px}" viewBox="0 0 {size_px} {size_px}">
        <style>
          @font-face {{
            font-family: 'CustomFont';
            src: url({font}) format('opentype');
          }}
          text {{
              font-family: 'CustomFont', sans-serif;
              fill: #800000
          }}
        </style>
        <defs>
            <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%"   stop-color="#B00000"/>  
              <stop offset="40%"  stop-color="#FF0000"/>   
              <stop offset="70%"  stop-color="#FF4500"/>   
              <stop offset="100%" stop-color="#F97306"/>   
            </linearGradient>
            <path id="ringTop" d="{ring_arc_top}"/>
            <path id="ringBottom" d="{ring_arc_bottom}"/>
            <path id="textTop" d="{text_arc_top}"/>
            <path id="textBottom" d="{text_arc_bottom}"/>
        </defs>

        <rect width="100%" height="100%" fill="white"/>

        <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#ringGrad)" stroke-width="{ring_width}"/>
  
        

        <text font-size="{top_font_px}" font-family="'Matches Schedule', sans-serif" font-weight="500" letter-spacing="1.2" fill="{text_color}">
            <textPath href="#textTop" startOffset="50%" text-anchor="middle">{top_text}</textPath>
        </text>

        <text font-size="{bottom_font_px}" font-family="'Matches Schedule', sans-serif" font-weight="500" letter-spacing="1.2" fill="{text_color}">
            <textPath href="#textBottom" startOffset="50%" text-anchor="middle">{bottom_text}</textPath>
        </text>
  
        <image href="data:image/jpeg;charset=utf-8;base64,{img_base64}" x="{cx - qr_width/2}" y="{cy - qr_width/2}" />
  
        <image x="{cx - logo_size / 2}" y="{cy - logo_size / 2}" width="{logo_size}" height="{logo_size}" href="data:image/png;base64,{image_base64}" />
    </svg>
    '''

    return svg_code

if __name__ == "__main__":
    svg = make_qr_border_svg(1)
    Path("qr_border.svg").write_text(svg, encoding="utf-8")

