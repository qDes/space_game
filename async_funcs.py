import curses
import asyncio

from curses_tools import get_frame_size
from curses_tools import draw_frame
from curses_tools import get_ship_postition
from curses_tools import rnd


async def blink(canvas, row, column, symbol='*'):
    ''' async function for symbol blinking '''
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for i in range(rnd()):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(rnd()):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for i in range(rnd()):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(rnd()):
            await asyncio.sleep(0)

async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed

async def animate_spaceship(canvas, start_row, start_column):
    """Async func for space ship animation."""


    frames = []
    with open('frames/rocket_frame_1.txt','r') as f:
        frames.append(f.read())
    with open('frames/rocket_frame_2.txt','r') as f1:
        frames.append(f1.read())

    while True:
        start_row, start_column = get_ship_postition(canvas,start_row, start_column,frames)
        #animate ship
        for frame in frames:
            draw_frame(canvas, start_row, start_column,frame)
            await asyncio.sleep(0)
            draw_frame(canvas, start_row, start_column,frame,negative=True)

        
async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed