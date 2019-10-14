import curses

from activity import Activity


class Conversations(Activity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.conversations = []
        self.messages = []

        self.hovered = -1
        self.selected = -1
        self.scroll_offset = 0

        vk = self.root.vk

        chats = {}
        users = []
        groups = []
        cons = vk.messages.get_conversations()['items']

        for con in cons:
            type = con['conversation']['peer']['type']
            if type == 'chat':
                chats[con['conversation']['peer']['id']] = con['conversation']['chat_settings']['title']
                self.conversations.append(con['conversation']['chat_settings']['title'])
            elif type == 'user':
                users.append(con['conversation']['peer']['id'])
                self.conversations.append(con['conversation']['peer']['id'])
            elif type == 'group':
                groups.append(con['conversation']['peer']['id'])
                self.conversations.append(con['conversation']['peer']['id'])
            self.messages.append(con['last_message']['text'])


        user_list = vk.users.get(user_ids=','.join(str(i) for i in users))
        users = {}

        for user in user_list:
            name = f'{user["first_name"]} {user["last_name"]}'
            users[user['id']] = name

        group_list = vk.groups.get_by_id(group_ids=','.join(str(-i) for i in groups))
        groups = {}

        for group in group_list:
            groups[group['id']] = group['name']

        for i, con in enumerate(self.conversations):
            if isinstance(con, int):
                if con < 0:
                    self.conversations[i] = groups[-self.conversations[i]]
                else:
                    self.conversations[i] = users[self.conversations[i]]

        for i, msg in enumerate(self.messages):
            if '\n' in msg:
                self.messages[i] = msg.replace('\n', ' ')


    def display_conversation(self, index, x=0, y=0, style=None):
        if style == 'hovered':
            style1 = style2 = style3 = self.root.style_hovered
        elif style == 'selected':
            style1 = style2 = style3 = self.root.style_highlighted
        else:
            style1 = style3 = curses.color_pair(0)
            style2 = self.root.style_title

        title = self.conversations[index]
        message = self.messages[index]
        if 0 <= y < self.height:
            self.addstr(y, x, ' ' * self.width, style1)
        if 0 <= y + 1 < self.height:
            self.addstr(y + 1, x, '  ' + title + ' ' * (self.width - len(title) - 2), style2)
        if 0 <= y + 2 < self.height:
            if len(message) > self.width - 3:
                self.addstr(y + 2, x, '  ' + message[:self.width-7] + '...  ', style3)
            else:
                self.addstr(y + 2, x, '  ' + message + ' ' * (self.width - len(message) - 2), style3)


    def resize(self, height, width):
        self.height = height


    def scroll_up(self, offset=1):
        self.scroll_offset -= offset
        self.scroll_offset = max(0, self.scroll_offset)


    def scroll_down(self, offset=1):
        self.scroll_offset += offset
        self.scroll_offset = min(len(self.conversations) * 3 - self.height + 1, self.scroll_offset)


    def handle(self, event):
        mx, my, bstate = self.root.getmouse()
        if self.x <= mx < self.x + self.width and self.y <= my < self.y + self.height:
            self.hovered = (my + self.scroll_offset) // 3

        if event == curses.KEY_LEFT:
            self.width -= 1
        elif event == curses.KEY_RIGHT:
            self.width += 1

        elif event == curses.KEY_DOWN:
            self.hovered += 1
            self.hovered = min(len(self.conversations)-1, self.hovered)
            if (self.hovered + 2) * 3 - self.scroll_offset > self.height:
                self.scroll_down((self.hovered + 2) * 3 - self.scroll_offset - self.height)

        elif event == curses.KEY_UP:
            self.hovered -= 1
            self.hovered = max(0, self.hovered)
            if (self.hovered - 1) * 3 - self.scroll_offset < 0:
                self.scroll_up(self.scroll_offset - (self.hovered - 1) * 3)

        elif event == 27: # ESC
            pass
        elif event == ord('\n'):
            self.selected = self.hovered

        elif event == curses.KEY_MOUSE:
            mx, my, bstate = self.root.getmouse()
            if self.x <= mx < self.x + self.width and self.y <= my < self.y + self.height:
                if bstate & curses.BUTTON1_CLICKED:
                    self.selected = (my + self.scroll_offset) // 3
                elif bstate & curses.BUTTON4_PRESSED: # scroll up
                    self.scroll_up()
                elif bstate & 2**21: # scroll down
                    self.scroll_down()

        elif event == ord('k'):
            self.scroll_up()
        elif event == ord('j'):
            self.scroll_down()

        elif event == ord(' '):
            self.root.show_message(str(bin(curses.REPORT_MOUSE_POSITION)))
        elif event == ord('c'):
            self.root.show_message('')


    def update(self):
        count = len(self.conversations)
        visible_start = self.scroll_offset // 3
        visible_end = (self.height + self.scroll_offset) // 3
        for i in range(visible_start, visible_end + 1):
        #for i, con in enumerate(self.conversations):
            #if (i*3 - self.scroll_offset >= self.height):
            #    break

            if i == self.selected:
                self.display_conversation(i, y=i*3-self.scroll_offset, style='selected')
            elif i == self.hovered:
                self.display_conversation(i, y=i*3-self.scroll_offset, style='hovered')
            else:
                self.display_conversation(i, y=i*3-self.scroll_offset)

