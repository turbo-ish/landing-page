import svgwrite
from pathlib import Path
import base64
import mimetypes
from urllib.parse import quote

PX_TO_MM = 0.264583  # 1px ≈ 0.264583 mm (96 dpi)

def data_uri_from_file(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.as_posix())
    if mime is None:
        mime = "image/png"
    if mime.endswith("svg+xml"):
        svg_text = path.read_text(encoding="utf-8")
        return "data:image/svg+xml;utf8," + quote(svg_text)
    else:
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{b64}"

def add_svg(dwg, path: Path, insert, size, opacity=1.0):
    uri = data_uri_from_file(path)
    img = dwg.image(href=uri, insert=insert, size=size)
    img.attribs["preserveAspectRatio"] = "xMidYMid meet"
    if opacity != 1.0:
        img.update({"opacity": opacity})
    return img

def _inject_custom_font_css(dwg, custom_font_txt: Path):
    font_url = custom_font_txt.read_text(encoding="utf-8").strip()
    css = f"""
    @font-face {{
      font-family: 'CustomFont';
      src: url({font_url}) format('opentype');
      font-display: swap;
    }}
    .title-text {{
      font-family: 'CustomFont', sans-serif;
      font-weight: 500;
      letter-spacing: 0.7px;
    }}
    """
    dwg.defs.add(dwg.style(css))

def create_flyer(output_file="flyer_a5.svg"):
    width_mm, height_mm = 148, 210
    base = Path("assets")

    dwg = svgwrite.Drawing(output_file, size=(f"{width_mm}mm", f"{height_mm}mm"),
                           viewBox=f"0 0 {width_mm} {height_mm}")

    # Fond
    dwg.add(dwg.rect(insert=(0, 0), size=(width_mm, height_mm), fill="white"))

    # ----- Décor: border1.svg plein format en arrière-plan -----
    border_path = base / "design" / "border1.svg"
    # Ajuste l'opacité si besoin (0.15–0.4 fonctionne bien)
    border_height_mm = 90
    border_img = add_svg(
        dwg,
        border_path,
        insert=(0, height_mm - border_height_mm + 10),
        size=(width_mm, border_height_mm),
        opacity=0.6
    )
    border_img.attribs["preserveAspectRatio"] = "xMidYMid slice"
    dwg.add(border_img)

    # -----------------------------------------------------------

    # Police Custom
    _inject_custom_font_css(dwg, Path("../custom_font.txt"))

    # Athlètes (inchangé)
    athletes = dwg.g(id="athletes", opacity=1)
    athletes.add(add_svg(dwg, base/"sports"/"soccer.svg",
                         insert=(width_mm/2 - 15, height_mm/2 - 95), size=(40, 40)))
    athletes.add(add_svg(dwg, base/"sports"/"runner.svg",
                         insert=(width_mm/2 - 65, height_mm/2 - 95), size=(40, 40)))
    athletes.add(add_svg(dwg, base/"sports"/"bicycle.svg",
                         insert=(width_mm/2 - 65, height_mm/2 - 55), size=(40, 40)))
    athletes.add(add_svg(dwg, base/"sports"/"fitness.svg",
                         insert=(width_mm/2 - 15, height_mm/2 - 55), size=(40, 40)))
    athletes.add(add_svg(dwg, base/"sports"/"tennisplayer.svg",
                         insert=(width_mm/2 + 30, height_mm/2 - 55), size=(40, 40)))
    athletes.add(add_svg(dwg, base/"sports"/"basketplayer.svg",
                         insert=(width_mm/2 + 30 , height_mm/2 - 100), size=(40, 40)))
    dwg.add(athletes)

    # Titre + logo
    title = "MOVE TOGETHER"
    center_y = height_mm / 2

    font_px = 13
    color = "#E67342"
    left_margin_mm = 6

    approx_char_width_px = 0.6 * font_px
    text_width_px = approx_char_width_px * len(title)
    text_width_mm = text_width_px * PX_TO_MM

    logo_scale = 8
    logo_h_mm = (font_px * logo_scale) * PX_TO_MM
    logo_w_mm = logo_h_mm
    gap_mm = 85

    x_text = left_margin_mm
    y_text = center_y
    x_logo = x_text + text_width_mm + gap_mm
    y_logo = center_y - (logo_h_mm / 2)

    dwg.add(dwg.text(
        title,
        insert=(x_text, y_text),
        text_anchor="start",
        dominant_baseline="middle",
        class_="title-text",
        font_size=f"{font_px}px",
        fill=color
    ))

    logo_uri = data_uri_from_file(base/"logos"/"logo_round_2.png")
    logo_img = dwg.image(href=logo_uri, insert=(x_logo, y_logo), size=(logo_w_mm, logo_h_mm))
    logo_img.attribs["preserveAspectRatio"] = "xMidYMid meet"
    dwg.add(logo_img)

    # QR au centre sous le bloc texte+logo
    qr_path = base / "qr" / "qr_border.svg"
    qr_size_mm = 60
    qr_x = (width_mm - qr_size_mm) / 2
    qr_y = y_text + logo_h_mm / 2   # espace de 12 mm sous le titre+logo
    qr_img = add_svg(dwg, qr_path, insert=(qr_x, qr_y), size=(qr_size_mm, qr_size_mm))
    dwg.add(qr_img)

    dwg.save()
    print(f"flyer generated : {output_file}")

if __name__ == "__main__":
    create_flyer()
