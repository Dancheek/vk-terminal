import curses

import vk as vk_api
import conversations


class VKApp:
    def __init__(self):
        self.vk_s = vk_api.interactive_log_in()
        self.vk = self.vk_s.get_api()

        self.screen = curses.initscr()

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.screen.keypad(1)
        curses.mousemask(curses.ALL_MOUSE_EVENTS)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE + 8, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE + 8, curses.COLOR_RED + 8)
        curses.init_pair(3, curses.COLOR_WHITE + 8, curses.COLOR_BLACK + 8)
        curses.init_color(0, 145, 145, 145)

        self.style_highlighted = curses.color_pair(1) | curses.A_REVERSE
        self.style_title = curses.color_pair(1)
        self.style_statusline = curses.color_pair(2)
        self.style_hovered = curses.color_pair(3)

        self.height, self.width = self.screen.getmaxyx()

        self.mx, self.my = -1, -1
        self.bstate = 0

        self.statusline_text = ''
        self.last_statusline_style = self.style_statusline

        self.conversations = conversations.Conversations(self.height, 50, self, 0, 0)
        self.activity = self.conversations


    def getmouse(self):
        return self.mx, self.my, self.bstate


    def show_message(self, text, style=None):
        if style is not None:
            self.last_statusline_style = style
        self.statusline_text = text


    def update(self):
        try:
            self.activity.update()
        except:
            pass
        if self.statusline_text:
            self.screen.addstr(0, 0, f'{self.statusline_text:^{self.width}}', self.last_statusline_style)


    def handle(self, event):
        _, mx, my, _, self.bstate = curses.getmouse()
        if mx != -1 and my != -1:
            self.mx = mx
            self.my = my

        if event == curses.KEY_RESIZE:
            self.height, self.width = self.screen.getmaxyx()
            self.activity.resize(self.height, self.width)
            curses.curs_set(0)
        self.activity.handle(event)


    def run(self):
        event = 0
        self.screen.nodelay(True)
        while True:
            self.screen.erase()
            self.handle(event)
            self.update()
            self.screen.refresh()
            curses.delay_output(20)
            event = self.screen.getch()



if __name__ == '__main__':
    vk_app = VKApp()
    vk_app.run()

