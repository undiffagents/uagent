import math
import threading

from .item import Area, Location
from .window import Window


class DisplayVisual(Area):

    def __init__(self, x, y, w, h, isa, obj):
        super().__init__(x, y, w, h, isa)
        self.set('seen', False)
        self.freq = None
        self.obj = obj

    def __eq__(self, visual):
        return (self.x == visual.x and self.y == visual.y
                and self.w == visual.w and self.h == visual.h
                and self.isa == visual.isa and self.obj == visual.obj)


class Display:

    def __init__(self, viewing_distance=30, pixels_per_inch=72, window=None):
        self.vision = None
        self.visuals = []
        self.viewing_distance = viewing_distance
        self.pixels_per_inch = pixels_per_inch
        self.window = window

    def set_vision(self, vision):
        self.vision = vision
        return self

    def _update_window(self):
        if self.window:
            self.window.update(self.visuals)

    def pixels_to_inches(self, pixels):
        return pixels / self.pixels_per_inch

    def pixels_to_degrees(self, pixels):
        return math.degrees(math.atan2(pixels / self.pixels_per_inch, self.viewing_distance))

    def degrees_to_pixels(self, angle):
        return self.viewing_distance * math.tan(math.radians(angle)) * self.pixels_per_inch

    def add_visual(self, visual):
        self.visuals.append(visual)
        self.vision.check_wait_for(visual)
        self._update_window()
        return visual

    def add_visuals(self, visuals):
        for visual in visuals:
            self.visuals.append(visual)
            self.vision.check_wait_for(visual)
        self._update_window()
        return visuals

    def add(self, x, y, w, h, isa, obj):
        visual = DisplayVisual(x, y, w, h, isa, obj)
        return self.add_visual(visual)

    def add_text(self, x, y, text, isa='text'):
        text = str(text)
        return self.add(x, y, len(text) * 16, 16, isa, text)

    def add_button(self, x, y, text):
        return self.add_text(x, y, text, isa='button')

    def remove_visual(self, visual):
        self.visuals.remove(visual)
        self._update_window()
        return visual

    def remove_visuals(self, visuals):
        for visual in visuals:
            self.visuals.remove(visual)
        self._update_window()
        return visuals

    def clear(self):
        self.visuals = []
        self._update_window()
        return self

    def set_attend(self, visual):
        if self.window:
            self.window.set_attend(visual)

    def set_eye(self, loc):
        if self.window:
            self.window.set_eye(loc)

    def set_pointer(self, visual):
        if self.window:
            self.window.set_pointer(visual)

    def set_click(self, visual):
        if self.window:
            self.window.set_click(visual)


class Speakers:

    def __init__(self):
        self.audition = None

    def set_audition(self, audition):
        self.audition = audition
        return self

    def add(self, isa, obj):
        return (self.audition.add_from_speakers(isa, obj)
                if self.audition else None)

    def add_speech(self, text):
        return (self.audition.add_speech(text)
                if self.audition else None)

    def clear(self):
        if self.audition:
            self.audition.clear()
        return self


