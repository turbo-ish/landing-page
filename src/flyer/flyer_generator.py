#flyer_generator.py

import svgwrite

def create_flyer(output_file="flyer_a5.svg"):
    width_mm, height_mm = 148, 210  
    dwg = svgwrite.Drawing(output_file, size=(f"{width_mm}mm", f"{height_mm}mm"),
                           viewBox=f"0 0 {width_mm} {height_mm}")


    dwg.save()
    printf("flyer generated : {output_file}")

if __name__ == "__main__":
    create_flyert()
