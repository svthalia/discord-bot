class RGB:
    def __init__(self, red: int, green: int, blue: int):
        self.red = red
        self.green = green
        self.blue = blue
        self.rgb = (red, green, blue)


class CMYK:
    def __init__(self, cyan: int, magenta: int, yellow: int, key: int):
        self.cyan = cyan
        self.magenta = magenta
        self.yellow = yellow
        self.key = key
        self.cmyk = (cyan, magenta, yellow, key)


class Colour:
    def __init__(self, name: str, hexadecimal: int, rgb: RGB, cmyk: CMYK):
        self.name = name
        self.hexadecimal = hexadecimal
        self.rgb = rgb
        self.cmyk = cmyk


class ThaliaColours:
    # from https://thalia.nu/members/styleguide/
    BLACK = Colour("Black", 0x000000, RGB(0, 0, 0), CMYK(91, 79, 62, 92))

    WHITE = Colour("White", 0xFFFFFF, RGB(255, 255, 255), CMYK(0, 0, 0, 0))

    MAGENTA = Colour("Magenta", 0xE62272, RGB(230, 24, 114), CMYK(0, 94, 21, 0))
