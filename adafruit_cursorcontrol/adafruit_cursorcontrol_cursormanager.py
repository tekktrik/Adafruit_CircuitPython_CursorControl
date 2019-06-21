# The MIT License (MIT)
#
# Copyright (c) 2019 Brent Rubell for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
`adafruit_cursorcontrol_cursormanager`
================================================================================
Simple interaction user interface interaction for Adafruit_CursorControl.
* Author(s): Brent Rubell
"""
import board
import digitalio
import analogio
from micropython import const
from gamepadshift import GamePadShift

# PyBadge
PYBADGE_BUTTON_LEFT = const(128)
PYBADGE_BUTTON_UP = const(64)
PYBADGE_BUTTON_DOWN = const(32)
PYBADGE_BUTTON_RIGHT = const(16)
PYBADGE_BUTTON_A = const(2)
PYBADGE_BUTTON_B = const(1)
PYBADGE_BUTTON_SEL = const(8)
PYBADGE_BUTTON_START = const(4)

class CursorManager:
    """Simple interaction user interface interaction for Adafruit_CursorControl.

    :param adafruit_cursorcontrol cursor: The cursor object we are using.
    :param adafruit_button.Button buttons: Optional array of button elements.
    """
    def __init__(self, cursor, buttons=None):
        self._cursor = cursor
        self._btns = buttons
        self._is_held = False
        self._init_hardware()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.deinit()

    def deinit(self):
        """Deinitializes a CursorManager object."""
        self._is_deinited()
        self._pad.deinit()
        self._cursor_deinit()
        self._cursor = None

    def _is_deinited(self):
        """Checks if CursorManager object has been deinitd."""
        if self._cursor is None:
            raise ValueError("CursorManager object has been deinitialized and can no longer "
                             "be used. Create a new CursorManager object.")

    def _init_hardware(self):
        """Initializes PyBadge or PyGamer hardware."""
        if hasattr(board, 'BUTTON_CLOCK') and not hasattr(board, 'SD_CS'):
            self._pad_btns = {'btn_left' : PYBADGE_BUTTON_LEFT,
                                'btn_right' : PYBADGE_BUTTON_RIGHT,
                                'btn_up' : PYBADGE_BUTTON_UP,
                                'btn_down' : PYBADGE_BUTTON_DOWN,
                                'btn_a' : PYBADGE_BUTTON_SEL,
                                'btn_b' : PYBADGE_BUTTON_START}
        elif hasattr(board, 'JOYSTICK_X'):
            self._joystick_x = analogio.AnalogIn(board.JOYSTICK_X)
            self._joystick_y = analogio.AnalogIn(board.JOYSTICK_Y)
            self._pad_btns = {'btn_a' : PYBADGE_BUTTON_SEL,
                                'btn_b' : PYBADGE_BUTTON_START}
        else:
            raise AttributeError('Board must have a D-Pad or Joystick for use with CursorManager!')
        self._pad = GamePadShift(digitalio.DigitalInOut(board.BUTTON_CLOCK),
                                    digitalio.DigitalInOut(board.BUTTON_OUT),
                                    digitalio.DigitalInOut(board.BUTTON_LATCH))

    def update(self):
        """Handles physical interaction, cursor movement, and cursor interaction"""
        pressed = self._pad.get_pressed()
        self._check_cursor_movement(pressed)
        if self._btns: # button elements exist in user-code
            btn_clicked = self._check_cursor_click(pressed)
        

    def _check_cursor_click(self, pressed):
        """Returns which display button element has been clicked as an integer."""
        if pressed & self._pad_btns['btn_a']:
            for i, b in enumerate(self._btns):
                if b.contains((self._cursor.x, self._cursor.y)):
                    return b

    def _check_cursor_movement(self, pressed=None):
        """Checks the PyBadge D-Pad or the PyGamer's Joystick for movement.
        :param int pressed: 8-bit number with bits that correspond to buttons
            which have been pressed down since the last call to get_pressed().
        """
        if self._pad_btns['btn_up']:
            if pressed & self._pad_btns['btn_right']:
                self._cursor.x += self._cursor.speed
            elif pressed & self._pad_btns['btn_left']:
                self._cursor.x -= self._cursor.speed
            if pressed & self._pad_btns['btn_up']:
                self._cursor.y -= self._cursor.speed
            elif pressed & self._pad_btns['btn_down']:
                self._cursor.y += self._cursor.speed
        else:
            self._cursor.x = self._joystick_x
            self._cursor.y = self._joystick_y
