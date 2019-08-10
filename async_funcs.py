import curses
import asyncio
import random 

from curses_tools import get_frame_size
from curses_tools import draw_frame
from curses_tools import get_ship_control
from curses_tools import rnd

from os import listdir
from os.path import isfile, join

from obstacles import Obstacle
from explosion import explode

from game_scenario import PHRASES
from game_scenario import get_garbage_delay_tics

from itertools import cycle

from global_vars import coroutines
from global_vars import spaceship_frame
from global_vars import obstacles
from global_vars import obstacles_in_last_collisions
from global_vars import year
from global_vars import score

async def blink(canvas, row, column, symbol='*'):
    ''' Async function for symbol blinking. '''


    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(rnd())

        canvas.addstr(row, column, symbol)
        await sleep(rnd())

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(rnd())

        canvas.addstr(row, column, symbol)
        await sleep(rnd())


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    global obstacles
    global obstacles_in_last_collisions
    global score

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
        #check fire collision with obstacles
        for obs in obstacles:
            if obs.has_collision(round(row), round(column)):
                obstacles_in_last_collisions.append(obs)
                score += 25
                return 
        row += rows_speed
        column += columns_speed


async def show_gameover(canvas):
    """Function draws gameover label after ship collision."""

        
    with open('frames/gameover.txt','r') as f:
        gameover_frame = f.read()

    #calculate label position
    y_crd, x_crd = canvas.getmaxyx()
    y_frame,x_frame = get_frame_size(gameover_frame)
    x_crd = int(x_crd/2 - x_frame/2)
    y_crd  = int(y_crd/2 - y_frame/2)
    while True:
        draw_frame(canvas, y_crd, x_crd, gameover_frame)
        await sleep()

async def run_spaceship(canvas, start_row, start_column):
    """Function provides ship control for a player."""
    
    global spaceship_frame
    global coroutintes
    global obstacles
    global year
    

    row_speed, column_speed = 0, 0
    score_counter = count_score()
    coroutines.append(score_counter)
    while True:
        #remembering current frame
        current_frame = spaceship_frame
        #get position and control data
        (start_row, start_column, 
        row_speed, column_speed, space) = get_ship_control(canvas,start_row, start_column, 
        row_speed, column_speed, spaceship_frame)
        
        #add fire if space were pressed
        if space and year >= 2020:
            coroutines.append(fire(canvas,start_row,start_column,-1,0))
            #coroutines.append(fire(canvas,start_row,start_column,-1,1))
            #coroutines.append(fire(canvas,start_row,start_column,-1,-1))

        draw_frame(canvas, start_row, start_column, current_frame)
        await sleep(1)
        draw_frame(canvas, start_row, start_column, current_frame, negative=True)
        #stop game after collision
        for obs in obstacles:
            if obs.has_collision(start_row, start_column,5,4):
                coroutines.append(show_gameover(canvas))
                coroutines.remove(score_counter)
                return 


async def animate_spaceship():
    """Function reads frames and changing it in global var spaceship_frame."""

    
    global spaceship_frame
    frames = []
    with open('frames/ship/rocket_frame_1.txt','r') as f:
        frames.append(f.read())
    with open('frames/ship/rocket_frame_2.txt','r') as f1:
        frames.append(f1.read())

    for frame in cycle(frames):
        spaceship_frame = frame
        await sleep(2)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    
    
    global obstacles
    global obstacles_in_last_collisions


    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    frame_rows, frame_columns = get_frame_size(garbage_frame)
    obs = Obstacle(row, column,frame_rows, frame_columns)
    obstacles.append(obs)

    while row < rows_number:

        draw_frame(canvas, row, column, garbage_frame)
        
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        #if obstacle in obstacles_in_last_collisions - obstacle removed, coro stops
        if obs in obstacles_in_last_collisions:
            obstacles_in_last_collisions.remove(obs)
            obstacles.remove(obs)
            await explode(canvas, row, column)
            return 
        


        row += speed
        obs.row = row
    try:
        obstacles.remove(obs)
    except ValueError:
        pass


async def fill_orbit_with_garbage(canvas):
    '''Function controlls coroutines with garbage flying.'''
    

    global coroutines
    global year

    frames = []
    y_max, x_max = canvas.getmaxyx()
    #read files with trash frames
    trash_dir = 'frames/trash_frames/'
    onlyfiles = [f for f in listdir(trash_dir) if isfile(join(trash_dir, f))]
    for fl in onlyfiles:
        with open(trash_dir+fl,'r') as f:
            frames.append(f.read())
    
    while True:
        #add random fly garbage coroutine after random sleep
        delay = get_garbage_delay_tics(year)#delay for garbage spawning
        if delay:
            coroutines.append(fly_garbage(canvas,random.randint(1,x_max), random.choice(frames)))
            await sleep(rnd(delay*1,delay*3))
        await sleep()



async def sleep(tics=1):
    """Async sleep function."""

    for _ in range(tics):
        await asyncio.sleep(0)


async def count_year():
    """Year incrementing function"""


    global year
    while True:
        year += 1
        await sleep(20)

async def count_score():
    """Score count on lifetime """
    global score

    while True:
        score += 1
        await sleep(20)

async def draw_score(canvas):
    
    
    global score
    while True:
        canvas.addstr(1,1,"Score "+str(score))
        await sleep()

async def draw_year_label(canvas):
    """Year drawing function"""
    

    global year
    #calculate year label position
    y_crd, x_crd = canvas.getmaxyx()
    x_crd = int(x_crd/2)
    y_crd -= 2
    while True:
        canvas.derwin(1,10, y_crd, x_crd)
        canvas.addstr(y_crd, x_crd, "Year "+str(year)) 
        await sleep()   

async def draw_phrases(canvas):
    """Phrases drawing function."""
    
    
    global year
    #calculate phrase position
    y_crd, x_crd = canvas.getmaxyx()
    x_crd = int(x_crd/2.2)
    phrase = ''
    while True:
        if PHRASES.get(year):
            phrase = PHRASES.get(year)

        try:
            canvas.addstr(1, x_crd, phrase)
        except TypeError:
            pass
        await sleep()


