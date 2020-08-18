import sys
import threading
import time
from multiprocessing.connection import Client, Listener

WINDOW_PORT = 4321


class ClientWindow:

    def __init__(self, host='localhost'):
        print('[client] Connecting to \'{}\' port {}...'.format(host, WINDOW_PORT))
        self.client = Client((host, WINDOW_PORT))

    def _send(self, *msg):
        print('[client] Sending {}()'.format(msg[0]))
        self.client.send(msg)

    def set_attend(self, visual):
        self._send('set_attend', visual)

    def set_eye(self, loc):
        self._send('set_eye', loc)

    def set_pointer(self, visual):
        self._send('set_pointer', visual)

    def set_click(self, visual):
        self._send('set_click', visual)

    def update(self, visuals):
        self._send('update', visuals)


try:

    import os
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
    import pygame

    class WindowIcon:

        def __init__(self, size):
            self.visual = None
            self.surface = pygame.Surface(size, pygame.SRCALPHA)
            self.surface.fill((255, 255, 255, 0))

        def draw(self, screen, center=True):
            if self.visual:
                sw, sh = self.surface.get_size() if center else (0, 0)
                screen.blit(self.surface,
                            (self.visual.x + (self.visual.w // 2) - (sw // 2),
                             self.visual.y + (self.visual.h // 2) - (sh // 2)))

    class AttendIcon(WindowIcon):

        def __init__(self):
            super().__init__((30, 30))
            pygame.draw.circle(self.surface,
                               (255, 255, 0, 128), (15, 15), 15)

    class EyeIcon(WindowIcon):

        def __init__(self):
            super().__init__((14, 14))
            pygame.draw.circle(self.surface,
                               (0, 0, 255, 128), (7, 7), 7)
            self.loc = None

        def draw(self, screen, center=True):
            if self.loc:
                sw, sh = self.surface.get_size() if center else (0, 0)
                screen.blit(self.surface,
                            (self.loc.x - (sw // 2),
                             self.loc.y - (sh // 2)))

    class PointerIcon(WindowIcon):

        def __init__(self):
            super().__init__((18, 17))

            def draw_pointer(x, y, color):
                pygame.draw.polygon(self.surface, color,
                                    [(x, y), (x + 10, y + 10), (x + 5, y + 9), (x + 8, y + 15),
                                     (x + 6, y + 16), (x + 3, y + 10), (x, y + 14)])

            draw_pointer(0, 0, (255, 255, 255))
            draw_pointer(2, 0, (255, 255, 255))
            draw_pointer(1, 0, (0, 0, 255))

    class ClickIcon(WindowIcon):

        def __init__(self):
            super().__init__((30, 30))

            def draw_line(sx, sy):
                pygame.draw.line(self.surface, (0, 0, 255),
                                 (15 + 5*sx, 15 + 5*sy), (15 + 15*sx, 15 + 15*sy))

            for sx in [-1, +1]:
                for sy in [-1, +1]:
                    draw_line(sx, sy)

    def get_color(color_name):
        return pygame.color.THECOLORS[color_name
                                      if color_name in pygame.color.THECOLORS else
                                      'black']

    class Window:

        def __init__(self, size=(500, 500), title='Think Window'):
            pygame.init()
            pygame.display.set_caption(title)
            self.screen = pygame.display.set_mode(size)
            self.font = pygame.font.SysFont('arial', 16)
            self.visuals = []
            self.attend = AttendIcon()
            self.eye = EyeIcon()
            self.pointer = PointerIcon()
            self.click = ClickIcon()
            self.updated = False

        def set_attend(self, visual):
            self.attend.visual = visual
            self.draw()

        def set_eye(self, loc):
            self.eye.loc = loc
            self.draw()

        def set_pointer(self, visual):
            self.pointer.visual = visual
            self.click.visual = None
            self.draw()

        def set_click(self, visual):
            self.click.visual = visual
            self.draw()

        def update(self, visuals):
            self.visuals = visuals
            self.draw()

        def draw(self):
            self.screen.fill((255, 255, 255))

            for v in self.visuals:
                if v.isa in ['text', 'letter', 'target', 'stimulus', 'button']:
                    if v.isa == 'button':
                        self.draw_rect(v, fill='gray94',
                                       stroke='darkgray', thick=1)
                    self.draw_text(v)
                elif v.isa == 'rectangle':
                    self.draw_rect(v, stroke='darkgray', thick=1)
                else:
                    self.draw_rect(v, thick=1)

            self.pointer.draw(self.screen, center=False)
            self.click.draw(self.screen)
            self.attend.draw(self.screen)
            self.eye.draw(self.screen)

            pygame.display.update()

        def draw_rect(self, visual, fill=None, stroke=None, thick=1):
            if fill or visual.has('fill'):
                pygame.draw.rect(self.screen, get_color(visual.get('fill') or fill),
                                 (visual.x, visual.y, visual.w, visual.h), 0)
            if stroke or visual.has('stroke'):
                pygame.draw.rect(self.screen, get_color(visual.get('stroke') or stroke),
                                 (visual.x, visual.y, visual.w, visual.h), thick)

        # def draw_circle(self, visual, dr=0, fill=None, stroke=None, thick=1):
        #     pygame.draw.circle(self.screen, stroke or visual_color(visual),
        #                        (visual.x + (visual.w // 2),
        #                         visual.y + (visual.h // 2)),
        #                        max(visual.w, visual.h) + dr,
        #                        thick)

        def draw_text(self, visual, text=None, color=None):
            text = text or str(visual.obj)
            if visual.has('multiline') and visual.get('multiline'):
                lines = text.strip().split('\n')
                total = len(lines)
                for i, line in enumerate(lines):
                    dy = (i - total/2) * 16
                    surface = self.font.render(
                        line, True, get_color(color or visual.get('color')))
                    rect = surface.get_rect()
                    rect.center = (visual.x + (visual.w // 2),
                                   visual.y + (visual.h // 2) + dy)
                    self.screen.blit(surface, rect)
            else:
                surface = self.font.render(
                    text, True, get_color(color or visual.get('color')))
                rect = surface.get_rect()
                rect.center = (visual.x + (visual.w // 2),
                            visual.y + (visual.h // 2))
                self.screen.blit(surface, rect)

        def reset(self):
            self.visuals = []
            self.attend.visual = None
            self.eye.loc = None
            self.pointer.visual = None
            self.click.visual = None
            self.draw()

    class ServerWindow(Window):

        def __init__(self, size=(500, 500), title='Think Window', host='localhost'):
            super().__init__(size=size, title=title)
            print('[server] Opening channel on port {}...'.format(WINDOW_PORT))
            self.listener = Listener((host, WINDOW_PORT))

        def run(self):

            def loop():
                try:
                    conn = None

                    while True:
                        print('[server] Waiting for client to connect...')
                        conn = self.listener.accept()
                        print('[server] Connected')
                        self.reset()

                        def receive():
                            try:
                                msg = conn.recv()
                                print('[server] Received {}()'.format(msg[0]))
                                return msg
                            except EOFError:
                                return None

                        msg = receive()
                        while msg:
                            if msg[0] == 'set_attend':
                                self.set_attend(msg[1])
                            elif msg[0] == 'set_pointer':
                                self.set_pointer(msg[1])
                            elif msg[0] == 'set_click':
                                self.set_click(msg[1])
                            elif msg[0] == 'update':
                                self.update(msg[1])
                            msg = receive()

                finally:
                    if conn:
                        conn.close()

            threading.Thread(target=loop).start()


except ImportError as e:

    class Window:

        def __init__(self, size=(500, 500), title='Think Window'):
            raise Exception('pygame must be installed to draw window')

    class ServerWindow(Window):

        def __init__(self, size=(500, 500), title='Think Window', host='localhost'):
            raise Exception('pygame must be installed to draw window')
