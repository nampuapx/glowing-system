
class Peak:
    red = 0
    green = 0
    blue = 0
    rgb = 0

    def __init__(self, rgb, r, g, b):
        self.red = self.byte_normalise(r)
        self.green = self.byte_normalise(g)
        self.blue = self.byte_normalise(b)
        self.rgb = self.byte_normalise(rgb)

    @staticmethod
    def byte_normalise(byte):

        if byte < 0:
            return 0
        if byte > 255:
            return 255
        return byte

