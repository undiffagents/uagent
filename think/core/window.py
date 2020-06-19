import pickle
import socket
import struct
import sys
import threading
import time


class Messenger:
    SOCKET_PORT = 4321

    def __init__(self, name, server=False):
        self.name = name
        self.server = server
        self.sock = None

    def startup(self):
        if self.server:
            try:
                print('[server] Binding {} socket to port {}...'.format(
                    self.name, self.SOCKET_PORT))
                self.sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                self.sock.bind(('', self.SOCKET_PORT))
                self.conn = None
            except OSError as e:
                print(
                    '[server] Could not bind {} socket - port already in use'.format(self.name))
                sys.exit(1)
        else:
            try:
                print('[client] Connecting {} socket to port {}...'.format(
                    self.name, self.SOCKET_PORT))
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect(('192.168.254.71', self.SOCKET_PORT))
            except OSError as e:
                print(
                    '[client] Could not connect {} socket - is the window server running?'.format(self.name))
                sys.exit(1)
        return self

    def wait_for_client(self):
        print('[server] Waiting for client to connect...')
        self.sock.listen(1)
        self.conn, _ = self.sock.accept()
        print('[server] Connected')

    def send(self, *msg):
        print('[client] Sending {} {}()'.format(self.name, msg[0]))
        msg_bytes = pickle.dumps(msg)
        len_bytes = struct.pack('>I', len(msg_bytes))
        self.sock.sendall(len_bytes)
        self.sock.sendall(msg_bytes)

    def receive(self):
        len_bytes = self.conn.recv(4)
        if not len_bytes:
            return None
        length = struct.unpack('>I', len_bytes)[0]
        msg_bytes = self.conn.recv(length)
        msg = pickle.loads(msg_bytes)
        print('[server] Received {} {}()'.format(self.name, msg[0]))
        return msg

    def close(self):
        print('[server] Closing {} socket'.format(self.name))
        self.sock.close()


class ClientWindow:

    def __init__(self):
        self.messenger = Messenger('window').startup()

    def set_attend(self, visual):
        self.messenger.send('set_attend', visual)

    def set_pointer(self, visual):
        self.messenger.send('set_pointer', visual)

    def set_click(self, visual):
        self.messenger.send('set_click', visual)

    def update(self, visuals):
        self.messenger.send('update', visuals)


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

    def visual_color(visual):
        if visual.has('color'):
            color_name = visual.get('color')
            if color_name in pygame.color.THECOLORS:
                return pygame.color.THECOLORS[color_name]
        return (0, 0, 0)

    class Window:

        def __init__(self, size=(500, 500), title='Think Window'):
            pygame.init()
            pygame.display.set_caption(title)
            self.screen = pygame.display.set_mode(size)
            self.font = pygame.font.SysFont('arial', 16)
            self.visuals = []
            self.attend = AttendIcon()
            self.pointer = PointerIcon()
            self.click = ClickIcon()
            self.updated = False

        def set_attend(self, visual):
            self.attend.visual = visual
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
                if v.isa == 'text' or v.isa == 'letter' or v.isa == 'button':
                    self.draw_text(v)
                    if v.isa == 'button':
                        self.draw_rect(v, color=(128, 128, 128), stroke=1)
                elif v.isa == 'rectangle':
                    self.draw_rect(v, stroke=1)
                else:
                    self.draw_rect(v, stroke=1)

            self.pointer.draw(self.screen, center=False)
            self.click.draw(self.screen)
            self.attend.draw(self.screen)

            pygame.display.update()

        def draw_rect(self, visual, dw=0, dh=0, color=(0, 0, 0), stroke=1):
            pygame.draw.rect(self.screen, visual_color(visual),
                             (visual.x - (dw // 2), visual.y - (dh // 2),
                              visual.w + dw, visual.h + dh),
                             stroke)

        def draw_circle(self, visual, dr=0, color=(0, 0, 0), stroke=1):
            pygame.draw.circle(self.screen, visual_color(visual),
                               (visual.x + (visual.w // 2),
                                visual.y + (visual.h // 2)),
                               max(visual.w, visual.h) + dr,
                               stroke)

        def draw_text(self, visual, text=None):
            text = text or str(visual.obj)
            surface = self.font.render(text, True, visual_color(visual))
            rect = surface.get_rect()
            rect.center = (visual.x + (visual.w // 2),
                           visual.y + (visual.h // 2))
            self.screen.blit(surface, rect)

        def reset(self):
            self.visuals = []
            self.attend.visual = None
            self.pointer.visual = None
            self.click.visual = None
            self.draw()

    class ServerWindow(Window):

        def __init__(self, size=(500, 500)):
            super().__init__(size=size)
            self.messenger = Messenger('window', server=True).startup()

        def run(self):

            def loop():
                try:

                    while True:
                        self.messenger.wait_for_client()
                        self.reset()

                        msg = self.messenger.receive()
                        while msg:
                            if msg[0] == 'set_attend':
                                self.set_attend(msg[1])
                            elif msg[0] == 'set_pointer':
                                self.set_pointer(msg[1])
                            elif msg[0] == 'set_click':
                                self.set_click(msg[1])
                            elif msg[0] == 'update':
                                self.update(msg[1])
                            msg = self.messenger.receive()

                finally:
                    self.messenger.close()

            threading.Thread(target=loop).start()


except ImportError as e:

    class Window:

        def __init__(self, size=(500, 500)):
            raise Exception('pygame must be installed to draw display window')

    class ServerWindow(Window):

        def __init__(self, size=(500, 500)):
            raise Exception('pygame must be installed to draw display window')
