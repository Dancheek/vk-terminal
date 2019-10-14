import curses


class Activity:
    def __init__(self, height, width, root, y=0, x=0):
        self.height = height
        self.width = width
        self.y = y
        self.x = x
        self.root = root

    def addstr(self, y, x, text, style=None):
        if style is None:
            self.root.screen.addstr(y, x, text)
        else:
            self.root.screen.addstr(y, x, text, style)

    def resize(self, height, width):
        self.height = height
        self.width = width

    def update(self):
        pass

    def handle(self, event):
        pass
