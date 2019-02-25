import math
from collections import namedtuple
from tkinter import font
import tkinter as tk

History = namedtuple('History', ['equation', 'value'])
COLUMNS = 4
ROW_OFFSET = 2

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Calculator')
        self.colors = None
        self.init_colors()
        self.root.configure(background=self.colors['whisper_gray'])
        # TODO: something else
        # currently dictionaries. maybe should be default dicts so there is a default?
        # otherwise maybe make them enums?
        self.fonts = {}
        self.styles = {}
        self._input = []
        self.value = ''
        self.displays = {}
        self.history = []

        self.init_fonts()
        self.init_styles()
        self.init_buttons()
        self.init_displays()
        self.reset_input()
        self.reset_value()
        self.update_history()

    @property
    def equation(self):       
        return ''.join(self._input)

    def click_digit(self, value):
        ''' handles clicks of buttons 0-9 '''
        # if the last input value is a number, append to the number
        if self._input and is_number(self._input[-1]):
            self._input[-1] += value
        else:
            # otherwise append it as new 
            self._input.append(value)
        # value display should represent what we're clicking
        self.value = self._input[-1]
        self.update()

    def click_operator(self, value):
        ''' handle operator (+-*/) button clicks '''
        # if there isn't input and they've hit an operator 
        # try to grab the last value from history
        if not self._input:
            self._input.append(self.history[-1].value)
        # if the last input is a number, append the operator to the list
        if is_number(self._input[-1]):
            self._input.append(value)
        # if the last value is already an operator, replace it
        else:
            self._input[-1] = value        
        self.calculate()
        self.update()

    def equals(self):
        ''' handles click on = button '''
        self.calculate()
        self.update_history()
        self.reset_input()
        self.update()

    def clear(self):
        ''' handles click on C button '''
        # reset input
        self.reset_input()
        self.reset_value()
        self.update()

    def clear_entry(self):
        ''' handles click on CE button '''
        # can't clear what isn't there
        if self._input:
            # remove last input element
            self._input.pop(-1)
        self.update()

    def backspace(self):
        ''' handles click on ⌫ button '''
        self.reset_value()
        # clear last input if it is not a number or only 1 character
        if self._input and not is_number(self._input[-1]) or len(self._input[-1]) == 1:
            self.clear_entry()
        else:
            # otherwise strip a character from the right side
            self._input[-1] = self._input[-1][:-1]
            self.value = self._input[-1]
        self.update()

    def write(self, target, value):
        ''' update target text control with value '''
        # enable editing
        target.configure(state='normal')
        # clear field
        target.delete('1.0', tk.END)
        # insert text
        target.insert(tk.END, value)
        # disable editing
        target.configure(state='disabled')

    def update_equation(self):
        ''' update equation display '''
        if len(self._input) > 1:
            equation = self.equation
        else:
            equation = ''
        self.write(self.displays['equation'], equation)

    def update_value(self):
        ''' update value display '''
        self.write(self.displays['value'], self.value)

    def update(self):
        ''' convenience method to update equation and value displays '''
        self.update_equation()
        self.update_value()

    def calculate(self):
        ''' calls the calculator engine with the current equation '''
        try:
            self.value = str(Calculator.calculate(self.equation))
        except SyntaxError:
            pass

    def update_history(self):
        ''' add new history entry '''
        history = History(self.equation, self.value)
        self.history.append(history)

    def reset_value(self):
        ''' reinitialize value '''
        self.value = '0'

    def reset_input(self):
        ''' reinitialize input '''
        self._input = []

    def init_colors(self):
        ''' initialize colors '''
        self.colors = {
            'whisper_gray': '#E6E6E6',
            'black': '#000000',
            'snow_gray': '#FAFAFA',
            'light_grey': '#D6D6D6',
            'white_smoke': '#F0F0F0',
            'white': '#FFFFFF',
            'medium_turquoise': '#28CCCC',
            'gray_swan': '#B2B2B2'
        }

    def init_fonts(self):
        ''' initialize fonts '''
        font_family = 'Arial'
        self.fonts = {
            'equation': font.Font(family=font_family, size=24),
            'operator': font.Font(family=font_family, size=24),
            'meta': font.Font(family=font_family, size=14),
            'digit': font.Font(family=font_family, size=17),
            'value': font.Font(family=font_family, size=24)
        }

    def init_styles(self):
        ''' initialize styles '''
        Style = namedtuple('Style', ['font', 'foreground', 'background', 'border', 'hover_foreground', 'hover_background'])
        self.styles = {
            'digit':Style('digit', 'black', 'snow_gray', 'black', None, 'light_grey'), 
            'operator':Style('operator', 'black', 'white_smoke', 'black', 'white', 'medium_turquoise'),
            'meta':Style('meta', 'black', 'white_smoke', 'black', None, 'light_grey')
        }

    def init_buttons(self):
        ''' initialize buttons '''
        Button = namedtuple('Button', ['name', 'text', 'replacement', 'command', 'style'])
        self.buttons = [
            Button('percent', '%', None, None, 'meta'),
            Button('square_root', '√', None, self.square_root, 'meta'),  # \u221A
            Button('square', 'x²', None, self.square, 'meta'),  # \u00B2 \U0001D712 not supported by Tcl
            Button('inverse', '1/x', None, self.inverse, 'meta'),
            Button('clear_entry', 'CE', None, self.clear_entry, 'meta'),
            Button('clear', 'C', None, self.clear, 'meta'),
            Button('backspace', '⌫', None, self.backspace, 'meta'),  # \u232B
            Button('divide', '÷', '/', None, 'operator'),  # \u00F7
            Button('seven', '7', None, None, 'digit'),
            Button('eight', '8', None, None, 'digit'),
            Button('nine', '9', None, None, 'digit'),
            Button('multiply', '×', '*', None, 'operator'),  # \u00D7
            Button('four', '4', None, None, 'digit'),
            Button('five', '5', None, None, 'digit'),
            Button('six', '6', None, None, 'digit'),
            Button('minus', '−', '-', None, 'operator'),  # \u2212
            Button('one', '1', None, None, 'digit'),
            Button('two', '2', None, None, 'digit'),
            Button('three', '3', None, None, 'digit'),
            Button('plus', '+', None, None, 'operator'),  # \u002B
            Button('plus-minus', '±', None, lambda x: -x, 'meta'),  # \u00B1
            Button('zero', '0', None, None, 'digit'),
            Button('decimal', '.', None, None, 'meta'),
            Button('equals', '=', None, self.equals, 'operator')  # \u003D
        ]

        # arrange buttons with grid manager
        for index, button in enumerate(self.buttons):
            row = index // COLUMNS + ROW_OFFSET
            column = index % COLUMNS
            self.create_button(button, row, column)

    def square_root(self):
        ''' handles √ click '''
        if self._input and is_number(self._input[-1]):
            self._input[-1] = f'math.sqrt({self._input[-1]})'

    def square(self):
        ''' handles x² click '''
        self._input[-1] = f'({self._input[-1]})**2'

    def inverse(self):
        ''' handles 1/x click '''
        self._input[-1] = f'1/({self._input[-1]})'

    def init_displays(self):
        ''' initialize displays '''
        # TODO: something different
        self.displays['value'] = self.create_text(font='value', row=0)
        self.displays['equation'] = self.create_text(font='equation', row=1)

    def create_button(self, button, row: int, column: int):
        ''' construct a tkinter button from a Button named tuple, row, and column '''
        style = self.styles[button.style]
        # if button.replacement is falsey use the button.text
        # zero button is a string '0' and will come back truthy
        button_value = button.replacement or button.text
        # for our digits, use click_digit
        if is_number(button_value):
            command = lambda: self.click_digit(button_value)
        # for everything else, use click_operator
        else:
            command = lambda: self.click_operator(button_value)
        b = HoverButton(
            self.root,
            # using get so we don't get a keyerror if it doesn't exist
            hover_foreground=self.colors.get(style.hover_foreground),
            hover_background=self.colors.get(style.hover_background),
            bg=self.colors.get(style.background),
            fg=self.colors.get(style.foreground),
            text=button.text,
            # prefer the button.command if it isn't falsey
            command=button.command or command,
            # TODO: variable?
            width=5,
            height=1,
            relief=tk.FLAT,
            # using get so we don't get a keyerror if it doesn't exist
            font=self.fonts.get(style.font))
        # place the button in the grid
        b.grid(row=row, column=column, sticky='NSEW', padx=1, pady=1)
        # nothing to return, as we don't need references to the buttons

    def create_text(self, font, row):
        ''' construct a tkinter text control given a font and it's row position '''
        text = tk.Text(
            root,
            state='disabled',
            width=1,
            height=1,
            font=self.fonts.get(font),
            padx=0,
            pady=0,
            bd=0,
            relief=tk.FLAT)
        # position displays in grid
        text.grid(
            row=row, column=0, columnspan=4, padx=0, pady=0, sticky='NSEW')
        # return the text control
        return text



