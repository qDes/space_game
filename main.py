import time
import curses
import random

from async_funcs import blink
from async_funcs import fire
from async_funcs import animate_spaceship

def add_stars_coros(canvas, coroutines):
    '''Function adds to coroutines list blinking stars coroutines.'''


    y_max, x_max = canvas.getmaxyx()
    #stars should not intersect window border
    #max values decreased
    border_offset = 2
    y_max -= border_offset
    x_max -= border_offset 
    val = int(x_max*y_max/20) # define number of stars
    for i in range(val):
        row = random.randint(1,y_max)
        column = random.randint(1,x_max)
        symbol = random.choice('+:*.')
        coroutines.append(blink(canvas,row,column,symbol))
    return coroutines


def draw(canvas):


    curses.curs_set(False) 
    canvas.nodelay(1) #will be non-blocking.
    canvas.border() 
    
    #add fire animation 
    fire_animation = fire(canvas,20,20,-1,1)
    #add space ship animation
    y_max, x_max = canvas.getmaxyx()
    space_ship = animate_spaceship(canvas, 15, 20)

    coroutines = []
    coroutines.append(fire_animation)
    coroutines.append(space_ship)
    coroutines = add_stars_coros(canvas, coroutines)

    #run event loop
    while True:  
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        
        canvas.refresh()
        time.sleep(0.05)
        


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)