class AcceptanceBox:
    length = 20.0
    width = 10.0
    height = 5.0

    def build(self):
        return Box(self.length, self.width, self.height, anchor=Anchor.BOTTOM)


AcceptanceBox()
