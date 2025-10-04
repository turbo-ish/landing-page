from bisect import insort
from io import BytesIO

import qrcode
import svgwrite
from pathlib import Path
import base64
import mimetypes
from urllib.parse import quote

from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer


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

def add_svg(dwg, path: Path, insert, size, opacity=0.15):
    uri = data_uri_from_file(path)
    img = dwg.image(href=uri, insert=insert, size=size)
    img.attribs["preserveAspectRatio"] = "xMidYMid meet"
    if opacity != 1.0:
        img.update({"opacity": opacity})
    return img

def create_flyer(lang: str, qr_id: int, output_file="flyer_a5.svg"):
    width_mm, height_mm = 148, 210
    base = Path("assets")

    font = None
    with open('custom_font.txt', 'r') as f:
        font = f.read()

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
        color_mask=RadialGradiantColorMask(back_color=(255, 255, 255), center_color=(176, 0, 0),
                                           edge_color=(249, 115, 6))
    )

    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    dwg = svgwrite.Drawing(output_file, size=(f"{width_mm}mm", f"{height_mm}mm"),
                           viewBox=f"0 0 {width_mm} {height_mm}")

    dwg.embed_stylesheet(f'''
                        @font-face {{
                            font-family: 'CustomFont';
                            src: url({font}) format('opentype');
                        }}
                        ''')

    dwg.add(dwg.rect(insert=(0, 0), size=(width_mm, height_mm), fill="white"))

    athletes = dwg.g(id="athletes", opacity=1)

    for i in range(0, 3):
        athletes.add(add_svg(dwg, base/"sports"/"soccer.svg",
                             insert=(width_mm/2 - 15, height_mm/2 - 95 + 80 * i), size=(40, 40)))
        athletes.add(add_svg(dwg, base/"sports"/"runner.svg",
                             insert=(width_mm/2 - 65, height_mm/2 - 95 + 80 * i), size=(40, 40)))
        athletes.add(add_svg(dwg, base/"sports"/"bicycle.svg",
                             insert=(width_mm/2 - 65, height_mm/2 - 55 + 80 * i), size=(40, 40)))
        athletes.add(add_svg(dwg, base/"sports"/"fitness.svg",
                             insert=(width_mm/2 - 15, height_mm/2 - 55 + 80 * i), size=(40, 40)))
        athletes.add(add_svg(dwg, base/"sports"/"tennisplayer.svg",
                             insert=(width_mm/2 + 30, height_mm/2 - 55 + 80 * i), size=(40, 40)))
        athletes.add(add_svg(dwg, base/"sports"/"basketplayer.svg",
                             insert=(width_mm/2 + 30 , height_mm/2 - 100 + 80 * i), size=(40, 40)))

    dwg.add(athletes)

    title = "MOVE TOGETHER"
    subtitle = ".NOW"

    #promotion = ("Find Sports Buddies! Interested in connecting with others for sports activities? "
    #             "We want to build an App for this!")

    promotion = ["🏃‍♀️ The app that makes finding a sports buddy easy! 🏀",
                 "",
                 "Ever wanted to play tennis, football, or go hiking but couldn’t ",
                 "find anyone to join?",
                 "",
                 "MoveTogether.now is a digital platform (launching soon!) ",
                 "that connects you with people nearby who want to play ",
                 "the same sport, at your skill level, at the time that works ",
                 "for you.",
                 "",
                 "✨ Why you’ll love it:",
                 "✅ Huge variety of sports to choose from",
                 "✅ Meet at parks, courts, and outdoor spots — ",
                 "no gym membership needed",
                 "✅ Match by activity, location, time, and skill level",
                 "✅ Create or join activities with just a few taps",
                 "",
                 "🚀 Be the first to join!",
                 "👉 Scan the QR code, take our short survey and get early",
                 " access updates."
                 ]

    x, y = width_mm/2, height_mm/2 - 80
    style = "letter-spacing:1px; word-spacing:6px;"
    shadow = "#eeeeee"
    color = "#E67342"

    off = 3
    #dwg.add(dwg.text(title, insert=(x+off, y+off), text_anchor="middle",
    #                 font_size="15px", font_family="CustomFont, sans-serif",
    #                 font_style="italic", fill=shadow))

    dwg.add(dwg.text(title, insert=(x, y), text_anchor="middle",
                    font_size="15px", font_family="CustomFont, sans-serif",
                      font_style="italic", fill=color))

    #dwg.add(dwg.text(subtitle, insert=(x+off, y+off + 15), text_anchor="middle",
    #                 font_size="15px", font_family="CustomFont, sans-serif",
    #                 font_style="italic", fill=shadow))

    dwg.add(dwg.text(subtitle, insert=(x, y + 15), text_anchor="middle",
                        font_size="15px", font_family="CustomFont, sans-serif",
                        font_style="italic", fill=color))

    for i, line in enumerate(promotion):
        x_shift = 10
        if 11 <= i <= 15 or i == 19:
            x_shift = 16
        if i==13:
            x_shift = 23
        dwg.add(dwg.text(line, insert=(x_shift, 50 + 5 * i), font_size="4.2px",
                         font_family="Montserrat, sans-serif", font_weight="500"))

    halo_w, halo_h = 34, 34
    halo_x, halo_y = width_mm/2 - halo_w/2, 160

    logo_w, logo_h = 20, 20
    logo_x, logo_y = width_mm/2 - logo_w/2, halo_y + (halo_h - logo_h)/2

    qr_width = 50
    dwg.add(dwg.image(href=f'''data:image/jpeg;charset=utf-8;base64,{img_base64}''', x=x - qr_width / 2,
                      y=logo_y + logo_w / 2 - qr_width / 2, width=50))

    logo_uri = data_uri_from_file(base/"logos"/"logo_round.png")
    logo = dwg.image(href=logo_uri, insert=(logo_x, logo_y), size=(logo_w, logo_h))
    logo.attribs["preserveAspectRatio"] = "xMidYMid meet"
    dwg.add(logo)

    dwg.save()
    print(f"flyer generated : {output_file}")

if __name__ == "__main__":
    create_flyer(lang="en", qr_id=1)
