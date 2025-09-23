# src/qr_svg.py
from pathlib import Path

def make_qr_border_svg(
    filename="qr_border.svg",
    size_px=1000,
    ring_radius=380,
    ring_width=50,
    top_text="movetogether.now",
    bottom_text="SCAN ME · DO SPORTS NOW",
    top_font_px=56,
    bottom_font_px=40,
    text_color="#000000",
    color_red="#FF0000",
    color_orange="#F97306",
    gap_top=50,
    gap_bottom=20
):
    cx = cy = size_px / 2
    r = ring_radius
    r_text_top = r + (ring_width / 2) + gap_top
    r_text_bottom = r + (ring_width / 2) + gap_bottom

    ring_arc_top    = f"M {cx - r},{cy} a {r},{r} 0 0 0 {2*r},0"
    ring_arc_bottom = f"M {cx - r},{cy} a {r},{r} 0 0 1 {2*r},0"
    text_arc_top    = f"M {cx - r_text_top},{cy} a {r_text_top},{r_text_top} 0 0 0 {2*r_text_top},0"
    text_arc_bottom = f"M {cx - r_text_bottom},{cy} a {r_text_bottom},{r_text_bottom} 0 0 1 {2*r_text_bottom},0"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
  width="{size_px}" height="{size_px}" viewBox="0 0 {size_px} {size_px}">
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

  <text font-size="{top_font_px}" font-family="Arial, sans-serif" font-weight="700" letter-spacing="1.2" fill="{text_color}">
    <textPath href="#textTop" startOffset="50%" text-anchor="middle">{top_text}</textPath>
  </text>

  <text font-size="{bottom_font_px}" font-family="Arial, sans-serif" font-weight="700" letter-spacing="1.2" fill="{text_color}">
    <textPath href="#textBottom" startOffset="50%" text-anchor="middle">{bottom_text}</textPath>
  </text>
</svg>'''

    Path(filename).write_text(svg, encoding="utf-8")
    print("svg generated:", filename)

if __name__ == "__main__":
    make_qr_border_svg()
