# %%
import json
from pprint import pprint
import os
import io

import numpy as np

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import SquareModuleDrawer, GappedSquareModuleDrawer, CircleModuleDrawer, RoundedModuleDrawer, VerticalBarsDrawer, HorizontalBarsDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import letter

from vcard_def import VCard2_1, vname, tel, adr

if __name__ == "__main__":
    cards = [fname for fname in os.listdir(
        "cards") if fname.endswith(".vc21.json")]

    card_data = {}
    card_objs = {}

    for card in cards:
        try:
            with open(f"cards/{card}", "r") as f:
                card_data[card] = json.load(f)
            card_objs[card] = VCard2_1(**card_data[card])
        except Exception as e:
            print(f"Error loading card {card}: {e}")

    # prompt selection of card
    prompt = "Select a card:"
    for i, card in enumerate(cards):
        prompt += f"\n{i+1}: {card}"
    card_idx = int(input(prompt+"\nEnter card number: "))
    card = cards[card_idx-1]

    vc = card_objs[card]
    vc.update_rev()

    qr = qrcode.QRCode()
    qr.add_data(str(vc))

    pprint(vc.pruned_dump())
    print("\n"+str(vc))

    f = io.StringIO()
    qr.print_ascii(out=f)
    f.seek(0)
    ascii_art = f.read()
    print(ascii_art)
    # %%

    drawer_type = "circle"
    drawer = {
        "square": SquareModuleDrawer(),
        "gapped_square": GappedSquareModuleDrawer(),
        "circle": CircleModuleDrawer(),
        "rounded": RoundedModuleDrawer(),
        "vertical_bars": VerticalBarsDrawer(),
        "horizontal_bars": HorizontalBarsDrawer(),
    }[drawer_type]

    img = qr.make_image(image_factory=StyledPilImage, module_drawer=drawer, color_mask=RadialGradiantColorMask(
        back_color=(255, 255, 255),
        center_color=(200, 140, 0),
        edge_color=(190, 100, 0)))

    # show image interactively
    # img.show()

    # save image
    if not os.path.exists("out"):
        os.mkdir("out")
    out_name = f"out/{card}.png"
    img.save(out_name)
    print(f"Saved QR code to {out_name}")

    # %%

    paper_shape = "letter"  # "letter" or "A4"
    add_tag_border = False
    rotation = 0  # number of 90 degree clockwise rotations

    paper_size = {
        "letter": letter,
        "A4": None
    }[paper_shape]

    code_size_mm = 40
    code_size = code_size_mm * mm

    pdf_name = f"out/{card}.pdf"
    canvas = Canvas(pdf_name, pagesize=paper_size, bottomup=0,)

    canv_w, canv_h = canvas._pagesize

    in_to_mm = 25.4

    dense_packing_layout = np.array([
        (0.7, 1),
        (0.7, 3.25),
        (0.7, 5.5),
        (0.7, 7.75),
        (4.5, 1),
        (4.5, 3.25),
        (4.5, 5.5),
        (4.5, 7.75),
    ])*in_to_mm*mm

    # sparse_centers = np.array([ #for avery labels
    #     (2.18,2),
    #     (2.18,5.3),
    #     (2.18,8.6),
    #     (4.25+2.1,2),
    #     (4.25+2.1,5.3),
    #     (4.25+2.1,8.6),
    # ])*in_to_mm*mm - np.array([(3.5, 2)]*6)*in_to_mm*mm/2

    upper_left_corners = dense_packing_layout

    card_h = 2*in_to_mm*mm
    card_w = 3.5*in_to_mm*mm

    code_padding = (card_h-code_size)/2

    for margin_x, margin_y in upper_left_corners:
        cen_x = margin_x + code_padding + code_size/2
        cen_y = margin_y + code_padding + code_size/2
        canvas.drawImage(out_name, margin_x+code_padding, margin_y+code_padding,
                         width=code_size, height=code_size,)

        # outline the tag
        canvas.setStrokeColorRGB(.5, .5, .5)
        canvas.setLineWidth(0.1)
        # add line to show square of the size of the paper sheet
        code_padding = (card_h-code_size)/2
        canvas.rect(margin_x, margin_y, card_w, code_size+2*code_padding)

        typeface = "Courier-Bold"

        text_color = (0, 0, 0)
        font_size = 4
        line_padding = 1.5
        text_margin_y = cen_y-len(str(vc).split("\n")) * \
            (font_size+line_padding)/2
        max_width = max([canvas.stringWidth(line, typeface, font_size)
                        for line in str(vc).split("\n")])
        text_margin_x = margin_x + card_w - code_padding - max_width - 5

        for i, line in enumerate(str(vc).split("\n")):
            canvas.setFont(typeface, font_size)
            text_obj = canvas.beginText(
                x=text_margin_x,
                y=text_margin_y+(i+1)*(font_size+line_padding) - line_padding)
            text_obj.setFillColorRGB(*text_color)
            text_obj.textOut(line)
            canvas.drawText(text_obj)

    # add another page with the same image
    canvas.showPage()

    canvas.save()

# %%
