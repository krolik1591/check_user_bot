from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

path = Path(__file__).parent
base = Image.open(str(path / "template.png")).convert("RGBA")


def make_image(question, time):
    img = _make_image(question, time)
    iob = BytesIO()
    img.save(iob, format='png')
    return iob.getvalue()


def _make_image(question, time):
    txt = Image.new("RGBA", base.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)
    d.text((20, 16), "Загадка від Жака Фреско", font=fnt(32), fill=(255, 255, 255))
    d.text((50, 125), f"{question}\nСкіко?", font=fnt(52), fill=(255, 255, 255), align='center')
    d.text((10, 325), f"На роздум дається \n{time} секунд", font=fnt(25), fill=(255, 255, 255))
    out = Image.alpha_composite(base, txt)
    return out


def fnt(size):
    return ImageFont.truetype(str(path / "SourceCodePro-Medium.otf"), size)


if __name__ == "__main__":
    _make_image("2+3", 60).show()
