import time
import curses
import random
import asyncio 

from async_funcs import blink
from async_funcs import fire
from async_funcs import animate_spaceship
from async_funcs import run_spaceship
from async_funcs import fly_garbage
from async_funcs import fill_orbit_with_garbage
from async_funcs import count_year
from async_funcs import draw_phrases
from async_funcs import draw_year_label

from obstacles import show_obstacles

from global_vars import coroutines
from global_vars import obstacles
from global_vars import obstacles_in_last_collisions
from global_vars import SHOW_OBSTACLES

def add_stars_coros(canvas):
#def add_stars_coros(canvas):
    '''Function adds to coroutines list blinking stars coroutines.'''


    global coroutines
    y_max, x_max = canvas.getmaxyx()
    #stars should not intersect window border
    #max values decreased
    border_offset = 3
    y_max -= border_offset
    x_max -= border_offset 
    val = int(x_max*y_max/20) # define number of stars
    for i in range(val):
        row = random.randint(2,y_max)
        column = random.randint(2,x_max)
        symbol = random.choice('+:*.')
        coroutines.append(blink(canvas,row,column,symbol))
    return coroutines


def draw(canvas):


    global coroutines
    global obstacles
    global obstacles_in_last_collisions
    global year

    curses.curs_set(False) 
    canvas.nodelay(1) #will be non-blocking.

    space_ship_animate = animate_spaceship()
    space_ship_run = run_spaceship(canvas, 15, 20)
    year_control = count_year()
    year_drawing = draw_year_label(canvas)
    labels_control = draw_phrases(canvas)
    garbage_anim = fill_orbit_with_garbage(canvas)

    coroutines.append(space_ship_animate)
    coroutines.append(space_ship_run)
    coroutines.append(labels_control)
    coroutines.append(year_drawing)
    coroutines.append(year_control)
    coroutines.append(garbage_anim)
    coroutines = add_stars_coros(canvas)

    #obstacles debug
    if SHOW_OBSTACLES:
        coroutines.append(show_obstacles(canvas,obstacles))
        coroutines.append(show_obstacles(canvas,obstacles_in_last_collisions))
    #run event loop
    while True:  
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.border() 
        canvas.refresh()
        time.sleep(0.05)
        

if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)