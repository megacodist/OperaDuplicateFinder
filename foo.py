from msvcrt import getwche
from PIL.ImageFont import FreeTypeFont
from tkinter.font import Font

from megacodist.fonts import installed_fonts_str
from megacodist.text import GetStringDimensions

def mmm( *m, /, *, mmm=23) -> slice:
    pass

if __name__ == '__main__':
    fonts = installed_fonts_str()
    widthSet = set()
    for font in fonts:
        font_ = Font(
            family=font,
            size=12
        )
        width_ = font_.measure('Megacodist')
        widthSet.add(width_)
    
    for result in widthSet:
        print(result)

    getwche()