def is_number(s):
    ''' Returns True if string is a number. '''
    try:
        float(s)
        return True
    except ValueError:
        return False


class HoverButton(tk.Button):
    ''' Subclassed tkinter button that changes color on hover '''
    def __init__(self,
                 parent,
                 hover_foreground=None,
                 hover_background=None,
                 *args,
                 **kwargs):
        tk.Button.__init__(self, parent, *args, **kwargs)
        # the default colors from the underlying button
        self.default_foreground = self.cget('foreground')
        self.default_background = self.cget('background')
        # the hover colors
        self.hover_foreground = hover_foreground or self.default_foreground
        self.hover_background = hover_background or self.default_background
        # bind the button's <Enter> and <Leave> events to our handlers
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_enter(self, event):
        ''' <Enter> event handler, display the hover colors '''
        self.configure(foreground=self.hover_foreground)
        self.configure(background=self.hover_background)

    def on_leave(self, event):
        ''' <Leave> event handler, reset colors to default '''
        self.configure(foreground=self.default_foreground)
        self.configure(background=self.default_background)


class Calculator:
    ''' Naive calculator engine. Uses eval() to process equation. '''
    # Not at all safe as there are no security considerations.
    # TODO: Add security considerations
    @staticmethod
    def calculate(equation: str):
        return eval(equation)


if __name__ == '__main__':
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()