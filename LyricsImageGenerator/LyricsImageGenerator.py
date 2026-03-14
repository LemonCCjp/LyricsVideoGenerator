from PIL import Image, ImageDraw, ImageFont
import math
from io import BytesIO


class Templates:
    def __init__(self):
        self.socialism = {
            "background_color": "#d30000",
            "font_path": fr"fonts/KCC-KP-CheongPong-Bold-KP-2011KPS.ttf",
            "title_background_color": "#f05354",
        }

        self.capitalism = {
            "background_color": "#0000c9",
            "font_path": fr"fonts/NotoSerifKR-VF.ttf",
            "title_background_color": "#004ce6",
        }

        self.imperialism = {
            "background_color": "#5f9131",
            "font_path": fr"fonts/NanumHumanBold.otf",
            "title_background_color": "#8db46a",
        }

templates = Templates()

async def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


async def create_solid_image(hex_color, filename="output.png"):
    width = 1920
    height = 1080
    
    rgb = hex_to_rgb(hex_color)
    
    img = Image.new("RGB", (width, height), rgb)
    img.save(filename)
    return img


async def create_title_background_image(hex_color, filename="output.png"):
    width = 1610
    height = 400
    
    rgb = hex_to_rgb(hex_color)
    
    img = Image.new("RGB", (width, height), rgb)
    img.save(filename)
    return img


async def imageToFile(img):
    buffer = BytesIO()
    img.save(buffer, "png")
    buffer.seek(0)
    return buffer


async def create_italic_text_image(
    img, 
    bg_hex,
    text,
    font,
    text_hex="#FFFFFF",
    outline_hex="#000000",
    outline_width=3,
    italic_angle=15,  # ← 斜体角度（おすすめ10〜20）
    filename="italic_text.png",
    text_position = (0,0)
):
    width = 1610
    height = 400

    bg_color = hex_to_rgb(bg_hex)
    text_color = hex_to_rgb(text_hex)
    outline_color = hex_to_rgb(outline_hex)

    # 背景
    bg = img

    # 文字を一旦透明画像に描く
    temp = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(temp)

    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=outline_width)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]


    draw.text(
        text_position,
        text,
        font=font,
        fill=text_color,
        stroke_width=outline_width,
        stroke_fill=outline_color,
        anchor="lm"
    )

    # 斜体変形
    shear = math.tan(math.radians(italic_angle))
    new_width = int(width + abs(shear) * height)

    italic = temp.transform(
        (new_width, height),
        Image.AFFINE,
        (1, shear, -shear * height / 2, 0, 1, 0),
        resample=Image.BICUBIC
    )

    # 背景に合成
    bg.paste(italic, (310, 340), italic)

    bg.save(filename)


async def draw_korean(img, texts, pattern=0, font_path=templates.socialism["font_path"]):
    positions = [
        {"x": 20, "y": 50},
        {"x": 20, "y": 320},
        {"x": 20, "y": 590},
        {"x": 20, "y": 860}
    ]

    draw = ImageDraw.Draw(img)

    x = positions[pattern]["x"]
    y = positions[pattern]["y"]

    font = font_path
    font = ImageFont.truetype(font, 80)

    draw.text((x, y), texts, font=font, fill="#FFFFFF", stroke_width=3, stroke_fill=f"#000000")
    return img


async def draw_japanese(img, texts, pattern=0):
    font = ImageFont.truetype(fr"fonts/NotoSerifJP-VF.ttf", 50)
    positions = [
        {"x": 20, "y": 150},
        {"x": 20, "y": 420},
        {"x": 20, "y": 690},
        {"x": 20, "y": 960}
    ]

    draw = ImageDraw.Draw(img)

    x = positions[pattern]["x"]
    y = positions[pattern]["y"]

    draw.text((x, y), texts, font=font, fill="#FFFF00", stroke_width=1, stroke_fill="#ffff00")
    return img


async def draw_lyricist(img, texts, font):
    draw = ImageDraw.Draw(img)

    draw.text((310, 750), f"작사:{texts}", font=font, fill="#FFFFFF", stroke_width=0, stroke_fill="#ffffFF")
    return img


async def draw_composer(img, texts, font):
    draw = ImageDraw.Draw(img)

    draw.text((310, 810), f"작곡:{texts}", font=font, fill="#FFFFFF", stroke_width=0, stroke_fill="#ffffFF")
    return img


async def draw_performer(img, texts, font):
    draw = ImageDraw.Draw(img)

    draw.text((310, 810), f"연주:{texts}", font=font, fill="#FFFFFF", stroke_width=0, stroke_fill="#ffffFF")
    return img


async def draw_texts(img, texts, font_path):
    for index, text in enumerate(texts):
        if index == 0:
            await draw_korean(img, text, 0, font_path)
        elif index == 1:
            await draw_japanese(img, text, 0)
        elif index == 2:
            await draw_korean(img, text, 1, font_path)
        elif index == 3:
            await draw_japanese(img, text, 1)
        elif index == 4:
            await draw_korean(img, text, 2, font_path)
        elif index == 5:
            await draw_japanese(img, text, 2)
        elif index == 6:
            await draw_korean(img, text, 3, font_path)
        elif index == 7:
            await draw_japanese(img, text, 3)
    return img


async def create_title_image(texts, background_color, font_path, title_background_color, ko_title_font_size, ja_title_font_size, lyricist=None, composer=None, performer=None):
    img = create_solid_image(background_color)
    title_image = await create_title_background_image(title_background_color)
    img.paste(title_image, (310, 340))

    font = ImageFont.truetype(font_path, ko_title_font_size)

    await create_italic_text_image(
        img,
        bg_hex="#1A1A40",
        text=texts[0],
        italic_angle=15,
        font=font,
        text_position=(0, 100)
    )

    font = ImageFont.truetype(fr"fonts/NotoSerifJP-VF.ttf", ja_title_font_size)

    await create_italic_text_image(
        img,
        bg_hex="#1A1A40",
        text=texts[1],
        italic_angle=15,
        font=font,
        text_hex="#FFFF00",
        outline_width=1,
        outline_hex="#FFFF00",
        text_position=(60, 300)
    )


    if not lyricist is None:
        font = ImageFont.truetype(font_path, 50)
        img = await draw_lyricist(img, lyricist, font)
    
    if not composer is None:
        font = ImageFont.truetype(font_path, 50)
        img = await draw_composer(img, composer, font)

    if not performer is None:
        font = ImageFont.truetype(font_path, 50)
        img = await draw_performer(img, performer, font)

    return imageToFile(img)


async def create_lyrics_image(texts, background_color, font_path):
    img = await create_solid_image(background_color)
    img = await draw_texts(img, texts, font_path)
    
    img.save("output.png") 

    return imageToFile(img)