class Keyboard:

    _KEY_TUPLES = [('a', False, 'a'), ('b', False, 'b'),
                   ('c', False, 'c'), ('d', False, 'd'), ('e', False, 'e'),
                   ('f', False, 'f'), ('g', False, 'g'), ('h', False, 'h'),
                   ('i', False, 'i'), ('j', False, 'j'), ('k', False, 'k'),
                   ('l', False, 'l'), ('m', False, 'm'), ('n', False, 'n'),
                   ('o', False, 'o'), ('p', False, 'p'), ('q', False, 'q'),
                   ('r', False, 'r'), ('s', False, 's'), ('t', False, 't'),
                   ('u', False, 'u'), ('v', False, 'v'), ('w', False, 'w'),
                   ('x', False, 'x'), ('y', False, 'y'), ('z', False, 'z'),
                   ('A', True, 'A'), ('B', True, 'B'), ('C', True, 'C'),
                   ('D', True, 'D'), ('E', True, 'E'), ('F', True, 'F'),
                   ('G', True, 'G'), ('H', True, 'H'), ('I', True, 'I'),
                   ('J', True, 'J'), ('K', True, 'K'), ('L', True, 'L'),
                   ('M', True, 'M'), ('N', True, 'N'), ('O', True, 'O'),
                   ('P', True, 'P'), ('Q', True, 'Q'), ('R', True, 'R'),
                   ('S', True, 'S'), ('T', True, 'T'), ('U', True, 'U'),
                   ('V', True, 'V'), ('W', True, 'W'), ('X', True, 'X'),
                   ('Y', True, 'Y'), ('Z', True, 'Z'),
                   ('`', False, 'back_quote'), ('~', True, 'tilde'),
                   ('0', False, '0'), ('1', False, '1'), ('2', False, '2'),
                   ('3', False, '3'), ('4', False, '4'), ('5', False, '5'),
                   ('6', False, '6'), ('7', False, '7'), ('8', False, '8'),
                   ('9', False, '9'), ('-', False, 'minus'),
                   ('=', False, 'equals'),
                   ('!', True, 'exclamation_mark'), ('@', True, 'at'),
                   ('#', True, 'number_sign'), ('$', True, 'dollar'),
                   ('%', True, '5'), ('^', True, 'circumflex'),
                   ('&', True, 'ampersand'), ('*', True, 'asterisk'),
                   ('(', True, 'left_parenthesis'),
                   (')', True, 'right_parenthesis'),
                   ('_', True, 'underscore'), ('+', True, 'plus'),
                   ('\t', False, 'tab'), ('\n', False, 'enter'),
                   ('[', False, 'open_bracket'),   ('{', True, 'open_brace'),
                   (']', False, 'close_bracket'), ('}', True, 'close_brace'),
                   ('\\', False, 'backslash'),   ('|', True, 'bar'),
                   (';', False, 'semicolon'), (':', True, 'colon'),
                   ('\'', False, 'apostrophe'),  ('"', True, 'quote'),
                   (',', False, 'comma'), ('<', True, 'less_than'),
                   ('.', False, 'period'),  ('>', True, 'greater_than'),
                   ('/', False, 'slash'), ('?', True, 'question_mark'),
                   (' ', False, 'space'),
                   (None, False, 'shift')]

    def __init__(self):
        self._char_to_code = {}
        self._char_to_shifted = {}
        self._code_to_char = {}
        for t in Keyboard._KEY_TUPLES:
            self._char_to_code[t[0]] = t[2]
            self._char_to_shifted[t[0]] = t[1]
            self._code_to_char[t[2]] = t[0]
        self.type_fns = []

    def code(self, c):
        return self._char_to_code[c]

    def shifted(self, c):
        return self._char_to_shifted[c]

    def char(self, code):
        return self._code_to_char[code]

    def add_type_fn(self, fn):
        self.type_fns.append(fn)
        return self

    def type(self, key):
        for fn in self.type_fns:
            fn(key)
        return self


class Mouse:

    def __init__(self, display):
        self.display = display
        self.visual = None
        self.move_fns = []
        self.click_fns = []

    def add_move_fn(self, fn):
        self.move_fns.append(fn)
        return self

    def add_click_fn(self, fn):
        self.click_fns.append(fn)
        return self

    def move(self, visual):
        self.visual = visual
        for fn in self.move_fns:
            fn(self.visual)
        return self

    def click(self, visual):
        self.visual = visual
        for fn in self.click_fns:
            fn(self.visual)
        return self


class Microphone:

    def __init__(self):
        self.receive_fns = []

    def add_receive_fn(self, fn):
        self.receive_fns.append(fn)
        return self

    def receive(self, word):
        for fn in self.receive_fns:
            fn(word)
        return self


class Environment:

    def __init__(self, window=None):
        self.display = Display(window=window)
        self.speakers = Speakers()
        self.keyboard = Keyboard()
        self.mouse = Mouse(self.display)
        self.microphone = Microphone()
