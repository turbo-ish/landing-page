import svgwrite
from pathlib import Path
import base64
import mimetypes
from urllib.parse import quote

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

def create_flyer(output_file="flyer_a5.svg"):
    width_mm, height_mm = 148, 210
    base = Path("assets")

    dwg = svgwrite.Drawing(output_file, size=(f"{width_mm}mm", f"{height_mm}mm"),
                           viewBox=f"0 0 {width_mm} {height_mm}")

    dwg.add(dwg.rect(insert=(0, 0), size=(width_mm, height_mm), fill="white"))

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

    title = "MOVE TOGETHER"
    x, y = width_mm/2, height_mm/2
    style = "letter-spacing:1px; word-spacing:6px;"
    shadow = "#eeeeee"
    color = "#E67342"

    for off in (3, 1):
        dwg.add(dwg.text(title, insert=(x+off, y+off), text_anchor="middle",
                         font_size="15px", font_family="Impact, Arial Black, sans-serif",
                         font_weight="bold", font_style="italic",
                         fill=shadow, style=style))

    dwg.add(dwg.text(title, insert=(x, y), text_anchor="middle",
                     font_size="15px", font_family="Impact, Arial Black, sans-serif",
                     font_weight="bold", font_style="italic",
                     fill=color, style=style))

    halo_w, halo_h = 34, 34
    halo_x, halo_y = width_mm/2 - halo_w/2, 160
    dwg.add(dwg.rect(insert=(halo_x, halo_y), size=(halo_w, halo_h),
                     rx=8, ry=8, fill="white", opacity=0.9))

    logo_w, logo_h = 70, 70
    logo_x, logo_y = width_mm/2 - logo_w/2, halo_y + (halo_h - logo_h)/2
    logo_uri = data_uri_from_file(base/"logos"/"logo_round_2.png")
    logo = dwg.image(href=logo_uri, insert=(logo_x, logo_y), size=(logo_w, logo_h))
    logo.attribs["preserveAspectRatio"] = "xMidYMid meet"
    dwg.add(logo)

    dwg.save()
    print(f"flyer generated : {output_file}")

if __name__ == "__main__":
    create_flyer()
