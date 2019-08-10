import random
from physics import update_speed
from global_vars import coroutines


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258

def rnd(x1 = 15,x2 = 25):
    '''Return random int in range x1-x2.'''
    return random.randint(x1,x2)


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""
    
    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True
    
    return rows_direction, columns_direction, space_pressed

def get_ship_control(canvas,start_row, start_column,row_speed, column_speed, frame):
    """Function read keyboard and return space ship coordinates
    for space ship animation function"""


    frame_y, frame_x = get_frame_size(frame)
    #ship should not intersect window border 
    #increase frame size
    frame_offset = 1
    frame_y += frame_offset
    frame_x += frame_offset
    y_max,x_max = canvas.getmaxyx()
        
    row, column, space = read_controls(canvas) #read keyboard 
    row_speed, column_speed = update_speed(row_speed,column_speed, row, column)

    start_row += row_speed 
    start_column += column_speed 

    #check field border
    if start_row >= y_max-frame_y:
        start_row = y_max-frame_y
    elif start_row < 1:
        start_row = 1
    if start_column >= x_max-frame_x:
        start_column = x_max-frame_x
    elif start_column < 1:
        start_column = 1

    return (start_row, start_column, row_speed, column_speed, space)

def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas. Erase text instead of drawing if negative=True is specified."""
    
    
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break
                
            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculate size of multiline text fragment. Returns pair (rows number, colums number)"""
    
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns

